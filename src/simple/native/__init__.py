# simple/native/__init__.py
"""
Dynamic loader for native security enforcers.

Discovery rules:
 - Files in this package matching "<keyword>_harden.py" are considered enforcers.
 - Each such module must define exactly one class that subclasses SecurityEnforcerBase.
 - The returned dict maps keyword -> enforcer instance.
 - If a "ssh_harden.py" module exists, its enforcer is instantiated first and injected
   into context as 'ssh_enforcer' for dependency injection.
"""

from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import inspect

PACKAGE_PATH = Path(__file__).parent
BASE_CLASS_PATH = "simple.core.os_hardening.SecurityEnforcerBase"

def _discover_harden_files() -> Dict[str, Path]:
    files: Dict[str, Path] = {}
    for child in PACKAGE_PATH.iterdir():
        if not child.is_file():
            continue
        name = child.name
        if name.endswith('_harden.py') and not name.startswith('__'):
            keyword = name[:-len('_harden.py')]
            files[keyword] = child
    return files

def _load_enforcer_class_from_path(path: Path) -> Tuple[Optional[type], Optional[str]]:
    """
    Import module from path and return the single class that subclasses SecurityEnforcerBase.
    Returns (class_obj, error) where error is None on success, else a string.
    """
    try:
        spec = spec_from_file_location(f"simple.native.{path.stem}", str(path))
        if spec is None:
            return None, "spec_missing"
        mod = module_from_spec(spec)
        loader = spec.loader
        assert loader is not None
        loader.exec_module(mod)
    except Exception as e:
        return None, f"import_error: {e}"

    # import the base class dynamically to avoid circular imports
    try:
        base_spec = spec_from_file_location("simple.core.os_hardening",
                                           str(Path(__file__).parents[1] / "core" / "os_hardening.py"))
        base_mod = module_from_spec(base_spec)
        base_loader = base_spec.loader
        assert base_loader is not None
        base_loader.exec_module(base_mod)
        SecurityEnforcerBase = getattr(base_mod, "SecurityEnforcerBase")
    except Exception:
        # fallback: try importing by usual import (may raise)
        try:
            from simple.core.os_hardening import SecurityEnforcerBase  # type: ignore
        except Exception as e:
            return None, f"base_import_error: {e}"

    # Find classes in module that subclass SecurityEnforcerBase and are defined in the module
    subclasses = []
    for _, member in inspect.getmembers(mod, inspect.isclass):
        if member.__module__ != mod.__name__:
            continue
        try:
            if issubclass(member, SecurityEnforcerBase) and member is not SecurityEnforcerBase:
                subclasses.append(member)
        except TypeError:
            # not a class type that can be checked with issubclass
            continue

    if len(subclasses) == 0:
        return None, "no_subclass_found"
    if len(subclasses) > 1:
        # Explicit assertion as requested
        raise AssertionError(f"Module {path.name} defines multiple SecurityEnforcerBase subclasses ({[c.__name__ for c in subclasses]})")
    return subclasses[0], None

def load_enforcers(context: Dict[str, Any]) -> Dict[str, object]:
    """
    Instantiate available enforcers discovered in this package.

    Returns a dict: { keyword: instance }.
    """
    enforcers: Dict[str, object] = {}
    files = _discover_harden_files()

    # Ensure ssh is instantiated first if present
    ordered_keys = sorted(files.keys())
    if 'ssh' in files:
        ordered_keys.remove('ssh')
        ordered_keys.insert(0, 'ssh')

    for key in ordered_keys:
        path = files[key]
        try:
            cls, err = _load_enforcer_class_from_path(path)
        except AssertionError:
            # Re-raise AssertionError to notify caller about misconfigured module
            raise
        if cls is None:
            # skip on import/class discovery error
            continue
        try:
            instance = cls(context)
            enforcers[key] = instance
            # inject ssh enforcer for DI
            if key == 'ssh':
                context['ssh_enforcer'] = instance
        except Exception:
            # skip instantiation errors
            continue

    return enforcers

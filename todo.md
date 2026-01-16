1. create the compose file at the last 
2. ask for service selection -> ask for alternatives -> ask for the values for parameters userd in alternative tempaltes mapped to prompts[*].name with prompts[*].description in the about.yaml. 
move to next serice selection. if the variable for the prompt from alternative is repeatative, show auto populated value where user can simply press enter and continue, or change he value.
3. fix this issue
📋 SECURITY SERVICES
========================================

📦 CrowdSec
     Open-source security automation platform
? Enable CrowdSec? No
Traceback (most recent call last):
  File "/home/shadow-gust/.local/share/uv/python/cpython-3.14.0-linux-x86_64-gnu/lib/python3.14/runpy.py", line 198, in _run_module_as_main
    return _run_code(code, main_globals, None,
                     "__main__", mod_spec)
  File "/home/shadow-gust/.local/share/uv/python/cpython-3.14.0-linux-x86_64-gnu/lib/python3.14/runpy.py", line 88, in _run_code
    exec(code, run_globals)
    ~~~~^^^^^^^^^^^^^^^^^^^
  File "/home/shadow-gust/.var/app/com.vscodium.codium/data/codium/extensions/ms-python.debugpy-2025.18.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/__main__.py", line 71, in <module>
    cli.main()
    ~~~~~~~~^^
  File "/home/shadow-gust/.var/app/com.vscodium.codium/data/codium/extensions/ms-python.debugpy-2025.18.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/../debugpy/server/cli.py", line 508, in main
    run()
    ~~~^^
  File "/home/shadow-gust/.var/app/com.vscodium.codium/data/codium/extensions/ms-python.debugpy-2025.18.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/../debugpy/server/cli.py", line 358, in run_file
    runpy.run_path(target, run_name="__main__")
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/shadow-gust/.var/app/com.vscodium.codium/data/codium/extensions/ms-python.debugpy-2025.18.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py", line 310, in run_path
    return _run_module_code(code, init_globals, run_name, pkg_name=pkg_name, script_name=fname)
  File "/home/shadow-gust/.var/app/com.vscodium.codium/data/codium/extensions/ms-python.debugpy-2025.18.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py", line 127, in _run_module_code
    _run_code(code, mod_globals, init_globals, mod_name, mod_spec, pkg_name, script_name)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/shadow-gust/.var/app/com.vscodium.codium/data/codium/extensions/ms-python.debugpy-2025.18.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py", line 118, in _run_code
    exec(code, run_globals)
    ~~~~^^^^^^^^^^^^^^^^^^^
  File "/mnt/Storage/Projects/SIMPLE/src/main.py", line 204, in <module>
    main()
    ~~~~^^
  File "/mnt/Storage/Projects/SIMPLE/src/main.py", line 157, in main
    engine.generate()
    ~~~~~~~~~~~~~~~^^
  File "/mnt/Storage/Projects/SIMPLE/src/simple/engine.py", line 347, in generate
    self._write_compose_file()
    ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/mnt/Storage/Projects/SIMPLE/src/simple/engine.py", line 504, in _write_compose_file
    service_yaml = yaml.safe_load(service_yaml_str)
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/__init__.py", line 125, in safe_load
    return load(stream, SafeLoader)
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/__init__.py", line 81, in load
    return loader.get_single_data()
           ~~~~~~~~~~~~~~~~~~~~~~^^
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/constructor.py", line 49, in get_single_data
    node = self.get_single_node()
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/composer.py", line 36, in get_single_node
    document = self.compose_document()
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/composer.py", line 55, in compose_document
    node = self.compose_node(None, None)
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/composer.py", line 84, in compose_node
    node = self.compose_mapping_node(anchor)
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/composer.py", line 133, in compose_mapping_node
    item_value = self.compose_node(node, item_key)
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/composer.py", line 84, in compose_node
    node = self.compose_mapping_node(anchor)
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/composer.py", line 133, in compose_mapping_node
    item_value = self.compose_node(node, item_key)
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/composer.py", line 84, in compose_node
    node = self.compose_mapping_node(anchor)
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/composer.py", line 133, in compose_mapping_node
    item_value = self.compose_node(node, item_key)
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/yaml/composer.py", line 68, in compose_node
    raise ComposerError(None, None, "found undefined alias %r"
            % anchor, event.start_mark)
yaml.composer.ComposerError: found undefined alias 'vault-app-defaults'
  in "<unicode string>", line 13, column 9:
        <<: *vault-app-defaults
            ^


4. [X] remove hardcoded fieldsfrom engine, make it dynamic based on the selected service alternative and the parametere defined in the corresponding yaml file
5. pre check the .github/workflow/ci.yaml linting enforcement before push to the git, can it be a pre hook?
6. one file one class rule adharance, specially in services/unified service, abstract dhould move to core.
7. logically rename file names and package names.
8. add logging framework instead on print statements. add debug, warn , info statements
9. convert the existing pring for ux to a standardised display module, which will have the parameter based prompts. (needs idea)
10. move rules/workflows/skills to global scope in a new repo. add a workflow to trigger everything systamatically.
11. create a cli for creating the templates, may be a project specific skill?
12. enforce git message format

21. make cline smart
22. convert core of cline to python
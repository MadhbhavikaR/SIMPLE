1. [x] create the compose file at the last 
2. [X] ask for service selection -> ask for alternatives -> ask for the values for parameters userd in alternative tempaltes mapped to prompts[*].name with prompts[*].description in the about.yaml. 
move to next serice selection. if the variable for the prompt from alternative is repeatative, show auto populated value where user can simply press enter and continue, or change he value.


4. [X] remove hardcoded fieldsfrom engine, make it dynamic based on the selected service alternative and the parametere defined in the corresponding yaml file
5. pre check the .github/workflow/ci.yaml linting enforcement before push to the git, can it be a pre hook?
6. [X] one file one class rule adharance, specially in services/unified service, abstract dhould move to core.
7. logically rename file names and package names.
8. [x] add logging framework instead on print statements. add debug, warn , info statements
9. convert the existing pring for ux to a standardised display module, which will have the parameter based prompts. (needs idea)
10. move rules/workflows/skills to global scope in a new repo. add a workflow to trigger everything systamatically.
11. create a cli for creating the templates, may be a project specific skill?
12. enforce git message format

21. make cline smart
22. convert core of cline to python


fix this 

📋 AUTH SERVICES
========================================

📦 Authelia
     Open-source high-performance authentication & authorization server
? Enable Authelia? Yes
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
  File "/mnt/Storage/Projects/SIMPLE/src/main.py", line 154, in main
    engine.select_services(allow_incremental=False)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/Storage/Projects/SIMPLE/src/simple/engine.py", line 217, in select_services
    self._handle_service_with_alternatives(service, about_data, is_enforced=False)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/Storage/Projects/SIMPLE/src/simple/engine.py", line 284, in _handle_service_with_alternatives
    selected_alternative = questionary.select(
                           ~~~~~~~~~~~~~~~~~~^
        f"Select configuration alternative for {service_name}:",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        choices=choices,
        ^^^^^^^^^^^^^^^^
        default=choices[0]['value']
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ).ask()
    ^
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/questionary/prompts/select.py", line 165, in select
    ic = InquirerControl(
        choices,
    ...<7 lines>...
        initial_choice=default,
    )
  File "/mnt/Storage/Projects/SIMPLE/.venv/lib/python3.14/site-packages/questionary/prompts/common.py", line 284, in __init__
    raise ValueError(
    ...<3 lines>...
    )
ValueError: Invalid `default` value passed. The value (`default`) does not exist in the set of choices. Please make sure the default value is one of the available choices.


this is the earlier code that seemed to work, pls check the logic again

 def _handle_service_with_alternatives(self, service: ServiceStrategy,
                                         about_data: Dict[str, Any],
                                         is_enforced: bool = False) -> None:
        """
        Handle service selection with alternative configuration options.
        
        Args:
            service: ServiceStrategy instance
            about_data: Service metadata from about.yaml
            is_enforced: Whether this service is enforced/auto-enabled
        """
        service_name = about_data.get('name', service.name)
        
        # Check if the service supports alternatives (unified service approach)
        if hasattr(service, 'get_available_alternatives'):
            alternatives = service.get_available_alternatives()
            
            if len(alternatives) > 1:
                # Multiple alternatives available - let user choose
                choices = [
                    {
                        'name': f"{alt['name']}: {alt['description']}",
                        'value': alt['name']
                    }
                    for alt in alternatives
                ]
                
                if is_enforced:
                    print(f"✅ {service_name} (AUTO-ENABLED)")
                    if about_data.get('description'):
                        print(f"     {about_data['description']}")

                    # For enforced services, ask which alternative to use
                    if choices:
                        selected_alternative = questionary.select(
                            f"Select configuration alternative for {service_name}:",
                            choices=choices
                        ).ask()
                    else:
                        raise ValueError(f"No alternatives available for enforced service {service_name}")
                else:
                    # For optional services, ask which alternative to use
                    if choices:
                        selected_alternative = questionary.select(
                            f"Select configuration alternative for {service_name}:",
                            choices=choices,
                            default=choices[0]['value']
                        ).ask()
                    else:
                        selected_alternative = questionary.select(
                            f"Select configuration alternative for {service_name}:",
                            choices=choices
                        ).ask()
                
                # Set the selected alternative
                service.set_alternative(selected_alternative)
            elif len(alternatives) == 1:
                # Only one alternative (default) - use it automatically
                if is_enforced:
                    print(f"✅ {service_name} (AUTO-ENABLED)")
                    if about_data.get('description'):
                        print(f"     {about_data['description']}")
                else:
                    print(f"✅ {service_name} enabled with default configuration")

                # Use the single available alternative
                service.set_alternative(alternatives[0]['name'])
            else:
                # No valid alternatives - this shouldn't happen due to sanity checks
                print(f"⚠️  {service_name} has no valid alternatives, using default")
        else:
            # Legacy service - handle as before
            if is_enforced:
                self.selected_services.append(service)
                print(f"✅ {service_name} (AUTO-ENABLED)")
                if about_data.get('description'):
                    print(f"     {about_data['description']}")
            else:
                self.selected_services.append(service)

                # Use dynamic prompt scanning based on selected alternative
                if hasattr(service, 'get_required_prompts_for_alternative'):
                    prompts = service.get_required_prompts_for_alternative()
                else:
                    prompts = about_data.get('prompts', [])

                for prompt in prompts:
                    prompt_value = self._get_prompt_input(prompt)
                    # Store prompt values in secrets or context as appropriate
                    prompt_type_str = prompt.get('type', {}).get('enum', ['STRING'])[0]
                    if prompt_type_str in ['PASSWORD', 'SECRET']:
                        self.secrets[prompt['name']] = prompt_value
                    else:
                        self.context[prompt['name']] = prompt_value

                # Collect any additional secrets not covered by prompts
                self._collect_secrets(service, about_data)
        
        # Add to selected services if not already there
        if service not in self.selected_services:
            self.selected_services.append(service)
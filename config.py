DEBUG = True


# TODO: Add tests, general refactor the code and add documentation.
def debug_print(module_name, input_str):
    if DEBUG:
        print(f"DEBUG - {module_name}")
        print("--------------------------------------")
        print(input_str)
        print("--------------------------------------\n")

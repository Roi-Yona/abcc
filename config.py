import pandas as pd
DEBUG = True

pd.set_option('display.max_rows', None)  # None means unlimited rows
pd.set_option('display.max_columns', None)  # None means unlimited columns

# Glasgow Dataset Consts
DISTRICTS_NUMBER_OF_CANDIDATES = {1: 9, 2: 11, 3: 10, 4: 11}
DISTRICTS_NUMBER_OF_VOTERS = {1: 6900, 2: 10376, 3: 5199, 4: 8624}
NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT = {1: 1,
                                           2: 1,
                                           3: 1,
                                           4: 1}
NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT_3 = {1: 3,
                                             2: 3,
                                             3: 3,
                                             4: 3}


def debug_print(module_name, input_str):
    if DEBUG:
        print(f"DEBUG - {module_name}")
        print("--------------------------------------")
        print(input_str)
        print("--------------------------------------\n")

import pandas as pd

DEBUG = True

pd.set_option('display.max_rows', None)  # None means unlimited rows
pd.set_option('display.max_columns', None)  # None means unlimited columns

# Glasgow Dataset Consts
DISTRICTS_NUMBER_OF_CANDIDATES = {1: 9, 2: 11, 3: 10, 4: 11, 5: 10, 6: 10, 7: 13, 8: 10, 9: 11, 10: 9, 11: 10, 12: 8,
                                  13: 11, 14: 8, 15: 9, 16: 10, 17: 9, 18: 9, 19: 11, 20: 9, 21: 10}
DISTRICTS_NUMBER_OF_VOTERS = {1: 6900, 2: 10376, 3: 5199, 4: 8624, 5: 11052, 6: 8680, 7: 9078, 8: 70160, 9: 9650,
                              10: 8682, 11: 8984, 12: 9334, 13: 9567, 14: 9901, 15: 8654, 16: 8363, 17: 12744, 18: 9567,
                              19: 8803, 20: 8783, 21: 5410}

NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT = dict()
NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT_3 = dict()

for i in range(1, 22):
    NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT[i] = 1
    NUMBER_OF_CANDIDATES_FROM_EACH_DISTRICT_3[i] = 3


def debug_print(module_name, input_str):
    if DEBUG:
        print(f"DEBUG - {module_name}")
        print("--------------------------------------")
        print(input_str)
        print("--------------------------------------\n")

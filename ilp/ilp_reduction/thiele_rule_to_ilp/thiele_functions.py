"""
A utility functions for creating a
thiele rule function in a form of a dict.
"""


def create_av_thiele_dict(length: int) -> dict:
    """Creates a dict from size of length contain the AV thiele function.
    :param length: The length of the returned AV thiele function dict.
    :return: An AV thiele function dict.
    """
    av_thiele_function = {}
    for i in range(0, length):
        av_thiele_function[i] = i
    return av_thiele_function


def create_cc_thiele_dict(length: int) -> dict:
    """Creates a dict from size of length contain the CC thiele function.
    :param length: The length of the returned CC thiele function dict.
    :return: A CC thiele function dict.
    """
    cc_thiele_function = {}
    if length > 0:
        cc_thiele_function[0] = 0
    for i in range(1, length):
        cc_thiele_function[i] = 1
    return cc_thiele_function


if __name__ == '__main__':
    # Sanity hand tests.
    print(create_av_thiele_dict(4))
    print(create_cc_thiele_dict(4))

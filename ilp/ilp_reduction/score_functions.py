"""
A utility functions for creating a
thiele rule functions (and SAV scoring rule function).
"""


def av_thiele_function(v_approval_number: int, v_approval_profile_size: int) -> float:
    """AV thiele function.
    :param v_approval_number: The size of the intersection between the chosen committee and voter 'v' approval profile.
    :param v_approval_profile_size: Voter 'v' approval profile size.
    :return: The score, calculated base on AV.
    """
    return v_approval_number


def cc_thiele_function(v_approval_number: int, v_approval_profile_size: int) -> float:
    """CC thiele function.
    :param v_approval_number: The size of the intersection between the chosen committee and voter 'v' approval profile.
    :param v_approval_profile_size: Voter 'v' approval profile size.
    :return: The score, calculated base on CC.
    """
    if v_approval_number == 0:
        return 0
    else:
        return 1


def pav_thiele_function(v_approval_number: int, v_approval_profile_size: int) -> float:
    """PAV thiele function.
    :param v_approval_number: The size of the intersection between the chosen committee and voter 'v' approval profile.
    :param v_approval_profile_size: Voter 'v' approval profile size.
    :return: The score, calculated base on PAV.
    """
    score = 0
    for i in range(1, v_approval_number + 1):
        score += (1 / i)
    return score


def k_truncated_av_thiele_function(v_approval_number: int, v_approval_profile_size: int, k: int) -> float:
    """K-Truncated AV thiele function.
    :param v_approval_number: The size of the intersection between the chosen committee and voter 'v' approval profile.
    :param v_approval_profile_size: Voter 'v' approval profile size.
    :param k: The point where the function becomes const.
    :return: The score, calculated base on K-Truncated AV function.
    """
    if v_approval_number < k:
        return av_thiele_function(v_approval_number, v_approval_profile_size)
    else:
        return av_thiele_function(k, v_approval_profile_size)


def k_2_truncated_av_thiele_function(v_approval_number: int, v_approval_profile_size: int) -> float:
    """2-Truncated AV thiele function.
    :param v_approval_number: The size of the intersection between the chosen committee and voter 'v' approval profile.
    :param v_approval_profile_size: Voter 'v' approval profile size.
    :return: The score, calculated base on 2-Truncated AV function.
    """
    return k_truncated_av_thiele_function(v_approval_number, v_approval_profile_size, 2)


def sav_score_rule_function(v_approval_number: int, v_approval_profile_size: int) -> float:
    """The score rule function SAV - Satisfaction Approval Voting.
    :param v_approval_number: The size of the intersection between the chosen committee and voter 'v' approval profile.
    :param v_approval_profile_size: Voter 'v' approval profile size.
    :return: The score, calculated base on SAV.
    """
    return v_approval_number/v_approval_profile_size


if __name__ == '__main__':
    # Sanity tests.
    print(av_thiele_function(4, 10))
    print(cc_thiele_function(100, 10))
    print(pav_thiele_function(3, 10))
    print(k_2_truncated_av_thiele_function(10, 10))
    print(sav_score_rule_function(2, 3))

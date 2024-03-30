import os

DATABASE_PATH = os.path.join('..', 'databases')
# The first number of approved candidate in the ranked-choice ballot will consider as approved
# candidates of the voter.
NUMBER_OF_APPROVED_CANDIDATE = 1


def soi_to_csv(soi_file_path: str, new_csv_file_path: str, candidate_starting_index=0, voter_starting_index=0):
    approval_rate = 5
    csv_rows = [['voter_id', 'candidate_id', 'rating']]
    current_voter_id = voter_starting_index
    with open(soi_file_path) as soi_file:
        for line in soi_file:
            # Parse data.
            line = line.split(':')
            # The number of voter with this voter profile.
            number_of_voters = int(line[0])
            candidate_ids = line[1].split(',')
            for _ in range(number_of_voters):
                current_voter_id += 1
                # In the original elections the election setting was STV, where there is a  ranked-choice ballot.
                # Because we convert the problem to an ABC, we need to convert the ranked ballot to an approval
                # profile, we do so by taking only the first candidate in the ballot.
                for candidate_id in candidate_ids[:NUMBER_OF_APPROVED_CANDIDATE]:
                    current_row = [current_voter_id,
                                   int(candidate_id) + candidate_starting_index,
                                   approval_rate]
                    csv_rows.append(current_row)
    print(csv_rows)
    # Write data to the CSV file
    write_data_to_csv(new_csv_file_path, csv_rows)


def write_data_to_csv(file_path: str, data: list):
    """Write data to the CSV file.
    :param file_path: The input file path.
    :param data: list of list, each list is a csv row including the columns names.
    :return:
    """
    with open(file_path, 'w') as csv_file:
        for row in data:
            csv_file.write(','.join(map(str, row)) + '\n')


if __name__ == '__main__':
    starting_points_dict = dict()
    starting_points_dict[1] = (9, 6900)
    starting_points_dict[2] = (11, 10376)
    starting_points_dict[3] = (10, 5199)
    starting_points_dict[4] = (11, 8624)

    candidates_starting_point = 0
    voters_starting_point = 0

    for i in range(1, 5):
        _soi_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-0000000{i}.soi.txt')
        _new_csv_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-0000000{i}_pre.csv')
        soi_to_csv(_soi_file_path, _new_csv_file_path, candidates_starting_point, voters_starting_point)

    for i in range(1, 5):
        _soi_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-0000000{i}.soi.txt')
        _new_csv_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-0000000{i}.csv')
        soi_to_csv(_soi_file_path, _new_csv_file_path, candidates_starting_point, voters_starting_point)
        voters_starting_point += starting_points_dict[i][1]
        candidates_starting_point += starting_points_dict[i][0]

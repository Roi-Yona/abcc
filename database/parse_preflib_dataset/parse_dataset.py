import os
import config

import pandas as pd

DATABASE_PATH = os.path.join('..', 'databases')
# The first number of approved candidate in the ranked-choice ballot will consider as approved
# candidates of the voter.
NUMBER_OF_APPROVED_CANDIDATE = 3


def write_data_to_csv(file_path: str, data: list):
    """Write data to the CSV file.
    :param file_path: The input file path.
    :param data: list of list, each list is a csv row including the columns names.
    :return:
    """
    with open(file_path, 'w') as csv_file:
        for row in data:
            csv_file.write(','.join(map(str, row)) + '\n')


def soi_to_csv_voting(soi_file_path: str, new_csv_file_path: str, candidate_starting_index=0, voter_starting_index=0):
    approval_rate = 5
    csv_rows = [['voter_id', 'candidate_id', 'rating']]
    current_voter_id = voter_starting_index
    with open(soi_file_path) as soi_file:
        for line in soi_file:
            # Parse data.
            line = line.split(':')
            # The number of voter with this voter profile.
            if not line[0].isdigit():
                continue
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


def soi_to_csv_candidates(soi_file_path: str, new_csv_file_path: str, candidate_starting_index=0):
    csv_rows = [['candidate_id', 'candidate_name']]
    current_candidate_id = candidate_starting_index
    with open(soi_file_path) as soi_file:
        for line in soi_file:
            # Parse data.
            line = line.split(':')
            # The number of voter with this voter profile.
            if not line[0][0:18] == "# ALTERNATIVE NAME":
                continue
            current_candidate_id += 1
            current_row = [current_candidate_id,
                           line[1][1:][:-1]]
            csv_rows.append(current_row)
    print(csv_rows)
    # Write data to the CSV file
    write_data_to_csv(new_csv_file_path, csv_rows)


def dat_to_csv_voting(dat_file_path: str, new_csv_file_path: str):
    # Reading the dat file in csv format.
    df = pd.read_csv(dat_file_path)

    # Removing irrelevant columns.
    columns_to_keep = ['User ID', 'Hotel ID', 'Overall Rating']
    df = df[columns_to_keep]

    # Rename the columns.
    new_column_names = {
        'User ID': 'voter_id',
        'Hotel ID': 'candidate_id',
        'Overall Rating': 'rating'
    }
    df.rename(columns=new_column_names, inplace=True)

    # Write data to the CSV file
    df.to_csv(new_csv_file_path, index=False)


def trip_advisor_dat_to_csv_candidates(dat_file_path: str, new_csv_file_path: str):
    # Reading the dat file in csv format.
    df = pd.read_csv(dat_file_path)

    # Removing irrelevant columns.
    columns_to_keep = ['Hotel ID', 'Price', 'Location']
    df = df[columns_to_keep]

    # Rename the columns.
    new_column_names = {
        'Hotel ID': 'candidate_id',
        'Price': 'price',
        'Location': 'location'
    }
    df.rename(columns=new_column_names, inplace=True)

    # TODO: Add a range of prices, and flag for each range.

    # Write data to the CSV file
    df.to_csv(new_csv_file_path, index=False)


def glasgow_data_main():
    candidates_starting_point = 0
    voters_starting_point = 0

    for i in range(1, 22):
        t = str(i)
        if i < 10:
            t = '0' + t
        _soi_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'data\\00008-000000{t}.soi')
        _new_csv_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-000000{t}_pre.csv')
        _new_csv_file_path_c = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-000000{t}'
                                                                                             f'_pre_candidates.csv')
        soi_to_csv_voting(_soi_file_path, _new_csv_file_path, candidates_starting_point, voters_starting_point)
        soi_to_csv_candidates(_soi_file_path, _new_csv_file_path_c)

    for i in range(1, 22):
        t = str(i)
        if i < 10:
            t = '0' + t
        _soi_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'data\\00008-000000{t}.soi')
        _new_csv_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-000000{t}.csv')
        _new_csv_file_path_c = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-000000{t}'
                                                                                             f'_candidates.csv')
        soi_to_csv_voting(_soi_file_path, _new_csv_file_path, candidates_starting_point, voters_starting_point)
        soi_to_csv_candidates(_soi_file_path, _new_csv_file_path_c, candidates_starting_point)
        voters_starting_point += config.DISTRICTS_NUMBER_OF_VOTERS[i]
        candidates_starting_point += config.DISTRICTS_NUMBER_OF_CANDIDATES[i]


def trip_advisor_data_main():
    dat_to_csv_voting(os.path.join(DATABASE_PATH, 'the_trip_advisor_database', f'00040-00000001.dat'),
                      os.path.join(DATABASE_PATH, 'the_trip_advisor_database', f'voting_table.csv'))
    trip_advisor_dat_to_csv_candidates(
        os.path.join(DATABASE_PATH, 'the_trip_advisor_database', f'00040-00000001.dat'),
        os.path.join(DATABASE_PATH, 'the_trip_advisor_database', f'candidates_table.csv'))


if __name__ == '__main__':
    trip_advisor_data_main()

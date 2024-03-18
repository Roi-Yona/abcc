import os

DATABASE_PATH = os.path.join('..', 'databases')


def soi_to_csv(soi_file_path: str, new_csv_file_path: str):
    approval_rate = 5
    csv_rows = [['voter_id', 'candidate_id', 'rating']]

    with open(soi_file_path) as soi_file:
        for line in soi_file:
            # Parse data.
            line = line.split(':')
            voter_id = int(line[0])
            candidate_ids = line[1].split(',')
            for candidate_id in candidate_ids:
                current_row = [voter_id, int(candidate_id), approval_rate]
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
    for i in range(1, 5):
        _soi_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-0000000{i}.soi.txt')
        _new_csv_file_path = os.path.join(DATABASE_PATH, 'glasgow_city_council_elections', f'00008-0000000{i}.csv')
        soi_to_csv(_soi_file_path, _new_csv_file_path)

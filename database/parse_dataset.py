"""This module is for parsing and cleaning the given datasets,
to prepare the data before creating a proper database.
Therefore, should be used before the create database script.
"""
import os
import numpy as np
import pandas as pd
import ast

import config

MODULE_NAME = "Parse Dataset"


def clean_movie_dataset_metadata(original_csv_file_path: str, new_csv_file_path: str):
    # Load the CSV file into a DataFrame.
    # Note: This line should generate a DtypeWarning because it is before cleaning, hence there are invalid lines.
    df = pd.read_csv(original_csv_file_path)

    # Filter out invalid rows.
    valid_rows = df[df['id'].apply(str.isdigit)].copy()

    # Convert the 'id' column to integers.
    valid_rows['id'] = valid_rows['id'].astype(int)

    # Rename id column.
    valid_rows.rename(columns={'id': config.CANDIDATES_COLUMN_NAME}, inplace=True)

    # Remove duplicates.
    valid_rows = valid_rows[valid_rows.duplicated(subset=['candidate_id'], keep=False) is False]

    # Save the cleaned DataFrame back to a CSV file.
    valid_rows.to_csv(new_csv_file_path, index=False)


def unpack_list_with_dictionary_column(original_csv_file_path: str, new_csv_file_path: str,
                                       column_name: str, new_column_name: str):
    # An example for the genres column value:
    # [{'id': 16, 'name': 'Animation'}, {'id': 35, 'name': 'Comedy'}, {'id': 10751, 'name': 'Family'}]
    # An example for the spoken languages column value:
    # [{'iso_639_1': 'en', 'name': 'English'}, {'iso_639_1': 'fr', 'name': 'FranÃ§ais'}]

    # Load the CSV file into a DataFrame.
    df = pd.read_csv(original_csv_file_path)

    # Drop rows where the requested column is empty.
    df = df.dropna(subset=[column_name])

    # Parse the required column as a dict (parsed as a string by default).
    df[column_name] = df[column_name].apply(ast.literal_eval)

    # Create a new column with the names list as a value.
    df[new_column_name] = df[column_name].apply(
        lambda current_row_dict_list: [current_dict['name'] for current_dict in current_row_dict_list])

    # Keep only the relevant columns.
    df = df[['candidate_id', new_column_name]]

    # Explode the new_column column to create a separate row for each genre.
    df_exploded = df.explode(new_column_name)

    # Drop rows where the new column is empty.
    df_exploded = df_exploded.dropna(subset=[new_column_name])
    df_exploded = df_exploded[df_exploded[new_column_name] != '']

    # Save the cleaned DataFrame to the new CSV file.
    df_exploded.to_csv(new_csv_file_path, index=False)


def create_movie_genre_metadata(original_csv_file_path: str, new_csv_file_path: str):
    unpack_list_with_dictionary_column(original_csv_file_path, new_csv_file_path, 'genres', 'genre')


def create_movie_spoken_languages_metadata(original_csv_file_path: str, new_csv_file_path: str):
    unpack_list_with_dictionary_column(original_csv_file_path, new_csv_file_path, 'spoken_languages', 'spoken_language')
    # Load the CSV file into a DataFrame.
    df = pd.read_csv(new_csv_file_path)

    df['spoken_language'] = df['spoken_language'].replace('Français', 'French')
    df['spoken_language'] = df['spoken_language'].replace('Español', 'Spanish')
    df['spoken_language'] = df['spoken_language'].replace('Italiano', 'Italian')
    df['spoken_language'] = df['spoken_language'].replace('Deutsch', 'German')

    # Save the updated DataFrame to the CSV file.
    df.to_csv(new_csv_file_path, index=False)


def create_movie_original_language_metadata(original_csv_file_path: str, new_csv_file_path: str):
    # Load the CSV file into a DataFrame.
    df = pd.read_csv(original_csv_file_path)

    # Save the updated DataFrame to the CSV file.
    df.to_csv(new_csv_file_path, index=False)

    # Load the CSV file into a DataFrame.
    df = pd.read_csv(original_csv_file_path)

    # Drop rows where the requested column is empty.
    df = df.dropna(subset=['original_language'])
    df = df[df['original_language'] != '']

    # Keep only the relevant columns.
    df = df[['candidate_id', 'original_language']]

    # Save the cleaned DataFrame to the new CSV file.
    df.to_csv(new_csv_file_path, index=False)


def create_movie_runtime_metadata(original_csv_file_path: str, new_csv_file_path: str):
    # Reading the dat file in csv format.
    df = pd.read_csv(original_csv_file_path)

    # Removing irrelevant columns.
    columns_to_keep = ['candidate_id', 'runtime']
    df = df[columns_to_keep]

    # Drop duplicate rows.
    df = df.drop_duplicates()

    # Find the median.
    median_value = df['runtime'].quantile(0.5)
    config.debug_print(MODULE_NAME, f"The Movies dataset - median: {median_value}")

    # Create a function to categorize values based on quantiles.
    def categorize_value(value, median):
        if value <= median:
            return 'short'
        else:
            return 'long'

    # Add 'price_range' column based on quantiles.
    df['runtime'] = df['runtime'].apply(lambda x: categorize_value(x, median_value))

    # Write data to the CSV file
    df.to_csv(new_csv_file_path, index=False)


def clean_movie_dataset_rating(original_csv_file_path: str, new_csv_file_path: str):
    # Load the CSV file into a DataFrame.
    # Note: This line should generate a DtypeWarning because it is before cleaning, hence there are invalid lines.
    df = pd.read_csv(original_csv_file_path)

    # Rename id column.
    df.rename(columns={'userId': config.VOTERS_COLUMN_NAME,
                       'movieId': config.CANDIDATES_COLUMN_NAME}, inplace=True)

    # Save the cleaned DataFrame back to a CSV file.
    df.to_csv(new_csv_file_path, index=False)


def soi_to_csv_voting(soi_file_path: str, new_csv_file_path: str, candidate_starting_index=0, voter_starting_index=0):
    approval_rate = 5
    csv_rows = [[config.VOTERS_COLUMN_NAME, config.CANDIDATES_COLUMN_NAME, config.APPROVAL_COLUMN_NAME]]
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
                # profile, we do so by taking only the first NUMBER_OF_APPROVED_CANDIDATE candidates in the ballot.
                for candidate_id in candidate_ids[:config.NUMBER_OF_APPROVED_CANDIDATE]:
                    current_row = [current_voter_id,
                                   int(candidate_id) + candidate_starting_index,
                                   approval_rate]
                    csv_rows.append(current_row)

    df = pd.DataFrame(csv_rows[1:], columns=csv_rows[0])
    df.to_csv(new_csv_file_path, index=False)


def soi_to_csv_candidates(soi_file_path: str, new_csv_file_path: str, candidate_starting_index=0):
    csv_rows = [[config.CANDIDATES_COLUMN_NAME, 'candidate_name']]
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

    df = pd.DataFrame(csv_rows[1:], columns=csv_rows[0])
    df.to_csv(new_csv_file_path, index=False)


def clean_trip_advisor_dat_file(dat_file_path: str, new_csv_file_path: str):
    with open(dat_file_path, "r", encoding="utf-8") as file:
        # Read the first line (and skip the headline).
        new_file_content = file.readline() + '\n'
        line = file.readline()

        # Continue reading until the end of the file.
        while line:
            list_line = line.split(',')

            if list_line[2] == '1':
                # If the price is equal to 1, remove this part of the line.
                list_line = list_line[:2] + list_line[3:]
            if list_line[2] == 'nkonwn' or list_line[2] == 'id="hotel_505846">' or list_line[2] == 'id="hotel_579210">' \
                    or list_line[2] == 'id="hotel_674915">':
                list_line[2] = '-1'

            new_line = ','.join(list_line)
            new_file_content += new_line + '\n'

            # Read the next line.
            line = file.readline()

    # Open the file in write mode.
    with open(new_csv_file_path, "w", encoding="utf-8") as file:
        # Write a string to the file
        file.write(new_file_content)

    # Read the new dat file as dataframe.
    df = pd.read_csv(new_csv_file_path)

    # Filter the DataFrame to include rows where column 'User ID' matches values in the valid voters list.
    valid_voters_list = get_trip_advisor_dataset_valid_voters_list(new_csv_file_path)
    df = df[df['User ID'].isin(valid_voters_list)]

    # Enumerate the user ID to int instead of string.
    user_names = df['User ID'].unique()
    user_name_to_id = {name: idx for idx, name in enumerate(user_names, start=1)}

    # Replace the usernames in the DataFrame with their corresponding ID numbers.
    df['User ID'] = df['User ID'].map(user_name_to_id)

    df.to_csv(new_csv_file_path, index=False)


def trip_advisor_dat_to_csv_voting(dat_file_path: str, new_csv_file_path: str):
    # Reading the dat file in csv format.
    df = pd.read_csv(dat_file_path)

    # Removing irrelevant columns.
    columns_to_keep = ['User ID', 'Hotel ID', 'Overall Rating']
    df = df[columns_to_keep]

    # Rename the columns.
    new_column_names = {
        'User ID': config.VOTERS_COLUMN_NAME,
        'Hotel ID': config.CANDIDATES_COLUMN_NAME,
        'Overall Rating': config.APPROVAL_COLUMN_NAME
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
        'Hotel ID': config.CANDIDATES_COLUMN_NAME,
        'Price': 'price',
        'Location': 'location'
    }
    df.rename(columns=new_column_names, inplace=True)

    # Drop duplicate rows
    df = df.drop_duplicates()

    # Find the one-third and two-third values
    one_third_value = df['price'].quantile(0.333)
    two_third_value = df['price'].quantile(0.667)

    config.debug_print(MODULE_NAME, f"Trip Advisor dataset - one-third price value: {one_third_value}")
    config.debug_print(MODULE_NAME, f"Trip Advisor dataset - two-third price value: {two_third_value}")

    # Create a function to categorize values based on quantiles.
    def categorize_value(value, one_third, two_third):
        if value <= one_third:
            return 'low'
        elif value <= two_third:
            return 'medium'
        else:
            return 'high'

    # Add 'price_range' column based on quantiles.
    df['price_range'] = df['price'].apply(lambda x: categorize_value(x, one_third_value, two_third_value))

    # Write data to the CSV file
    df.to_csv(new_csv_file_path, index=False)


def trip_advisor_locations_csv(candidates_table_path: str, new_locations_table_path: str):
    candidates_df = pd.read_csv(candidates_table_path)
    # Filter to only the location column.
    locations_df = candidates_df[['location']]
    # Remove the value 'Unknown'.
    locations_df = locations_df[locations_df['location'] != 'Unknown']
    # Drop duplicates, sort the column, and reset indices.
    locations_df = locations_df.drop_duplicates().sort_values(by='location').reset_index(drop=True)

    # Save the clean table of locations into a csv.
    locations_df.to_csv(new_locations_table_path, index=False)


def print_trip_advisor_dataset_frequency_of_voters(dataset_path: str):
    # Read the CSV file and extract the column.
    original_df = pd.read_csv(dataset_path)
    column_data = original_df['User ID']

    # Counting occurrences of unique values (of User ID, i.e. how many times a user voted).
    value_counts = column_data.value_counts().reset_index()
    value_counts.columns = ['User ID', 'count']

    # Counting the occurrences of voters with X number of votes.
    value_counts = np.bincount(value_counts['count'].values)

    # Printing the histogram in text format
    print("----------------")
    for value, count in enumerate(value_counts):
        if count > 0:
            print(f"Number of reviews:{value}\t\tFrequency:{count}\t\t:Percentage:{100 * (count / len(column_data))}%")
    print(f"Total number of reviews: {len(column_data)}")
    print("----------------")


def get_trip_advisor_dataset_valid_voters_list(dataset_path: str):
    # Read the CSV file and extract the column
    original_df = pd.read_csv(dataset_path)
    column_data = original_df['User ID']

    # Counting occurrences of unique values (of User UD, i.e. how many times a user voted).
    value_counts = column_data.value_counts().reset_index()
    value_counts.columns = ['User ID', 'count']

    # Screen out the anonymous voters (with a very large votes count, and the users that voted only ones).
    value_counts = value_counts[value_counts['count'] > 1]
    value_counts = value_counts[value_counts['count'] < 10000]

    # Sanity print.
    print(value_counts.head())
    print(value_counts.tail())

    return value_counts['User ID'].tolist()


def print_best_hotels_by_av(dataset_path: str):
    original_df = pd.read_csv(dataset_path)
    # Filter the DataFrame to include only ratings above approval threshold.
    filtered_df = original_df[original_df['Overall Rating'] > config.APPROVAL_THRESHOLD].copy()
    un_voted_hotels = original_df[original_df['Overall Rating'] <= config.APPROVAL_THRESHOLD].copy()
    un_voted_hotels = un_voted_hotels['Hotel ID'].drop_duplicates().reset_index()
    un_voted_hotels['count'] = 0
    un_voted_hotels = un_voted_hotels.drop('index', axis=1)

    # Count the number of ratings above threshold for each item.
    rating_counts = filtered_df['Hotel ID'].value_counts().reset_index()
    rating_counts.columns = ['Hotel ID', 'count']

    # Sort the items by the count of ratings.
    sorted_items = rating_counts.sort_values(by='count', ascending=False)

    # Concatenate DataFrames column-wise
    result_col_wise = pd.concat([sorted_items, un_voted_hotels])

    # Print the sorted items list.
    print("\nSorted items list by the number of ratings above threshold:")
    print(result_col_wise.head())


def the_movies_dataset_main():
    config.create_folder_if_not_exists(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME)
    clean_movie_dataset_metadata(
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.ORIGINAL_DATA_FOLDER_NAME, f'movies_metadata.csv'),
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'movies_metadata_new.csv'))
    clean_movie_dataset_rating(
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.ORIGINAL_DATA_FOLDER_NAME, f'ratings.csv'),
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'ratings_new.csv'))
    create_movie_genre_metadata(
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'movies_metadata_new.csv'),
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'movies_genres.csv'))
    create_movie_spoken_languages_metadata(
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'movies_metadata_new.csv'),
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'movies_spoken_languages.csv'))
    create_movie_runtime_metadata(
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'movies_metadata_new.csv'),
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'movies_runtime.csv'))
    create_movie_original_language_metadata(
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'movies_metadata_new.csv'),
        os.path.join(config.MOVIES_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME,
                     f'movies_original_language.csv'))


def glasgow_dataset_main():
    config.create_folder_if_not_exists(config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME)
    candidates_starting_point = 0
    voters_starting_point = 0

    for i in range(1, 22):
        t = str(i)
        if i < 10:
            t = '0' + t
        _soi_file_path = os.path.join(config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH, config.ORIGINAL_DATA_FOLDER_NAME,
                                      f'00008-000000{t}.soi')
        _new_csv_file_path = os.path.join(config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME,
                                          f'00008-000000{t}_pre.csv')
        _new_csv_file_path_c = os.path.join(config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH,
                                            config.PARSED_DATA_FOLDER_NAME,
                                            f'00008-000000{t}_pre_candidates.csv')
        soi_to_csv_voting(_soi_file_path, _new_csv_file_path, candidates_starting_point, voters_starting_point)
        soi_to_csv_candidates(_soi_file_path, _new_csv_file_path_c)

    for i in range(1, 22):
        t = str(i)
        if i < 10:
            t = '0' + t
        _soi_file_path = os.path.join(config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH, config.ORIGINAL_DATA_FOLDER_NAME,
                                      f'00008-000000{t}.soi')
        _new_csv_file_path = os.path.join(config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME,
                                          f'00008-000000{t}.csv')
        _new_csv_file_path_c = os.path.join(config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH,
                                            config.PARSED_DATA_FOLDER_NAME,
                                            f'00008-000000{t}_candidates.csv')
        soi_to_csv_voting(_soi_file_path, _new_csv_file_path, candidates_starting_point, voters_starting_point)
        soi_to_csv_candidates(_soi_file_path, _new_csv_file_path_c, candidates_starting_point)
        voters_starting_point += config.GLASGOW_DISTRICTS_NUMBER_OF_VOTERS[i]
        candidates_starting_point += config.GLASGOW_DISTRICTS_NUMBER_OF_CANDIDATES[i]


def glasgow_dataset_analyze_district(district_number: int):
    soi_file_path = os.path.join(config.GLASGOW_ELECTIONS_DATASET_FOLDER_PATH, config.ORIGINAL_DATA_FOLDER_NAME,
                                 f'00008-0000000{district_number}.soi')

    # Number of candidates that is larger than all districts number of candidates.
    max_number_of_candidates = 20
    total_count_of_voters = 0

    # Init histogram.
    histogram = dict()
    for i in range(max_number_of_candidates + 1):
        histogram[i] = 0

    with open(soi_file_path) as soi_file:
        for line in soi_file:
            # Parse data.
            line = line.split(':')
            # The number of voter with this voter profile.
            if not line[0].isdigit():
                continue
            number_of_voters = int(line[0])
            candidate_ids = line[1].split(',')
            for candidate_id in candidate_ids[:1]:
                histogram[int(candidate_id)] += number_of_voters
            total_count_of_voters += number_of_voters

    print(
        f"Histogram of district {district_number} (when taking in account approval threshold to be first choice - 1).")
    print("The keys are candidates, and values are the number of votes the candidate got.")
    print(histogram)
    print(f"The total number of voters is: {total_count_of_voters}.")
    print(f"The total number of votes is: {sum([i for j, i in histogram.items()])}.")


def glasgow_dataset_analyze():
    glasgow_dataset_analyze_district(1)


def trip_advisor_dataset_main():
    config.create_folder_if_not_exists(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME)
    clean_trip_advisor_dat_file(
        os.path.join(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.ORIGINAL_DATA_FOLDER_NAME, f'00040-00000001.dat'),
        os.path.join(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME,
                     f'00040-00000001_new.dat'))

    trip_advisor_dat_to_csv_voting(
        os.path.join(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME,
                     f'00040-00000001_new.dat'),
        os.path.join(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'voting_table.csv'))
    trip_advisor_dat_to_csv_candidates(
        os.path.join(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME,
                     f'00040-00000001_new.dat'),
        os.path.join(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'candidates_table.csv'))
    trip_advisor_locations_csv(
        os.path.join(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'candidates_table.csv'),
        os.path.join(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME, f'locations_table.csv'))


def trip_advisor_dataset_analyze():
    new_dat_file_path = os.path.join(config.TRIP_ADVISOR_DATASET_FOLDER_PATH, config.PARSED_DATA_FOLDER_NAME,
                                     f'00040-00000001_new.dat')
    print_trip_advisor_dataset_frequency_of_voters(new_dat_file_path)
    print_best_hotels_by_av(new_dat_file_path)


if __name__ == '__main__':
    the_movies_dataset_main()
    trip_advisor_dataset_main()
    glasgow_dataset_main()
    # trip_advisor_dataset_analyze()
    # glasgow_dataset_analyze()

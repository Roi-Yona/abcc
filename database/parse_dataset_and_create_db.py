"""In this script we use a configured path for the datasets directories.

"""
import argparse

import config
import create_database
import parse_dataset


def parse_arguments():
    # Create the parser.
    parser = argparse.ArgumentParser(
        description="This script parse the datasets of glasgow city council elections (2007), "
                    "kaggle's movies dataset and trip advisor, and given the parsed data - "
                    "creates sqlite databases for the experiments usage.")

    # Add arguments.
    parser.add_argument("--kaggle_movies_dataset", "-m", action="store_true",
                        help="Parse Kaggle Movies dataset, and create a proper DB.")
    parser.add_argument("--glasgow_elections_dataset", "-g", action="store_true",
                        help="Parse Glasgow Elections (2007) dataset, and create a proper DB")
    parser.add_argument("--trip_advisor_dataset", "-t", action="store_true",
                        help="Parse Trip Advisor dataset, and create a proper DB")
    parser.add_argument("--no_parse_dataset", action="store_true",
                        help="When specified, the datasets will not be parsed (only creating the DB skipping the "
                             "parsing stage, relaying on previous parsed data).")
    parser.add_argument("--create_tests_db", action="store_true",
                        help="When specified, ignore all other tasks and create the tests db.")

    # Parse the arguments.
    return parser.parse_args()


def main():
    args = parse_arguments()
    config.create_folder_if_not_exists(config.DATABASES_FOLDER_PATH, config.DATABASES_DIRECTORY_NAME)
    print(f"Starting parsing datasets and creating DBs...")

    if args.create_tests_db:
        print("Creating movies tests DB.")
        create_database.create_tests_db_main()
    else:
        if args.kaggle_movies_dataset:
            if not args.no_parse_dataset:
                print("Parsing Kaggle Movies dataset.")
                parse_dataset.the_movies_dataset_main()
            print("Creating Kaggle Movies dataset DB.")
            create_database.the_movies_database_create_database_main()
        if args.glasgow_elections_dataset:
            if not args.no_parse_dataset:
                print("Parsing Glasgow Elections dataset.")
                parse_dataset.glasgow_dataset_main()
            print("Creating Glasgow Elections dataset DB.")
            create_database.glasgow_create_database_main()
        if args.trip_advisor_dataset:
            if not args.no_parse_dataset:
                print("Parsing Trip Advisor dataset.")
                parse_dataset.trip_advisor_dataset_main()
            print("Creating Trip Advisor dataset DB.")
            create_database.trip_advisor_create_database_main()
    print(f"Done parsing datasets and creating DBs.")


if __name__ == '__main__':
    main()

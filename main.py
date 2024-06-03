import pandas as pd
import numpy as np
import os

DATABASE_PATH = os.path.join("database", "databases", "the_movies_database")


def main():
    df = pd.read_csv(os.path.join(DATABASE_PATH, 'ratings.csv'))
    print(df.head())


main()

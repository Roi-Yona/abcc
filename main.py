import pandas as pd
import numpy as np
import pathlib

DATABASE_PATH = "database\\databases\\the_movies_database\\"


def main():
    df = pd.read_csv(pathlib.Path(DATABASE_PATH + 'ratings.csv'))
    print(df.head())


main()

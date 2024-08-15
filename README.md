# Approval-Based Committee Voting in the Presence of Constraints

A new framework that extends ABC voting with a database context.
In this work we study approval-based committee voting in the presence of external constraints expressed as database
dependencies over a relational database with information about the candidates.
In order to solve this new problem we build an appropriate MIP program.

### Datasets

In our existing experiments we use datasets of three different domains, and in order to use them you should download the
datasets, and refer to the next chapter to see how to add it to the project and create a database properly.
The used datasets are:

* The Glasgow City Council Election Dataset. This dataset is taken from Preflib at
  https://preflib.simonrey.fr/dataset/00008 and donated by Jeffery O’Neill. Open STV. www.OpenSTV.org, 2013.
* The Trip Advisor Dataset. This dataset is taken from Preflib at https://preflib.simonrey.fr/dataset/00040 and was
  scraped and denoted by Hongning Wang, first introduced in (Wang, Lu, and Zhai 2010).
* The Movies Dataset. This dataset is taken from Kaggle
  at https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset/data, the dataset is an ensemble of data
  collected from TMDB and GroupLens.

### How to add new database?

All datasets should locate under:
```database/databases/datasets_data/<new_dataset_folder>```
All ```.db``` sqlite databases should locate under:
```database/databases/sqlite_databases/<database_name>```

After adding the datasets to the project properly, you should run ```parse_dataset``` python script.
A parsing for the three datasets describe above is already implemented.
Any new datasets should have a proper parsing implementation.
After parsing the data, you should run ```create_database``` python script, to create a new ```.db``` sqlite file given
an appropriate csv files that describes the relations. The three databases above creation is
already implemented and any new datasets should have a proper creation implementation.

In our work, we show several examples of handling soi, dat, and csv datasets cleaning and preparation, and exports a
general functionality to handle similar cases.

### How to run an experiment?

This project requires python3, sqlite3, ortools (and any additional solver you want to define for the ortools wrapper,
we found Gurobi to work well on this problem).
The experiments are located under:
```ilp/experiments/<dataset_name>/<experiment_number>/<experiment_file>```
To run an experiment can simply run the python file.

Note that ```config.py``` holds important settings for your experiment, such as DEBUG mode.
The current experiments of the three database described above, assume that you place a copy of your ```.db``` file in
your experiment folder, (because in order to run experiments in parallel you should access to different db files).
Therefore, you should copy your db file to your experiment folder. This can be easily changed to point to a
shared db file by using a full path to the db (instead the use of ```config.MOVIES_DATABASE_DB_NAME``` in the Movies
Dataset experiments use ```config.MOVIES_DATABASE_DB_PATH``` for example). The result of this experiments can be found
under ```ilp/experiments/<dataset_name>/results```.

### How to define a new experiment?

Experiment is defined by a database, ABC settings and external constraints.
You can define constraints of the form of TGD and DC, and there a lot of examples in this repo for three different
databases. It is recommended to check the documentation of ```config.py``` and ```combined_constraints_experiments.py```
for further information.

### How to add a new score function?

Under ```ilp/ilp_reduction/score_functions``` you can define a new function with the appropriate interface of score
function, that returns the voter committee score contribution, and use it in your experiment.

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

Furthermore, for the Glasgow Elections dataset, we have our own additional csv ('00008-00000000_candidates') containing 
the combined candidates list from all district with context (such as the candidate party association) that we have
collected from the internet.


### How to add new database?

All datasets should locate under:
```database/data/datasets/<new_dataset_folder>/original_data```
All ```.db``` sqlite databases should locate under:
```database/databases/sqlite_databases/<database_name>```

After adding the datasets to the project properly, you should run ```parse_dataset_and_create_db``` python script.
Parsing, cleaning and creating for the three datasets describe above is already implemented.
Any new datasets should have a proper parsing implementation.

In our work, we show several examples of handling soi, dat, and csv datasets cleaning and preparation, and exports a
general functionality to handle similar cases.

### How to run an experiment?

This project requires python3, sqlite3, ortools (and any additional solver you want to define for the ortools wrapper,
we found Gurobi to work well on this problem).
The experiments are located under:
```mip/experiments/<dataset_name>/<experiment_number>/<experiment_file>```
To run an experiment can simply run the python file.

Note that ```config.py``` holds important settings for your experiment, such as DEBUG mode.
Note thay when running the experiment, a copy from the database directory of the ```.db``` file will be created in your 
experiment directory, in order to enable parallel running.
The result of this experiments can be found under ```mip/experiments/<dataset_name>/results```.

### How to define a new experiment?

Experiment is defined by a database, ABC settings and external constraints.
You can define constraints of the form of TGD and DC, and there a lot of examples in this repo for three different
databases. It is recommended to check the documentation of ```config.py``` and ```combined_constraints_experiments.py```
for further information.

### How to add a new score function?

Under ```mip/mip_reduction/score_functions``` you can define a new function with the appropriate interface of score
function, that returns the voter committee score contribution, and use it in your experiment.

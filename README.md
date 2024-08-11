# Approval-Based Committee Voting in the Presence of Constraints
A new framework that extends ABC voting with a database context.
In this work we study approval-based committee voting in the presence of external constraints expressed as database 
dependencies over a relational database with information about the candidates.
In order to solve this new problem we build an appropriate MIP program.

### How to run an experiment?
This project requires python3, sqlite3, ortools (and any additional solver you want to define for the ortools wrapper, 
we found Gurobi to work well on this problem).
The experiments are located under:
```ilp/experiments/<dataset_name>/<experiment_number>/<experiment_file>```
To run an experiment can simply run the python file.
Note that ```config.py``` holds important settings for your experiment, such as DEBUG mode.
Important Note: The value of ```config.MOVIES_DATABASE_DB_NAME``` should be the path for your database, the current value
assume that you place a copy of your .db file in your experiment folder, this is because in order to run experiments in 
parallel you should access to different db files. Therefor, you should either copy your db file to your experiment folder, 
or change the value of this constant to be the path to your shared db.
The result of this experiments can be found in ```ilp/experiments/<dataset_name>/results```.

### How to define a new experiment?
Experiment is defined by a database, ABC settings and external constraints.
You can define constraints of the form of TGD and DC, and there a lot of examples in this repo for three different databases.
It is recommended to check the documentation of ```config.py``` and ```combined_constraints_experiments.py``` for further information.

### How to add new database?
All datasets should locate under:
```database/databases/datasets_data/<new_dataset_folder>```
All ```.db``` sqlite databases should locate under:
```database/databases/sqlite_databases/<database_name>```

In the module ```create_database``` we show several examples of building a new ```.db``` sqlite file given an appropriate csv files 
that describes the relations.
Furthermore, we show several examples of handling soi, dat, and csv datasets cleaning and preparation, and exports a 
general functionality to handle similar cases.

### How to add a new score function?
Under ```ilp_reduction```, you can simply define a new function with the appropriate interface of score function, that 
returns the voter committee score contribution, and use it in your experiment.

# Approval-Based Committee Voting in the Presence of Constraints

A new framework that extends ABC voting with a database context.
In this work we study approval-based committee voting in the presence of external constraints expressed as database
dependencies over a relational database with information about the candidates.
In order to solve this new problem we build an appropriate MIP program.

## Setting Up the Python Environment
This project is built using python 3.8. If trying to run on a newer version, consider that some dependencies here may need to be changed.
For your convenience, we've created a `requirements.txt` file, so you can use it to set a virtual environment for running the UI and all scripts in this project.

First, find out your python's path using the terminal:

Linux/macOS:
```shell
which python3.8
```
Windows:
```shell
where python3.8
```
Then, you can just simply enter in your terminal (under the project's root directory): 
Linux/macOS:
```shell
C:\path\to\python3.8 -m venv ABCV-venv
source ABCV-venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Windows:
```shell
C:\path\to\python3.8 -m venv ABCV-venv
ABCV-venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Datasets

In our existing experiments we use datasets of three different domains, and in order to use them you should download the
datasets, and refer to the next chapter to see how to add it to the project and create a database properly.
The used datasets are:

* The Glasgow City Council Election Dataset. This dataset is taken from Preflib at
  https://preflib.github.io/PrefLib-Jekyll/dataset/00008 and donated by Jeffery O’Neill. Open STV. www.OpenSTV.org, 2013.
* The Trip Advisor Dataset. This dataset is taken from Preflib at https://preflib.github.io/PrefLib-Jekyll/dataset/00040 and was
  scraped and denoted by Hongning Wang, first introduced in (Wang, Lu, and Zhai 2010).
* The Movies Dataset. This dataset is taken from Kaggle
  at https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset/data, the dataset is an ensemble of data
  collected from TMDB and GroupLens.

Furthermore, for the Glasgow Elections dataset, we have our own additional csv (already in this repo - '00008-00000000_candidates') containing 
the combined candidates list from all district with context (such as the candidate party association) that we have
collected from the internet.

After downloading the relevant db files, you should place them in the appropriate directory (check for the folder path constants in ```config.py```) and run the ```parse_dataset_and_create_db.py``` script - for detailed instructions please read [our instructions on how to add new databases](#How-to-add-a-new-database)
## Running the Front End (Experiments Sandbox GUI)

We've implemented a GUI using Streamlit, for a convenient experiment running framework.
In order to run the application, you simply need to create the project's environment (with all package requirements), and run the following command in the root path of this repository:

```shell
  streamlit run streamlit_main.py
```

You can find an instructional video on using this system here **insert link to demo video**

## Extending the Repo
Below we describe how you can add your own data and run your own experiments, using this codebase.

### How to add a new database?

All datasets should be located under:
```database/data/datasets/<new_dataset_folder>/original_data```

All ```.db``` sqlite databases should be located under:
```database/databases/sqlite_databases/<database_name>```

The ```<new_dataset_folder>``` and the ```<database_name>```, along with further specific configuration constants, 
should be defined in the ```config.py``` file 
(the preexisting ones are already defined, and can be viewed for reference). 

Notice that in order for the code to run on your new database, it must satisfy the following requirements (all datasets described earlier already satisfy these):

1. Have a relation called "candidates", containing information about the committee candidates, with a column called "candidate_id"
2. Have a relation called "voters", containing information about all votes regarding the committee, containing the columns "voter_id", "candidate_id" and "rating", which represent the voter, that candidate he rated, and the rating he gave him (on a scale of 1-5), respectively.
3. Have a relation called "candidates_summary", containing all information you want to be present when viewing your selected committee (must contain a "candidate_id" column of course)

Finally, in order to enable adding new datasets in the main script, you must add the new db flag to the argument-parser in ```parse_dataset_and_create_db.py```, 
and add proper parsing and creation functions to the ```parse_dataset.py``` and ```create_database.py``` files, respectively.
It is well recommended to go over the existing DB parsing and creation methods and make sure that your new methods follow the same logic (with the
specific needed adjustments for your new tables and relations, of course).

After adding the datasets to the project properly, you should run the ```parse_dataset_and_create_db``` python script.
As previously mentioned - parsing, cleaning and transformation of the three datasets described above is already implemented.
Any new dataset should have its own parsing and creation implementation.

In our work, we show several examples of handling ```.soi```, ```.dat```, and ```.csv``` datasets cleaning and preparation, and export a
general functionality to handle similar cases.

### How to run an experiment (with a script)?

This project requires python3, sqlite3, ortools (and any additional solver you want to define for the ortools wrapper,
we found Gurobi to work well on this problem, the default solver defined in ```config.py``` is SAT).
The experiments are located under:
```mip/experiments/<dataset_name>/<experiment_number>/<experiment_file>```
To run an experiment can simply run the python file.

Note that ```config.py``` holds important settings for your experiment, such as DEBUG mode.
Note that when running the experiment, a copy from the database directory of the ```.db``` file will be created in your 
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

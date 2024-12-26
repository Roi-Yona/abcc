import os
import time
from datetime import datetime
import pandas as pd

import config
from database import database_server_interface as db_interface
import mip.mip_reduction.mip_convertor as mip_convertor
import mip.mip_reduction.abc_to_mip_convertor as abc_to_mip_convertor
from mip.mip_db_data_extractors.progress_bar_utils import run_func_with_fake_progress_bar

MODULE_NAME = 'Experiment'
# The results of an experiment are with a saved to .xlsx located in the experiments db folder (the parent folder of the
# experiment) within a folder name results.
RESULTS_PATH = os.path.join('..', 'results')


def save_result(experiment_results: pd.DataFrame, new_result: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([experiment_results, new_result], ignore_index=True)


def experiment_save_excel(df: pd.DataFrame, experiment_name: str, results_file_path: str):
    config.debug_print(MODULE_NAME, f"Experiment results\n{str(df)}")
    result_path = os.path.join(f'{results_file_path}',
                               f'{str(datetime.now().date())}',
                               f'lifted_{config.LIFTED_INFERENCE}_score_'
                               f'{config.MINIMIZE_VOTER_CONTRIBUTION_EQUATIONS}_dc_'
                               f'{config.MINIMIZE_DC_CONSTRAINTS_EQUATIONS}',
                               f'{experiment_name}.xlsx')
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    # Save the DataFrame to Excel
    df.to_excel(result_path, index=False)


class Experiment:
    def __init__(self,
                 experiment_name: str,
                 database_name: str):
        self._experiment_name = experiment_name
        self._database_name = database_name
        self.results_file_path = RESULTS_PATH
        db_path = os.path.join(f"{self._database_name}")
        self._db_engine = db_interface.Database(db_path)

        self._solver = mip_convertor.create_solver(config.SOLVER_NAME, config.SOLVER_TIME_LIMIT)
        self._abc_convertor = abc_to_mip_convertor.ABCToMIPConvertor(self._solver)

    def run_model(self) -> float:
        print("----------------------------------------------------------------------------")
        print(f"Experiment Name - {self._experiment_name} | Database Name - {self._database_name} start.")

        # Solve the MIP problem.
        mip_solver_progress_bar = run_func_with_fake_progress_bar(
            delay=3,
            loading_message="Running MIP Solver...",
            finish_message="*Solved MIP Problem!*",
            func_to_run=self._abc_convertor.solve,
        )
        time.sleep(2)
        mip_solver_progress_bar.empty()

        # Print the MIP solution.
        config.debug_print(MODULE_NAME, f"The solving time is {str(self._abc_convertor.solving_time)}\n" +
                           str(self._abc_convertor))

        print(f"Experiment Name - {self._experiment_name} | Database Name - {self._database_name} end.")
        print("----------------------------------------------------------------------------\n")

        return self._abc_convertor.solving_time

    def run_experiment(self):
        pass

    def get_db_engine(self):
        return self._db_engine

    def __del__(self):
        self._db_engine.__del__()

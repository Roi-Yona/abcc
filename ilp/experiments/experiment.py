import pandas as pd

import config
import database_server_interface.database_server_interface as db_interface
import ilp.ilp_reduction.ilp_convertor as ilp_convertor
import ilp.ilp_reduction.abc_to_ilp_convertor as abc_ilp_convertor

MODULE_NAME = 'Experiment'
MINUTE = 1000 * 60
RESULTS_PATH = 'results\\'
SERVER = 'LAPTOP-MO1JPG72'


def save_result(experiment_results: pd.DataFrame, new_result: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([experiment_results, new_result], ignore_index=True)


class Experiment:
    def __init__(self,
                 experiment_name: str,
                 database_name: str,
                 solver_time_limit: int,
                 solver_name: str):
        self._experiment_name = experiment_name
        self._database_name = database_name
        self.results_file_path = RESULTS_PATH
        self._db_engine = db_interface.database_connect(SERVER, self._database_name)

        self._solver = ilp_convertor.create_solver(solver_name, MINUTE * solver_time_limit)
        self._abc_convertor = abc_ilp_convertor.ABCToILPConvertor(self._solver)

    @staticmethod
    def create_results_df() -> pd.DataFrame:
        pass

    def run_model(self, experiment_name: str, database_name: str) -> float:
        solved_time_scale = 100
        print("----------------------------------------------------------------------------")
        print(f"Experiment Name - {self._experiment_name} | Database Name - {self._database_name} start.")

        # Solve the ILP problem.
        self._abc_convertor.solve()

        # Print the ILP solution.
        config.debug_print(MODULE_NAME, f"The solving time is {str(self._abc_convertor.solving_time)}\n" +
                           str(self._abc_convertor))

        print(f"Experiment Name - {self._experiment_name} | Database Name - {self._database_name} end.")
        print("----------------------------------------------------------------------------\n")

        return self._abc_convertor.solving_time * solved_time_scale if self._abc_convertor.solving_time != -1 \
            else self._abc_convertor.solving_time

    def run_experiment(self):
        pass

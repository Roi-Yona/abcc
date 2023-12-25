from sqlalchemy.engine import Engine
import ortools.linear_solver.pywraplp as pywraplp
import time


class Experiment:
    """An abstract class for an ILP experiment.
    """
    def __init__(self,
                 solver: pywraplp.Solver,
                 database_engine: Engine):
        self._solver = solver
        self._db_engine = database_engine
        self.convertor = None
        self._experiment_time = -1

    def extract_data_from_db(self) -> None:
        # Abstract function.
        pass

    def create_ilp_problem_convertor(self) -> None:
        # Abstract function.
        pass

    def __str__(self):
        return f"The experiment duration time is {str(self._experiment_time)}\n" + str(self.convertor)

    def run_experiment(self) -> None:
        # Extract the needed ABC data from the DB.
        self.extract_data_from_db()

        # Convert the problem to an ILP problem.
        self.create_ilp_problem_convertor()
        self.convertor.define_ilp_model_variables()
        self.convertor.define_ilp_model_constraints()
        self.convertor.define_ilp_model_objective()

        # Solve the ILP problem.
        start_time = time.time()
        self.convertor.solve()
        end_time = time.time()
        self._experiment_time = end_time - start_time


def experiment_runner(experiment: Experiment, experiment_name: str, database_name: str) -> None:
    print("----------------------------------------------------------------------------")
    print(f"Experiment Name - {experiment_name} Database Name - {database_name} start.")
    # Run the experiment (also extracted the required data from the DB).
    experiment.run_experiment()
    # Print and experiment the results.
    print(experiment)
    print(f"Experiment Name: {experiment_name} Database Name: {database_name} end.")
    print("----------------------------------------------------------------------------\n")


if __name__ == '__main__':
    pass

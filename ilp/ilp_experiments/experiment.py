from sqlalchemy.engine import Engine
import ortools.linear_solver.pywraplp as pywraplp
import ilp.ilp_reduction.abc_to_ilp_convertor as ilp_convertor


class Experiment:
    """An abstract class for an ILP experiment.
    """
    def __init__(self,
                 abc_convertor: ilp_convertor.ABCToILPConvertor,
                 database_engine: Engine):
        self._abc_convertor = abc_convertor
        self._db_engine = database_engine
        self.convertor = None
        self._experiment_time = -1

    def extract_data_from_db(self) -> None:
        # Abstract function.
        pass

    def convert_to_ilp(self) -> None:
        # Abstract function.
        pass

    def extract_and_convert(self) -> None:
        # Extract problem data from the database.
        self.extract_data_from_db()

        # Convert to ILP problem (add the model properties)
        self.convert_to_ilp()


def create_solver(solver_name: str, solver_time_limit: int) -> pywraplp.Solver:
    solver = pywraplp.Solver.CreateSolver(solver_name)
    if not solver:
        print("ERROR: Creating solver failed.")
        exit(1)
    solver.set_time_limit(solver_time_limit)
    return solver


if __name__ == '__main__':
    pass


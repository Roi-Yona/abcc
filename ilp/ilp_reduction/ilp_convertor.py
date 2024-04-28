import ortools.linear_solver.pywraplp as pywraplp
import time
import config
MODULE_NAME = "ILP Convertor"


class ILPConvertor:
    """An abstract class for converting a general problem to an ILP problem.
    """

    def __init__(self, solver: pywraplp.Solver):
        """Initializing the convertor.

        :param solver: The input solver wrapper.
        """
        # Initialize solver related variables.
        self._model = solver
        self._solved = False
        self.solver_status = None
        self.solving_time = -1

    def solve(self) -> None:
        """Solve the ILP problem, and saves the time it took,
        the status and if it solved indicator
        :return:
        """
        # Solve the ILP problem.
        start_time = time.time()
        self.solver_status = self._model.Solve()
        end_time = time.time()
        if self.solver_status == pywraplp.Solver.OPTIMAL:
            self._solved = True
        self.solving_time = end_time - start_time

    def get_model_state(self) -> str:
        """Creates a representation for the model current state.

        :return: A string that represents the general problem assignment.
        """
        # Abstract function
        pass

    def __str__(self):
        """Creates a str depending only on the solver state function if solver,
        otherwise the solver status"""
        solution = ""
        if self._solved:
            solution = self.get_model_state()
        else:
            solution = f"The solver doesn't have an optimal solution, the solver status is {str(self.solver_status)}."
        return solution

    def print_all_model_variables(self) -> None:
        """Print all the model variables.
        :return:
        """
        if self._solved:
            for var in self._model.variables():
                print(f"Var name is {str(var)}, and var value is {str(var.solution_value())}")


def create_solver(solver_name: str, solver_time_limit: int) -> pywraplp.Solver:
    """Create a new pywraplp solver.
    :param solver_name: The solver name.
    :param solver_time_limit: The solver time limit in seconds.
    :return:
    """
    solver = pywraplp.Solver.CreateSolver(solver_name)
    if not solver:
        print("ERROR: Creating solver failed.")
        exit(1)
    solver.set_time_limit(solver_time_limit)
    return solver


if __name__ == '__main__':
    pass

import time
import ortools.linear_solver.pywraplp as pywraplp

import config

MODULE_NAME = "MIP Convertor"


class MIPConvertor:
    """An abstract class for converting a general problem to an MIP problem.
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
        """Solve the MIP problem, and saves the time it took,
        the status and if it solved indicator.
        :return:
        """
        # Solve the MIP problem.
        start_time = time.time()
        self.solver_status = self._model.Solve()
        end_time = time.time()
        if self.solver_status == pywraplp.Solver.OPTIMAL:
            self._solved = True
        self.solving_time = end_time - start_time

    def get_model_state(self) -> str:
        """Creates representation for the model current state.

        :return: A string that represents the general problem assignment.
        """
        # Abstract function
        pass

    def __str__(self):
        """Creates representation for the module assignment,
        if there is no solution than a proper string containing the solver status will return.

        :return: The representative string.
        """
        if self._solved:
            solution = self.get_model_state()
        else:
            solution = f"The solver doesn't have an optimal solution, the solver status is {str(self.solver_status)}."
        return solution

    def print_all_model_variables(self) -> None:
        """Print all the model variables (only if we are in DEBUG mode).
        """
        if config.DEBUG:
            if self._solved:
                for var in self._model.variables():
                    print(f"Var name is {str(var)}, and var value is {str(var.solution_value())}")


def create_solver(solver_name: str, solver_time_limit: int) -> pywraplp.Solver:
    """Create a new pywraplp solver.
    :param solver_name: The solver name.
    :param solver_time_limit: The solver time limit in milliseconds.
    :return:
    """
    if solver_name == "GUROBI":
        solver = pywraplp.Solver.CreateSolver("GUROBI_MIXED_INTEGER_PROGRAMMING")
    else:
        solver = pywraplp.Solver.CreateSolver(solver_name)
    if not solver:
        print("ERROR: Creating solver failed.")
        exit(1)
    solver.set_time_limit(solver_time_limit)
    return solver


if __name__ == '__main__':
    pass

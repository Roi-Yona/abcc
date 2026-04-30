import time

import config
import mip.mip_reduction.solver_wrapper as solver_wrapper

MODULE_NAME = "MIP Convertor"


class MIPConvertor:
    """An abstract class for converting a general problem to an MIP problem.
    """

    def __init__(self, solver):
        """Initializing the convertor.

        Accept either a `SolverWrapper` or a raw `pywraplp.Solver` instance.
        If a raw solver is provided, wrap it with `PywraplpAdapter` so the
        rest of the code can rely on the unified SolverWrapper API.
        :param solver: The input solver wrapper or raw solver.
        """
        # Initialize solver related variables.
        if hasattr(solver, 'model_add_bool_var'):
            self._model = solver
        else:
            # Prefer to adapt known pywraplp Solver objects.
            try:
                self._model = solver_wrapper.PywraplpAdapter(solver)
            except Exception:
                # Fallback: use as-is (may raise later if incompatible)
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
        self._model.solve()
        self.solver_status = self._model.model_status()
        end_time = time.time()
        if self.solver_status == config.SOLVER_FOUND_OPTIMAL_STATUS:
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
                for (var_name, var_value) in self._model.model_variables():
                    print(f"Var name is {var_name}, and var value is {str(var_value)}")


if __name__ == '__main__':
    pass

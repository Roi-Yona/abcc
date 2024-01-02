import ortools.linear_solver.pywraplp as pywraplp
import time


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
        solution = ""
        if self._solved:
            solution = self.get_model_state()
        else:
            solution = f"The solver doesn't hane an optimal solution, the solver status is {str(self.solver_status)}."
        return solution

    def print_all_model_variables(self) -> None:
        if self._solved:
            for var in self._model.variables():
                print(f"Var name is {str(var)}, and var value is {str(var.solution_value())}")


if __name__ == '__main__':
    pass

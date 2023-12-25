import ortools.linear_solver.pywraplp as pywraplp


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
        self._solver_status = None

    def define_ilp_model_variables(self) -> None:
        # Abstract function.
        pass

    def define_ilp_model_constraints(self) -> None:
        # Abstract function.
        pass

    def define_ilp_model_objective(self) -> None:
        # Abstract function.
        pass

    def solve(self) -> None:
        self._solver_status = self._model.Solve()
        if self._solver_status == pywraplp.Solver.OPTIMAL:
            self._solved = True

    def show_solution(self) -> str:
        """Creates a representation for the problem solution.

           An abstract function.

        :return: A string that represents the general problem solution.
        """
        pass

    def __str__(self):
        solution = ""
        if self._solved:
            solution = self.show_solution()
        else:
            solution = f"The solver doesn't hane an optimal solution, the solver status is {str(self._solver_status)}."
        return solution

    def print_all_model_variables(self) -> None:
        if self._solved:
            for var in self._model.variables():
                print(f"Var name is {str(var)}, and var value is {str(var.solution_value())}")


if __name__ == '__main__':
    pass

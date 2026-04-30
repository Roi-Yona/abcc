import ortools.linear_solver.pywraplp as pywraplp
try:
    import gurobipy
except Exception:
    gurobipy = None

import config

MODULE_NAME = "Solver Wrapper"


def get_variable_value(var):
    if config.SOLVER_NAME == "GUROBI":
        return var.X
    else:
        return var.solution_value()


class SolverWrapper:
    def __init__(self, solver_name: str, solver_time_limit: int):
        """Initializing the solver.
        :param solver_name: The solver name.
        :param solver_time_limit: The solver time limit in milliseconds.
        """
        self._solver_name = solver_name
        if self._solver_name == "GUROBI":
            m = gurobipy.Model("gurobi_mip")
            # Gurobi API works in seconds.
            m.setParam("TimeLimit", solver_time_limit / 1000)
            # m = pywraplp.Solver.CreateSolver("GUROBI_MIXED_INTEGER_PROGRAMMING")
        else:
            m = pywraplp.Solver.CreateSolver(solver_name)
            m.set_time_limit(solver_time_limit)
        if not m:
            print("ERROR: Creating solver failed.")
            exit(1)
        self._model = m
        self._solver_status = config.SOLVER_MODEL_NOT_SOLVED_ERROR_STATUS

    def solve(self) -> None:
        """Solve the MIP problem.
        """
        if self._solver_name == "GUROBI":
            self._model.optimize()
            self._solver_status = self._model.status
        else:
            self._solver_status = self._model.Solve()

    def model_status(self):
        """Returns the model status.
        Values are based on the constants defined in the config file.
        """
        if self._solver_name == "GUROBI":
            if self._solver_status == gurobipy.GRB.LOADED:
                return config.SOLVER_MODEL_NOT_SOLVED_ERROR_STATUS
            elif self._solver_status == gurobipy.GRB.OPTIMAL:
                return config.SOLVER_FOUND_OPTIMAL_STATUS
            elif self._solver_status == gurobipy.GRB.INFEASIBLE:
                return config.SOLVER_PROVEN_INFEASIBLE_STATUS
            elif self._solver_status == gurobipy.GRB.INF_OR_UNBD:
                return config.SOLVER_PROVEN_INFEASIBLE_STATUS
            elif self._solver_status == gurobipy.GRB.UNBOUNDED:
                return config.SOLVER_PROVEN_UNBOUNDED_STATUS
            elif self._solver_status == gurobipy.GRB.CUTOFF:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.ITERATION_LIMIT:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.NODE_LIMIT:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.TIME_LIMIT:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.SOLUTION_LIMIT:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.INTERRUPTED:
                return config.SOLVER_ABNORMAL_ERROR_STATUS
            elif self._solver_status == gurobipy.GRB.NUMERIC:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.SUBOPTIMAL:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.INPROGRESS:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.USER_OBJ_LIMIT:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.WORK_LIMIT:
                return config.SOLVER_TIMEOUT_STATUS
            elif self._solver_status == gurobipy.GRB.MEM_LIMIT:
                return config.SOLVER_TIMEOUT_STATUS
        else:
            return self._solver_status

    def model_optimal(self) -> bool:
        """Returns the true if the model found an optimal solution.
        """
        return self.model_status() == config.SOLVER_FOUND_OPTIMAL_STATUS

    def model_variables(self):
        """Returns a dictionary of the variable name: optimal value.
        """
        if self._solver_name == "GUROBI":
            return {v.VarName: v.X for v in self._model.getVars()}
        else:
            return {str(v): v.solution_value() for v in self._model.variables()}

    def model_number_of_constraints(self):
        if self._solver_name == "GUROBI":
            return self._model.numconstrs
        else:
            return self._model.NumConstraints()

    def model_number_of_variables(self):
        if self._solver_name == "GUROBI":
            return self._model.numvars
        else:
            return self._model.NumVariables()

    def model_add_bool_var(self, var_name):
        if self._solver_name == "GUROBI":
            return self._model.addVar(vtype=gurobipy.GRB.BINARY, name=var_name)
        else:
            return self._model.BoolVar(var_name)

    def model_add_int_var(self, lb, ub, var_name):
        if self._solver_name == "GUROBI":
            return self._model.addVar(vtype=gurobipy.GRB.INTEGER, lb=lb, ub=ub, name=var_name)
        else:
            return self._model.IntVar(lb, ub, var_name)

    def model_add_num_var(self, lb, ub, var_name):
        if self._solver_name == "GUROBI":
            return self._model.addVar(vtype=gurobipy.GRB.CONTINUOUS, lb=lb, ub=ub, name=var_name)
        else:
            return self._model.NumVar(lb, ub, var_name)

    def model_add_constraint(self, constraint):
        if self._solver_name == "GUROBI":
            self._model.addConstr(constraint)
        else:
            self._model.Add(constraint)

    def model_add_objective_maximize(self, expr):
        if self._solver_name == "GUROBI":
            self._model.setObjective(expr, gurobipy.GRB.MAXIMIZE)
        else:
            self._model.Maximize(expr)


class PywraplpAdapter:
    """Adapter that exposes the SolverWrapper API for an existing
    ortools `pywraplp.Solver` instance.

    This allows tests and callers that already construct a pywraplp.Solver
    to be passed directly to convertors without requiring them to create a
    SolverWrapper instance.
    """
    def __init__(self, pywrap_solver):
        self._model = pywrap_solver
        self._solver_status = config.SOLVER_MODEL_NOT_SOLVED_ERROR_STATUS

    def solve(self) -> None:
        self._solver_status = self._model.Solve()

    def model_status(self):
        return self._solver_status

    def model_optimal(self) -> bool:
        return self.model_status() == config.SOLVER_FOUND_OPTIMAL_STATUS

    def model_variables(self):
        return {str(v): v.solution_value() for v in self._model.variables()}

    def model_number_of_constraints(self):
        return self._model.NumConstraints()

    def model_number_of_variables(self):
        return self._model.NumVariables()

    def model_add_bool_var(self, var_name):
        return self._model.BoolVar(var_name)

    def model_add_int_var(self, lb, ub, var_name):
        return self._model.IntVar(lb, ub, var_name)

    def model_add_num_var(self, lb, ub, var_name):
        return self._model.NumVar(lb, ub, var_name)

    def model_add_constraint(self, constraint):
        self._model.Add(constraint)

    def model_add_objective_maximize(self, expr):
        self._model.Maximize(expr)



if __name__ == '__main__':
    pass


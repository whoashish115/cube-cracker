from magiccube import Cube, BasicSolver

def solve_cube(facelet_string):
    try:
        cube = Cube(3, facelet_string)
        solver = BasicSolver(cube)
        solver.solve()
        return solver.moves
    except Exception as e:
        print(f"Solver error: {e}")
        return []
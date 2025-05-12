class RubiksCube:
    def __init__(self):
        self.colors = {
            'U': ['W'] * 9, 'D': ['Y'] * 9,
            'F': ['G'] * 9, 'B': ['B'] * 9,
            'L': ['O'] * 9, 'R': ['R'] * 9
        }

    def get_cubelets(self):
        cubelets = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    faces = {}
                    if y == 1: faces['U'] = self.colors['U'][(x + 1) + (1 - z) * 3]
                    if y == -1: faces['D'] = self.colors['D'][(x + 1) + (z + 1) * 3]
                    if z == 1: faces['F'] = self.colors['F'][(x + 1) + (1 - y) * 3]
                    if z == -1: faces['B'] = self.colors['B'][(1 - x) + (1 - y) * 3]
                    if x == -1: faces['L'] = self.colors['L'][(z + 1) + (1 - y) * 3]
                    if x == 1: faces['R'] = self.colors['R'][(1 - z) + (1 - y) * 3]
                    cubelets.append(((x, y, z), faces))
        return cubelets

    def shuffle(self): pass
    def reset(self): pass
    def perform_move(self, move): pass

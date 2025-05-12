import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import sys, itertools, random, time
import pygame.freetype

pygame.init()
display = (900, 700)
screen = pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
icon_surface = pygame.image.load("icon.png")
pygame.display.set_icon(icon_surface)
pygame.display.set_caption("Cube Cracker")
font = pygame.freetype.SysFont("Consolas", 18)
glMatrixMode(GL_PROJECTION)
gluPerspective(45, display[0] / display[1], 0.1, 100)
glMatrixMode(GL_MODELVIEW)
glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_POSITION, [2, 2, 2, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
glEnable(GL_COLOR_MATERIAL)
glClearColor(2/255, 5/255, 10/255, 1)
# Colors & faces
colors = {
    'U': (1, 1, 1), 'D': (1, 1, 0), 'F': (0, 1, 0),
    'B': (0, 0, 1), 'L': (1, 0.5, 0), 'R': (1, 0, 0), '': (0.1, 0.1, 0.1)
}
face_dirs = {
    'U': (0, 1, 0), 'D': (0, -1, 0), 'F': (0, 0, 1),
    'B': (0, 0, -1), 'L': (-1, 0, 0), 'R': (1, 0, 0)
}
move_history = []

def init_cubelets():
    cubelets = {}
    for x, y, z in itertools.product([-1, 0, 1], repeat=3):
        faces = {}
        if y == 1: faces['U'] = 'U'
        if y == -1: faces['D'] = 'D'
        if z == 1: faces['F'] = 'F'
        if z == -1: faces['B'] = 'B'
        if x == -1: faces['L'] = 'L'
        if x == 1: faces['R'] = 'R'
        cubelets[(x, y, z)] = faces
    return cubelets

original_cubelets = init_cubelets()
current_cubelets = dict(original_cubelets)

def draw_box(size):
    hs = size / 2
    v = [[-hs, -hs, -hs], [hs, -hs, -hs], [hs, hs, -hs], [-hs, hs, -hs],
         [-hs, -hs, hs], [hs, -hs, hs], [hs, hs, hs], [-hs, hs, hs]]
    faces = [(0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (1,2,6,5), (0,3,7,4)]
    for f in faces:
        glBegin(GL_QUADS)
        for vert in f: glVertex3fv(v[vert])
        glEnd()

def draw_sticker(face, color):
    dx, dy, dz = face_dirs[face]
    glPushMatrix()
    glTranslatef(dx * 0.51, dy * 0.51, dz * 0.51)
    if face == 'U': glRotatef(-90, 1, 0, 0)
    elif face == 'D': glRotatef(90, 1, 0, 0)
    elif face == 'F': pass
    elif face == 'B': glRotatef(180, 0, 1, 0)
    elif face == 'L': glRotatef(-90, 0, 1, 0)
    elif face == 'R': glRotatef(90, 0, 1, 0)
    glColor3fv(colors[color])
    glBegin(GL_QUADS)
    glVertex3f(-0.4, -0.4, 0.01)
    glVertex3f(0.4, -0.4, 0.01)
    glVertex3f(0.4, 0.4, 0.01)
    glVertex3f(-0.4, 0.4, 0.01)
    glEnd()
    glPopMatrix()

def draw_cubelet(pos, faces):
    glPushMatrix()
    glTranslatef(pos[0]*1.05, pos[1]*1.05, pos[2]*1.05)
    glColor3f(0.1, 0.1, 0.1)
    draw_box(1)
    for face, color in faces.items():
        draw_sticker(face, color)
    glPopMatrix()

def draw_cube():
    for pos, faces in current_cubelets.items():
        draw_cubelet(pos, faces)

def rotate_face(face, prime=False):
    global current_cubelets
    move_history.append((face, prime))
    axis_map = {'U': 1, 'D': 1, 'F': 2, 'B': 2, 'L': 0, 'R': 0}
    axis = axis_map[face]
    layer_val = 1 if face in 'URFB' else -1
    new_cubelets = {}
    for pos, faces in current_cubelets.items():
        x, y, z = pos
        if (axis == 0 and x == layer_val) or \
           (axis == 1 and y == layer_val) or \
           (axis == 2 and z == layer_val):
            vec = [x, y, z]
            i1, i2 = [i for i in range(3) if i != axis]
            if not prime:
                vec[i1], vec[i2] = -vec[i2], vec[i1]
            else:
                vec[i1], vec[i2] = vec[i2], -vec[i1]
            new_faces = {}
            for f, c in faces.items():
                fvec = face_dirs[f]
                fv = list(fvec)
                if not prime:
                    fv[i1], fv[i2] = -fv[i2], fv[i1]
                else:
                    fv[i1], fv[i2] = fv[i2], -fv[i1]
                for nf, d in face_dirs.items():
                    if tuple(fv) == d:
                        new_faces[nf] = c
                        break
            new_cubelets[tuple(vec)] = new_faces
        else:
            new_cubelets[pos] = faces.copy()
    current_cubelets = new_cubelets

def dummy_solve():
    return list(reversed(move_history))
def draw_instructions():
    lines = [
        "[U D L R F B] – Rotate Faces",
        "[Shift + Key] – Prime Move",
        "[S] – Shuffle   |   [SPACE] – Solve",
        "[Mouse Drag] – Rotate Cube"
    ]

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, display[0], 0, display[1], -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    y = 10
    for line in lines:
        surf, _ = font.render(line, (255, 255, 255), (0, 0, 0))
        text_data = pygame.image.tostring(surf, "RGBA", True)
        w, h = surf.get_size()

        glRasterPos2f(10, display[1] - y - h)
        glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        y += 22

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def main():
    clock = pygame.time.Clock()
    rotating = False
    mouse_last = None
    rot = [20, -30]
    solving = False
    steps = []

    while True:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, -15)
        glRotatef(rot[0], 1, 0, 0)
        glRotatef(rot[1], 0, 1, 0)
        draw_cube()
        draw_instructions()
        pygame.display.flip()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                rotating = True
                mouse_last = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                rotating = False
            elif event.type == pygame.MOUSEMOTION and rotating:
                x, y = event.pos
                dx, dy = x - mouse_last[0], y - mouse_last[1]
                rot[1] += dx * 0.4
                rot[0] += dy * 0.4
                mouse_last = (x, y)
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                prime = bool(mods & pygame.KMOD_SHIFT)
                if event.key == pygame.K_u: rotate_face('U', prime)
                elif event.key == pygame.K_d: rotate_face('D', prime)
                elif event.key == pygame.K_l: rotate_face('L', prime)
                elif event.key == pygame.K_r: rotate_face('R', prime)
                elif event.key == pygame.K_f: rotate_face('F', prime)
                elif event.key == pygame.K_b: rotate_face('B', prime)
                elif event.key == pygame.K_s:
                    for _ in range(20):
                        rotate_face(random.choice('UDFBLR'), random.choice([True, False]))
                elif event.key == pygame.K_SPACE:
                    solving = True
                    steps = dummy_solve()

        if solving and steps:
            face, prime = steps.pop(0)
            rotate_face(face, not prime)
            time.sleep(0.05)
        elif solving and not steps:
            solving = False
        clock.tick(60)

if __name__ == "__main__":
    main()

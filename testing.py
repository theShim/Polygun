import pygame
import numpy as np
import math

# -------------------- Pygame setup --------------------
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4D Hypercube (Tesseract)")
clock = pygame.time.Clock()

# -------------------- Hypercube data --------------------

# 16 vertices of a 4D hypercube
points_4d = np.array([
    [x, y, z, w]
    for x in (-1, 1)
    for y in (-1, 1)
    for z in (-1, 1)
    for w in (-1, 1)
], dtype=float)

# Generate edges (vertices differing in exactly one coordinate)
edges = []
for i in range(len(points_4d)):
    for j in range(i + 1, len(points_4d)):
        if np.sum(points_4d[i] != points_4d[j]) == 1:
            edges.append((i, j))

# -------------------- Rotation matrices --------------------

def rot_xy(a):
    return np.array([
        [ math.cos(a), -math.sin(a), 0, 0],
        [ math.sin(a),  math.cos(a), 0, 0],
        [ 0, 0, 1, 0],
        [ 0, 0, 0, 1]
    ])

def rot_xz(a):
    return np.array([
        [math.cos(a), 0, math.sin(a), 0],
        [0, 1, 0, 0],
        [-math.sin(a), 0, math.cos(a), 0],
        [0, 0, 0, 1]
    ])

def rot_zw(a):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0,  math.cos(a), -math.sin(a)],
        [0, 0,  math.sin(a),  math.cos(a)]
    ])

def rot_xw(a):
    return np.array([
        [math.cos(a), 0, 0, -math.sin(a)],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [math.sin(a), 0, 0, math.cos(a)]
    ])

# -------------------- Projection --------------------

def project_4d_to_3d(p, d=3):
    w = 1 / (d - p[3])
    return p[:3] * w

def project_3d_to_2d(p, d=4):
    z = 1 / (d - p[2])
    return p[:2] * z

# -------------------- Main loop --------------------

angle = 0.0
scale = 1200
center = np.array([WIDTH // 2, HEIGHT // 2])

running = True
while running:
    dt = clock.tick(60) / 1000
    screen.fill((10, 10, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update rotation
    angle += 1.0 * dt

    rotation = rot_zw(angle) @ rot_xw(0.4) @ rot_xz(angle)
    rotated = points_4d @ rotation.T

    # Project points
    projected = []
    for p in rotated:
        p3 = project_4d_to_3d(p)
        p2 = project_3d_to_2d(p3)
        projected.append(p2)

    projected = np.array(projected) * scale + center

    # Draw edges
    for i, j in edges:
        pygame.draw.line(
            screen,
            (120, 200, 255),
            projected[i],
            projected[j],
            1
        )

    # Draw vertices
    for p in projected:
        pygame.draw.circle(screen, (255, 255, 255), p.astype(int), 3)

    pygame.display.flip()

pygame.quit()

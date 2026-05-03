import pygame
import math

# ── constants ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 800, 600
TOOLBAR_H = 60
CANVAS_H = HEIGHT - TOOLBAR_H

# Palette colours shown as swatches
PALETTE = [
    (255, 255, 255),
    (180, 180, 180),
    (255,  80,  80),
    (255, 160,  40),
    (255, 220,  40),
    ( 80, 200,  80),
    ( 40, 160, 255),
    (160,  80, 255),
    (255, 100, 200),
    ( 80, 220, 220),
]

TOOLS = ['pen', 'rect', 'circle', 'eraser']
TOOL_LABELS = {'pen': 'Pen', 'rect': 'Rect', 'circle': 'Circle', 'eraser': 'Eraser'}


# ── helpers ────────────────────────────────────────────────────────────────────

def draw_toolbar(screen, tool, draw_color, radius, font):
    """Render the toolbar at the top of the screen."""
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, TOOLBAR_H))
    pygame.draw.line(screen, (70, 70, 70), (0, TOOLBAR_H - 1), (WIDTH, TOOLBAR_H - 1))

    # ── tool buttons
    btn_w, btn_h = 72, 36
    for i, t in enumerate(TOOLS):
        x = 8 + i * (btn_w + 6)
        y = 12
        active = (t == tool)
        bg = (80, 120, 200) if active else (55, 55, 55)
        border = (140, 170, 255) if active else (90, 90, 90)
        pygame.draw.rect(screen, bg, (x, y, btn_w, btn_h), border_radius=6)
        pygame.draw.rect(screen, border, (x, y, btn_w, btn_h), 1, border_radius=6)
        lbl = font.render(TOOL_LABELS[t], True, (230, 230, 230))
        screen.blit(lbl, (x + btn_w // 2 - lbl.get_width() // 2,
                          y + btn_h // 2 - lbl.get_height() // 2))

    # ── palette swatches
    sw = 28
    px_start = 8 + len(TOOLS) * (btn_w + 6) + 10
    for i, c in enumerate(PALETTE):
        px = px_start + i * (sw + 4)
        py = 16
        pygame.draw.rect(screen, c, (px, py, sw, sw), border_radius=4)
        if c == draw_color:
            pygame.draw.rect(screen, (255, 255, 255), (px, py, sw, sw), 2, border_radius=4)
        else:
            pygame.draw.rect(screen, (80, 80, 80), (px, py, sw, sw), 1, border_radius=4)

    # ── current colour + size preview
    cx = px_start + len(PALETTE) * (sw + 4) + 14
    pygame.draw.rect(screen, (20, 20, 20), (cx, 10, 44, 40), border_radius=6)
    pygame.draw.rect(screen, (80, 80, 80), (cx, 10, 44, 40), 1, border_radius=6)
    disp_r = min(radius, 18)
    if tool == 'eraser':
        pygame.draw.circle(screen, (200, 200, 200), (cx + 22, 30), disp_r)
        pygame.draw.circle(screen, (120, 120, 120), (cx + 22, 30), disp_r, 1)
    else:
        pygame.draw.circle(screen, draw_color, (cx + 22, 30), disp_r)

    # ── size hint
    hint = font.render(f"size {radius}", True, (150, 150, 150))
    screen.blit(hint, (cx + 50, 22))


def draw_preview(screen, tool, start, end, draw_color, radius):
    """Ghost preview while dragging rect / circle tools."""
    if tool == 'rect':
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        s = pygame.Surface((w or 1, h or 1), pygame.SRCALPHA)
        pygame.draw.rect(s, (*draw_color, 80), (0, 0, w or 1, h or 1), radius)
        pygame.draw.rect(s, (*draw_color, 180), (0, 0, w or 1, h or 1), max(1, radius), border_radius=2)
        screen.blit(s, (x, y))
    elif tool == 'circle':
        rx = abs(end[0] - start[0]) // 2
        ry = abs(end[1] - start[1]) // 2
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        if rx > 1 and ry > 1:
            s = pygame.Surface((rx * 2 + 4, ry * 2 + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*draw_color, 80), (2, 2, rx * 2, ry * 2))
            pygame.draw.ellipse(s, (*draw_color, 180), (2, 2, rx * 2, ry * 2), max(1, radius))
            screen.blit(s, (cx - rx - 2, cy - ry - 2))


def commit_shape(canvas, tool, start, end, draw_color, radius):
    """Stamp a finished rect or circle onto the persistent canvas."""
    if tool == 'rect':
        x = min(start[0], end[0])
        y = min(start[1], end[1]) - TOOLBAR_H
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.rect(canvas, draw_color, (x, y, w, h), max(1, radius), border_radius=2)
    elif tool == 'circle':
        rx = abs(end[0] - start[0]) // 2
        ry = abs(end[1] - start[1]) // 2
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2 - TOOLBAR_H
        if rx > 1 and ry > 1:
            pygame.draw.ellipse(canvas, draw_color,
                                (cx - rx, cy - ry, rx * 2, ry * 2), max(1, radius))


def draw_line_between(canvas, index, start, end, width, draw_color, eraser):
    """Draw a smooth stroke segment between two mouse positions."""
    color = (0, 0, 0) if eraser else draw_color
    r = width * 3 if eraser else width

    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy), 1)

    for i in range(iterations):
        progress = i / iterations
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1]) - TOOLBAR_H
        if y >= 0:
            pygame.draw.circle(canvas, color, (x, y), r)


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Drawing App")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    # persistent canvas (only the drawing area, no toolbar)
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill((0, 0, 0))

    radius = 8
    tool = 'pen'
    draw_color = (100, 160, 255)
    points = []

    drag_start = None          # for rect / circle drag
    mouse_on_canvas = False    # True when cursor is below toolbar

    while True:
        pressed = pygame.key.get_pressed()
        alt_held  = pressed[pygame.K_LALT]  or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        mx, my = pygame.mouse.get_pos()
        mouse_on_canvas = my >= TOOLBAR_H

        for event in pygame.event.get():
            # ── quit
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_w and ctrl_held) or \
                   (event.key == pygame.K_F4 and alt_held) or \
                   event.key == pygame.K_ESCAPE:
                    return
                # keyboard shortcuts
                if event.key == pygame.K_p: tool = 'pen'
                if event.key == pygame.K_r: tool = 'rect'
                if event.key == pygame.K_c: tool = 'circle'
                if event.key == pygame.K_e: tool = 'eraser'
                if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    canvas.fill((0, 0, 0))   # clear canvas

            # ── scroll wheel → resize brush
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:   # scroll up
                    radius = min(80, radius + 1)
                elif event.button == 5: # scroll down
                    radius = max(1, radius - 1)

                # left click on toolbar → check tool buttons & palette
                if event.button == 1 and my < TOOLBAR_H:
                    btn_w, btn_h = 72, 36
                    for i, t in enumerate(TOOLS):
                        bx = 8 + i * (btn_w + 6)
                        by = 12
                        if bx <= mx <= bx + btn_w and by <= my <= by + btn_h:
                            tool = t
                    sw = 28
                    px_start = 8 + len(TOOLS) * (btn_w + 6) + 10
                    for i, c in enumerate(PALETTE):
                        px = px_start + i * (sw + 4)
                        if px <= mx <= px + sw and 16 <= my <= 16 + sw:
                            draw_color = c
                            if tool == 'eraser':
                                tool = 'pen'   # switch back when picking colour

                # start drag for shapes
                if event.button == 1 and mouse_on_canvas:
                    if tool in ('rect', 'circle'):
                        drag_start = (mx, my)
                    elif tool in ('pen', 'eraser'):
                        points = [(mx, my)]

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drag_start and tool in ('rect', 'circle'):
                    commit_shape(canvas, tool, drag_start, (mx, my), draw_color, radius)
                    drag_start = None

            if event.type == pygame.MOUSEMOTION:
                if mouse_on_canvas and tool in ('pen', 'eraser'):
                    if pygame.mouse.get_pressed()[0]:
                        points.append((mx, my))
                        points = points[-512:]

        # ── draw pen / eraser strokes onto canvas each frame
        if tool in ('pen', 'eraser') and len(points) >= 2:
            for i in range(len(points) - 1):
                draw_line_between(canvas, i, points[i], points[i + 1],
                                  radius, draw_color, tool == 'eraser')
            points = [points[-1]]   # keep only last point to avoid re-drawing

        # ── compose final frame
        screen.fill((0, 0, 0))
        screen.blit(canvas, (0, TOOLBAR_H))

        # shape preview while dragging
        if drag_start and tool in ('rect', 'circle'):
            draw_preview(screen, tool, drag_start, (mx, my), draw_color, radius)

        # cursor crosshair on canvas
        if mouse_on_canvas:
            if tool == 'eraser':
                pygame.draw.circle(screen, (160, 160, 160), (mx, my), radius * 3, 1)
            else:
                pygame.draw.circle(screen, draw_color, (mx, my), radius, 1)

        draw_toolbar(screen, tool, draw_color, radius, font)
        pygame.display.flip()
        clock.tick(60)


main()
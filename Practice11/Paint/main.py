import pygame
import math

WIDTH, HEIGHT = 800, 600
TOOLBAR_H     = 60         
CANVAS_H      = HEIGHT - TOOLBAR_H

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

TOOLS = ['pen', 'rect', 'circle', 'eraser',
         'square', 'rtri', 'etri', 'rhombus']

TOOL_LABELS = {
    'pen':     'Pen',
    'rect':    'Rect',
    'circle':  'Circle',
    'eraser':  'Eraser',

    'square':  'Square',       
    'rtri':    'R-Tri',        
    'etri':    'E-Tri',        
    'rhombus': 'Rhombus',      
}


KEY_SHORTCUTS = {
    pygame.K_p: 'pen',
    pygame.K_r: 'rect',
    pygame.K_c: 'circle',
    pygame.K_e: 'eraser',
    pygame.K_s: 'square',
    pygame.K_t: 'rtri',
    pygame.K_y: 'etri',
    pygame.K_h: 'rhombus',
}



def _square_points(start, end):
    
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    
    return [
        (x1,       y1),
        (x2,       y2),
        (x2 - dy,  y2 + dx),
        (x1 - dy,  y1 + dx),
    ]


def _right_triangle_points(start, end):
    
    x1, y1 = start
    x2, y2 = end
    return [
        (x1, y1),           # bottom-left  (right angle)
        (x1, y2),           # top-left
        (x2, y1),           # bottom-right
    ]


def _equilateral_triangle_points(start, end):
    
    x1, y1 = start
    x2, y2 = end
    mx = (x1 + x2) / 2          
    my = (y1 + y2) / 2          
    base = math.hypot(x2 - x1, y2 - y1)
    h    = base * math.sqrt(3) / 2   

    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    # rotate 90° counter-clockwise: (-dy, dx)
    nx, ny = -dy / length, dx / length

    apex = (mx + nx * h, my + ny * h)
    return [(x1, y1), (x2, y2), apex]


def _rhombus_points(start, end):
    
    x1, y1 = start
    x2, y2 = end
    mx = (x1 + x2) / 2     
    my = (y1 + y2) / 2     
    return [
        (mx, y1),   
        (x2, my),   
        (mx, y2),   
        (x1, my),   
    ]


def _polygon_to_int(points):
    
    return [(int(x), int(y)) for x, y in points]



def draw_toolbar(screen, tool, draw_color, radius, font):
    

    
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, TOOLBAR_H))
    pygame.draw.line(screen, (70, 70, 70), (0, TOOLBAR_H - 1), (WIDTH, TOOLBAR_H - 1))

    
    btn_w, btn_h = 64, 26
    cols = 4                    
    for i, t in enumerate(TOOLS):
        col = i % cols
        row = i // cols
        x = 4 + col * (btn_w + 4)
        y = 4 + row * (btn_h + 4)
        active = (t == tool)
        bg     = (80, 120, 200) if active else (55, 55, 55)
        border = (140, 170, 255) if active else (90, 90, 90)
        pygame.draw.rect(screen, bg,     (x, y, btn_w, btn_h), border_radius=5)
        pygame.draw.rect(screen, border, (x, y, btn_w, btn_h), 1, border_radius=5)
        lbl = font.render(TOOL_LABELS[t], True, (230, 230, 230))
        screen.blit(lbl, (x + btn_w // 2 - lbl.get_width() // 2,
                          y + btn_h // 2 - lbl.get_height() // 2))

    
    sw       = 22
    px_start = 4 + cols * (btn_w + 4) + 8
    for i, c in enumerate(PALETTE):
        px = px_start + i * (sw + 3)
        py = 4
        pygame.draw.rect(screen, c, (px, py, sw, sw), border_radius=3)
        
        outline = (255, 255, 255) if c == draw_color else (80, 80, 80)
        pygame.draw.rect(screen, outline, (px, py, sw, sw), 1 if c != draw_color else 2,
                         border_radius=3)

    
    cx = px_start + len(PALETTE) * (sw + 3) + 10
    pygame.draw.rect(screen, (20, 20, 20), (cx, 2, 40, 56), border_radius=5)
    pygame.draw.rect(screen, (80, 80, 80), (cx, 2, 40, 56), 1, border_radius=5)
    disp_r = min(radius, 16)
    if tool == 'eraser':
        pygame.draw.circle(screen, (200, 200, 200), (cx + 20, 30), disp_r)
        pygame.draw.circle(screen, (120, 120, 120), (cx + 20, 30), disp_r, 1)
    else:
        pygame.draw.circle(screen, draw_color, (cx + 20, 30), disp_r)

    
    hint = font.render(f"sz {radius}", True, (150, 150, 150))
    screen.blit(hint, (cx + 44, 24))




def _draw_poly_preview(screen, points, color, thickness):
    
    if len(points) < 3:
        return
    pts = _polygon_to_int(points)
    
    min_x = min(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    max_x = max(p[0] for p in pts)
    max_y = max(p[1] for p in pts)
    w = max(max_x - min_x, 1)
    h = max(max_y - min_y, 1)
    s = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    shifted = [(p[0] - min_x + 1, p[1] - min_y + 1) for p in pts]
    pygame.draw.polygon(s, (*color, 50), shifted)
    pygame.draw.polygon(s, (*color, 180), shifted, max(1, thickness))
    screen.blit(s, (min_x - 1, min_y - 1))


def draw_preview(screen, tool, start, end, draw_color, radius):
    
    if tool == 'rect':
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(s, (*draw_color, 50),  (0, 0, w, h))
            pygame.draw.rect(s, (*draw_color, 180), (0, 0, w, h), max(1, radius))
            screen.blit(s, (x, y))

    elif tool == 'circle':
        rx = abs(end[0] - start[0]) // 2
        ry = abs(end[1] - start[1]) // 2
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        if rx > 1 and ry > 1:
            s = pygame.Surface((rx * 2 + 4, ry * 2 + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*draw_color, 50),  (2, 2, rx * 2, ry * 2))
            pygame.draw.ellipse(s, (*draw_color, 180), (2, 2, rx * 2, ry * 2),
                                max(1, radius))
            screen.blit(s, (cx - rx - 2, cy - ry - 2))

    elif tool == 'square':
        pts = _square_points(start, end)
        _draw_poly_preview(screen, pts, draw_color, radius)

    elif tool == 'rtri':
        pts = _right_triangle_points(start, end)
        _draw_poly_preview(screen, pts, draw_color, radius)

    elif tool == 'etri':
        pts = _equilateral_triangle_points(start, end)
        _draw_poly_preview(screen, pts, draw_color, radius)

    elif tool == 'rhombus':
        pts = _rhombus_points(start, end)
        _draw_poly_preview(screen, pts, draw_color, radius)




def _canvas_pts(points):
    
    return [(int(x), int(y) - TOOLBAR_H) for x, y in points]


def commit_shape(canvas, tool, start, end, draw_color, radius):
    
    th = max(1, radius)     

    if tool == 'rect':
        x = min(start[0], end[0])
        y = min(start[1], end[1]) - TOOLBAR_H
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.rect(canvas, draw_color, (x, y, w, h), th, border_radius=2)

    elif tool == 'circle':
        rx = abs(end[0] - start[0]) // 2
        ry = abs(end[1] - start[1]) // 2
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2 - TOOLBAR_H
        if rx > 1 and ry > 1:
            pygame.draw.ellipse(canvas, draw_color,
                                (cx - rx, cy - ry, rx * 2, ry * 2), th)

    elif tool == 'square':
        pts = _canvas_pts(_square_points(start, end))
        if len(pts) >= 3:
            pygame.draw.polygon(canvas, draw_color, pts, th)

    elif tool == 'rtri':                        
        pts = _canvas_pts(_right_triangle_points(start, end))
        if len(pts) >= 3:
            pygame.draw.polygon(canvas, draw_color, pts, th)

    elif tool == 'etri':                       
        pts = _canvas_pts(_equilateral_triangle_points(start, end))
        if len(pts) >= 3:
            pygame.draw.polygon(canvas, draw_color, pts, th)

    elif tool == 'rhombus':                    
        pts = _canvas_pts(_rhombus_points(start, end))
        if len(pts) >= 3:
            pygame.draw.polygon(canvas, draw_color, pts, th)



def draw_line_between(canvas, index, start, end, width, draw_color, eraser):
    
    color = (0, 0, 0) if eraser else draw_color
    r     = width * 3  if eraser else width

    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy), 1)

    for i in range(iterations):
        t  = i / iterations
        x  = int((1 - t) * start[0] + t * end[0])
        y  = int((1 - t) * start[1] + t * end[1]) - TOOLBAR_H
        if y >= 0:
            pygame.draw.circle(canvas, color, (x, y), r)



def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Drawing App")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont(None, 18)   

    
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill((0, 0, 0))

    
    radius     = 8
    tool       = 'pen'
    draw_color = (100, 160, 255)
    points     = []          
    drag_start = None        

    
    DRAG_TOOLS = ('rect', 'circle', 'square', 'rtri', 'etri', 'rhombus')

    while True:
        pressed   = pygame.key.get_pressed()
        alt_held  = pressed[pygame.K_LALT]  or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        mx, my         = pygame.mouse.get_pos()
        mouse_on_canvas = my >= TOOLBAR_H    

        
        for event in pygame.event.get():

            
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_w and ctrl_held) or \
                   (event.key == pygame.K_F4 and alt_held) or \
                   event.key == pygame.K_ESCAPE:
                    return

                
                for key, tname in KEY_SHORTCUTS.items():
                    if event.key == key:
                        tool = tname

                
                if event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                    canvas.fill((0, 0, 0))

            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    radius = min(80, radius + 1)
                elif event.button == 5: 
                    radius = max(1, radius - 1)

                
                if event.button == 1 and my < TOOLBAR_H:
                    btn_w, btn_h = 64, 26
                    cols = 4
                    for i, t in enumerate(TOOLS):
                        col = i % cols
                        row = i // cols
                        bx  = 4 + col * (btn_w + 4)
                        by  = 4 + row * (btn_h + 4)
                        if bx <= mx <= bx + btn_w and by <= my <= by + btn_h:
                            tool = t

                    sw       = 22
                    px_start = 4 + cols * (btn_w + 4) + 8
                    for i, c in enumerate(PALETTE):
                        px = px_start + i * (sw + 3)
                        if px <= mx <= px + sw and 4 <= my <= 4 + sw:
                            draw_color = c
                            if tool == 'eraser':
                                tool = 'pen'    

            
                if event.button == 1 and mouse_on_canvas:
                    if tool in DRAG_TOOLS:
                        drag_start = (mx, my)
                    elif tool in ('pen', 'eraser'):
                        points = [(mx, my)]

            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drag_start and tool in DRAG_TOOLS:
                    commit_shape(canvas, tool, drag_start, (mx, my),
                                 draw_color, radius)
                    drag_start = None

            
            if event.type == pygame.MOUSEMOTION:
                if mouse_on_canvas and tool in ('pen', 'eraser'):
                    if pygame.mouse.get_pressed()[0]:
                        points.append((mx, my))
                        points = points[-512:]  

        
        if tool in ('pen', 'eraser') and len(points) >= 2:
            for i in range(len(points) - 1):
                draw_line_between(canvas, i, points[i], points[i + 1],
                                  radius, draw_color, tool == 'eraser')
            points = [points[-1]]   

        
        screen.fill((0, 0, 0))
        screen.blit(canvas, (0, TOOLBAR_H))     

        
        if drag_start and tool in DRAG_TOOLS:
            draw_preview(screen, tool, drag_start, (mx, my), draw_color, radius)

        
        if mouse_on_canvas:
            if tool == 'eraser':
                pygame.draw.circle(screen, (160, 160, 160), (mx, my), radius * 3, 1)
            else:
                pygame.draw.circle(screen, draw_color, (mx, my), radius, 1)

        draw_toolbar(screen, tool, draw_color, radius, font)
        pygame.display.flip()
        clock.tick(60)


main()
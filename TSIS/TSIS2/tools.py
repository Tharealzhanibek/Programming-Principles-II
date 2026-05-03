import math
from collections import deque
from datetime import datetime

import pygame

# Окно
WIDTH, HEIGHT = 1100, 720
TOOLBAR_HEIGHT = 130
CANVAS_Y = TOOLBAR_HEIGHT
CANVAS_WIDTH = WIDTH
CANVAS_HEIGHT = HEIGHT - TOOLBAR_HEIGHT

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
ORANGE = (255, 140, 0)

COLOR_OPTIONS = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE]
BRUSH_SIZES = {"small": 2, "medium": 5, "large": 10}
SIZE_ORDER = ["small", "medium", "large"]

#текст на экран
def draw_text(screen, text, x, y, font, color=BLACK):
    """Draw text on the given surface."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

#правильное строение фигур
def normalize_rect(start_pos, end_pos):
    """Convert two points into a normal pygame rectangle."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x1 - x2)
    height = abs(y1 - y2)
    return pygame.Rect(left, top, width, height)

#прямоугольник
def get_square_rect(start_pos, end_pos):
    """Build a square using the smaller dragged side."""
    x1, y1 = start_pos
    x2, y2 = end_pos

    side = min(abs(x2 - x1), abs(y2 - y1))
    left = x1 if x2 >= x1 else x1 - side
    top = y1 if y2 >= y1 else y1 - side

    return pygame.Rect(left, top, side, side)

#треугольник
def get_right_triangle_points(start_pos, end_pos):
    """Return points for a right triangle with legs parallel to axes."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    return [(x1, y1), (x1, y2), (x2, y2)]

#равностороний треугольник
def get_equilateral_triangle_points(start_pos, end_pos):
    """Build an equilateral triangle from dragged width."""
    x1, y1 = start_pos
    x2, y2 = end_pos

    side = abs(x2 - x1)
    if side == 0:
        side = 1

    height = (math.sqrt(3) / 2) * side

    if x2 >= x1:
        left_x = x1
        right_x = x1 + side
    else:
        left_x = x1 - side
        right_x = x1

    mid_x = (left_x + right_x) / 2

    if y2 >= y1:
        apex_y = y1 + height
        base_y = y1
    else:
        apex_y = y1 - height
        base_y = y1

    return [(left_x, base_y), (right_x, base_y), (mid_x, apex_y)]

#ромб
def get_rhombus_points(start_pos, end_pos):
    """Return rhombus points inside the dragged rectangle."""
    x1, y1 = start_pos
    x2, y2 = end_pos

    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)

    return [
        (center_x, top),
        (right, center_y),
        (center_x, bottom),
        (left, center_y),
    ]

#рисовка кружков между двумя точками
def draw_brush(surface, color, start, end, radius):
    """Draw a smooth freehand stroke by stamping circles along a segment."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    steps = max(abs(dx), abs(dy))

    if steps == 0:
        pygame.draw.circle(surface, color, start, radius)
        return

    for i in range(steps + 1):
        x = int(start[0] + dx * i / steps)
        y = int(start[1] + dy * i / steps)
        pygame.draw.circle(surface, color, (x, y), radius)

#заливка
def flood_fill(surface, start_pos, fill_color):
    """Fill an area using exact color matching with get_at and set_at."""
    width, height = surface.get_size()
    x, y = start_pos

    if not (0 <= x < width and 0 <= y < height):
        return

    target_color = surface.get_at((x, y))
    fill_color_rgba = pygame.Color(*fill_color)

    if target_color == fill_color_rgba:
        return

    queue = deque([(x, y)])

    while queue:
        px, py = queue.popleft()

        if px < 0 or px >= width or py < 0 or py >= height:
            continue
        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), fill_color)

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def clamp_to_canvas_screen(pos):
    """Keep mouse position inside the canvas area in screen coordinates."""
    x, y = pos
    x = max(0, min(WIDTH - 1, x))
    y = max(CANVAS_Y, min(HEIGHT - 1, y))
    return x, y


def screen_to_canvas(pos):
    """Convert a screen position to canvas-local coordinates."""
    x, y = pos
    return x, y - TOOLBAR_HEIGHT

#функции фигур
def draw_shape(surface, tool, color, start_pos, end_pos, thickness):
    """Draw the selected geometric shape on a surface."""
    if tool == "line":
        pygame.draw.line(surface, color, start_pos, end_pos, thickness)
    elif tool == "rectangle":
        rect = normalize_rect(start_pos, end_pos)
        pygame.draw.rect(surface, color, rect, thickness)
    elif tool == "circle":
        rect = normalize_rect(start_pos, end_pos)
        if rect.width > 0 and rect.height > 0:
            pygame.draw.ellipse(surface, color, rect, thickness)
    elif tool == "square":
        rect = get_square_rect(start_pos, end_pos)
        pygame.draw.rect(surface, color, rect, thickness)
    elif tool == "right_triangle":
        points = get_right_triangle_points(start_pos, end_pos)
        pygame.draw.polygon(surface, color, points, thickness)
    elif tool == "equilateral_triangle":
        points = get_equilateral_triangle_points(start_pos, end_pos)
        pygame.draw.polygon(surface, color, points, thickness)
    elif tool == "rhombus":
        points = get_rhombus_points(start_pos, end_pos)
        pygame.draw.polygon(surface, color, points, thickness)


def save_canvas(canvas):
    """Save the canvas as a PNG file with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"paint_{timestamp}.png"
    pygame.image.save(canvas, filename)
    return filename

#верхнее меню
def draw_toolbar(screen, current_tool, current_color, brush_size_name, brush_size_value, font, small_font):
    """Draw the toolbar and return clickable button rectangles."""
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    tools = [
        "pencil", "line", "fill", "text", "rectangle", "circle",
        "square", "right_triangle", "equilateral_triangle", "rhombus",
        "eraser", "clear",
    ]

    label_map = {
        "pencil": "Pencil",
        "line": "Line",
        "fill": "Fill",
        "text": "Text",
        "rectangle": "Rect",
        "circle": "Circle",
        "square": "Square",
        "right_triangle": "R-Tri",
        "equilateral_triangle": "E-Tri",
        "rhombus": "Rhombus",
        "eraser": "Eraser",
        "clear": "Clear",
    }

    tool_buttons = {}
    color_buttons = []
    size_buttons = {}

    button_w = 95
    button_h = 28
    gap = 7
    x = 10
    y = 8

    for tool in tools:
        rect = pygame.Rect(x, y, button_w, button_h)
        tool_buttons[tool] = rect

        selected = current_tool == tool
        button_color = DARK_GRAY if selected else WHITE
        text_color = WHITE if selected else BLACK

        pygame.draw.rect(screen, button_color, rect, border_radius=6)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
        draw_text(screen, label_map[tool], rect.x + 9, rect.y + 6, font, text_color)

        x += button_w + gap
        if x + button_w > WIDTH - 10:
            x = 10
            y += button_h + 8

    color_y = 78
    x = 12
    for color in COLOR_OPTIONS:
        rect = pygame.Rect(x, color_y, 32, 24)
        color_buttons.append((rect, color))
        pygame.draw.rect(screen, color, rect)
        border_width = 4 if color == current_color else 2
        pygame.draw.rect(screen, BLACK, rect, border_width)
        x += 40

    draw_text(screen, "Brush size:", 310, 81, font)

    size_x = 400
    for size_name in SIZE_ORDER:
        rect = pygame.Rect(size_x, 76, 90, 28)
        size_buttons[size_name] = rect
        selected = brush_size_name == size_name
        pygame.draw.rect(screen, DARK_GRAY if selected else WHITE, rect, border_radius=6)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
        label = f"{size_name.title()} ({BRUSH_SIZES[size_name]})"
        draw_text(screen, label, rect.x + 7, rect.y + 6, small_font, WHITE if selected else BLACK)
        size_x += 100

    help_text = (
        "Hotkeys: P pencil | L line | F fill | T text | E eraser | R rect | "
        "C circle | S square | G right tri | Q eq tri | H rhombus | 1/2/3 sizes | Ctrl+S save"
    )
    draw_text(screen, help_text, 10, 108, small_font, BLACK)
    draw_text(screen, f"Current size: {brush_size_value}px", 730, 81, font, BLACK)

    return tool_buttons, color_buttons, size_buttons
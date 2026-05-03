import pygame

from tools import (
    WIDTH,
    HEIGHT,
    TOOLBAR_HEIGHT,
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    WHITE,
    BLACK,
    BRUSH_SIZES,
    draw_text,
    draw_toolbar,
    draw_brush,
    draw_shape,
    flood_fill,
    clamp_to_canvas_screen,
    screen_to_canvas,
    save_canvas,
)


# -----------------------------------
# Main program
# -----------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSIS 2 Paint Application")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 16)
    small_font = pygame.font.SysFont("Arial", 13)
    text_font = pygame.font.SysFont("Arial", 28)

    # Холст для рис
    canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
    canvas.fill(WHITE)

    # Старт настройки
    current_tool = "pencil"
    current_color = BLACK
    brush_size_name = "medium"
    brush_size = BRUSH_SIZES[brush_size_name]

    drawing = False
    start_pos_screen = None
    preview_pos_screen = None
    last_canvas_pos = None

    # Text tool state
    text_mode = False
    text_position = None
    text_input = ""

    status_message = "Ready"
    running = True

    while running:
        screen.fill(WHITE)

        # Рис верх меню
        tool_buttons, color_buttons, size_buttons = draw_toolbar(
            screen,
            current_tool,
            current_color,
            brush_size_name,
            brush_size,
            font,
            small_font,
        )
        screen.blit(canvas, (0, TOOLBAR_HEIGHT)) #вывод рисунка на холсте
        draw_text(screen, status_message, 880, 108, small_font, BLACK)

        # превью текста
        if text_mode and text_position is not None:
            preview_surface = canvas.copy()
            text_preview = text_font.render(text_input + "|", True, current_color)
            preview_surface.blit(text_preview, text_position)
            screen.blit(preview_surface, (0, TOOLBAR_HEIGHT))

        # превью фигур
        if drawing and current_tool in {
            "line", "rectangle", "circle", "square",
            "right_triangle", "equilateral_triangle", "rhombus"
        } and start_pos_screen and preview_pos_screen:
            temp_canvas = canvas.copy()
            draw_shape(
                temp_canvas,
                current_tool,
                current_color,
                screen_to_canvas(start_pos_screen),
                screen_to_canvas(preview_pos_screen),
                brush_size,
            )
            screen.blit(temp_canvas, (0, TOOLBAR_HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                # сохранение
                if mods & pygame.KMOD_CTRL and event.key == pygame.K_s:
                    filename = save_canvas(canvas)
                    status_message = f"Saved: {filename}"
                    continue

                # для текста
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        if text_input.strip() and text_position is not None:
                            final_text = text_font.render(text_input, True, current_color)
                            canvas.blit(final_text, text_position)
                            status_message = "Text placed"
                        else:
                            status_message = "Empty text cancelled"

                        text_mode = False
                        text_position = None
                        text_input = ""

                    elif event.key == pygame.K_ESCAPE:
                        text_mode = False
                        text_position = None
                        text_input = ""
                        status_message = "Text cancelled"

                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]

                    else:
                        if event.unicode.isprintable():
                            text_input += event.unicode
                    continue

                # горячие клавиши
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    current_tool = "pencil"
                elif event.key == pygame.K_l:
                    current_tool = "line"
                elif event.key == pygame.K_f:
                    current_tool = "fill"
                elif event.key == pygame.K_t:
                    current_tool = "text"
                elif event.key == pygame.K_r:
                    current_tool = "rectangle"
                elif event.key == pygame.K_c:
                    current_tool = "circle"
                elif event.key == pygame.K_s:
                    current_tool = "square"
                elif event.key == pygame.K_g:
                    current_tool = "right_triangle"
                elif event.key == pygame.K_q:
                    current_tool = "equilateral_triangle"
                elif event.key == pygame.K_h:
                    current_tool = "rhombus"
                elif event.key == pygame.K_e:
                    current_tool = "eraser"
                elif event.key == pygame.K_1:
                    brush_size_name = "small"
                    brush_size = BRUSH_SIZES[brush_size_name]
                elif event.key == pygame.K_2:
                    brush_size_name = "medium"
                    brush_size = BRUSH_SIZES[brush_size_name]
                elif event.key == pygame.K_3:
                    brush_size_name = "large"
                    brush_size = BRUSH_SIZES[brush_size_name]

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # нажатие на элементы
                if my < TOOLBAR_HEIGHT:
                    for tool, rect in tool_buttons.items():
                        if rect.collidepoint(event.pos):
                            if tool == "clear":
                                canvas.fill(WHITE)
                                status_message = "Canvas cleared"
                            else:
                                current_tool = tool
                                status_message = f"Tool: {tool}"

                    for rect, color in color_buttons:
                        if rect.collidepoint(event.pos):
                            current_color = color
                            status_message = "Color changed"

                    for size_name, rect in size_buttons.items():
                        if rect.collidepoint(event.pos):
                            brush_size_name = size_name
                            brush_size = BRUSH_SIZES[brush_size_name]
                            status_message = f"Brush size: {brush_size}px"

                # нажатие на холст
                else:
                    canvas_pos = screen_to_canvas(clamp_to_canvas_screen(event.pos))

                    if current_tool == "fill":
                        flood_fill(canvas, canvas_pos, current_color)
                        status_message = "Area filled"

                    elif current_tool == "text":
                        text_mode = True
                        text_position = canvas_pos
                        text_input = ""
                        status_message = "Typing text... Enter to confirm"

                    else:
                        drawing = True
                        start_pos_screen = clamp_to_canvas_screen(event.pos)
                        preview_pos_screen = start_pos_screen
                        last_canvas_pos = canvas_pos

                        if current_tool == "pencil":
                            pygame.draw.circle(canvas, current_color, canvas_pos, brush_size)
                        elif current_tool == "eraser":
                            pygame.draw.circle(canvas, WHITE, canvas_pos, brush_size)

            elif event.type == pygame.MOUSEMOTION and drawing:
                preview_pos_screen = clamp_to_canvas_screen(event.pos)
                current_canvas_pos = screen_to_canvas(preview_pos_screen)

                # свободное рисование либо стирание
                if current_tool == "pencil":
                    draw_brush(canvas, current_color, last_canvas_pos, current_canvas_pos, brush_size)
                    last_canvas_pos = current_canvas_pos
                elif current_tool == "eraser":
                    draw_brush(canvas, WHITE, last_canvas_pos, current_canvas_pos, brush_size)
                    last_canvas_pos = current_canvas_pos

            elif event.type == pygame.MOUSEBUTTONUP and drawing:
                end_pos_screen = clamp_to_canvas_screen(event.pos)

                # после отпускания мышки
                if current_tool in {
                    "line", "rectangle", "circle", "square",
                    "right_triangle", "equilateral_triangle", "rhombus"
                }:
                    draw_shape(
                        canvas,
                        current_tool,
                        current_color,
                        screen_to_canvas(start_pos_screen),
                        screen_to_canvas(end_pos_screen),
                        brush_size,
                    )

                drawing = False
                start_pos_screen = None
                preview_pos_screen = None
                last_canvas_pos = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
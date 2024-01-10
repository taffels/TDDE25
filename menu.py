import pygame
import images
import maps

pygame.init()
pygame.display.set_mode()
screen = pygame.display.set_mode((480, 200))


def main_menu_screen(screen=pygame.display.set_mode((480, 200))):
    """A function that displays the main menu screen"""
    menu_screen = images.main_menu1
    screen.fill((0, 0, 0))
    screen.blit(menu_screen, (0, 0))
    pygame.display.update()


def map_select_screen(
        select_marker, screen=pygame.display.set_mode((800, 452))):
    """A function that displays the map select screen"""
    # Menu image
    menu_screen = images.map_selection
    screen.fill((100, 100, 100))
    screen.blit(menu_screen, (0, 0))
    # Map selection
    if select_marker == 1:
        map1_icon = images.map1_icon
        screen.blit(map1_icon, (400, 125))
    elif select_marker == 2:
        map2_icon = images.map2_icon
        screen.blit(map2_icon, (400, 150))
    elif select_marker == 3:
        map3_icon = images.map3_icon
        screen.blit(map3_icon, (400, 195))
    elif select_marker == 4:
        map4_icon = images.map4_icon
        screen.blit(map4_icon, (400, 245))
    # Text
    font = pygame.font.Font(None, 80)
    font_outline = pygame.font.Font(None, 80)
    marker_text = ">"
    map1_text = "Map 1"
    map2_text = "Map 2"
    map3_text = "Map 3"
    map4_text = "Map 4"
    # Colors
    text_color = (255, 63, 43)
    outline_color = (0, 0, 0)
    # Marker text
    marker = font.render(marker_text, True, (255, 0, 0))
    marker_outline = font.render(marker_text, True, outline_color)
    # Maps text
    map1 = font.render(map1_text, True, text_color)
    map2 = font.render(map2_text, True, text_color)
    map3 = font.render(map3_text, True, text_color)
    map4 = font.render(map4_text, True, text_color)
    map1_outline = font_outline.render(map1_text, True, outline_color)
    map2_outline = font_outline.render(map2_text, True, outline_color)
    map3_outline = font_outline.render(map3_text, True, outline_color)
    map4_outline = font_outline.render(map4_text, True, outline_color)
    select_marker *= 100  # Pointing marker position
    # Rendering the outline of the text
    screen.blit(map1_outline, (200, 98))
    screen.blit(map2_outline, (200, 198))
    screen.blit(map3_outline, (200, 298))
    screen.blit(map4_outline, (200, 398))
    screen.blit(map1_outline, (200, 102))
    screen.blit(map2_outline, (200, 202))
    screen.blit(map3_outline, (200, 302))
    screen.blit(map4_outline, (200, 402))
    screen.blit(map1_outline, (202, 100))
    screen.blit(map2_outline, (202, 200))
    screen.blit(map3_outline, (202, 300))
    screen.blit(map4_outline, (202, 400))
    screen.blit(map1_outline, (198, 100))
    screen.blit(map2_outline, (198, 200))
    screen.blit(map3_outline, (198, 300))
    screen.blit(map4_outline, (198, 400))
    # Outline of the marker
    screen.blit(marker_outline, (150, select_marker - 2))
    screen.blit(marker_outline, (150, select_marker + 2))
    screen.blit(marker_outline, (148, select_marker))
    screen.blit(marker_outline, (152, select_marker))
    # Loads the maps text and the pointing marker
    screen.blit(marker, (150, select_marker))
    screen.blit(map1, (200, 100))
    screen.blit(map2, (200, 200))
    screen.blit(map3, (200, 300))
    screen.blit(map4, (200, 400))

    pygame.display.update()


def menu_state(game_state):
    """A function that keeps track of the game state and calls the appropriate menu screen"""
    current_map = 0
    game_mode = "single_player"
    # Run game from main menu
    while game_state != "quit" and game_state != "game_time":
        if game_state == "main menu":
            game_mode, game_state = run_main_menu(game_state)
        if game_state == "map select":
            game_mode, current_map, game_state = run_map_select(
                game_state, game_mode)
    return game_mode, current_map, game_state


def run_main_menu(game_state):
    """Function for displaying main menu and choosing game mode"""
    # print("entered main menu")
    main_menu_selection = ["singleplayer", "multiplayer", "quit"]
    index_select = 0
    current_select = main_menu_selection[index_select]
    game_mode = None
    main_menu_screen(screen=pygame.display.set_mode((480, 200)))
    while game_state == "main menu":
        # Main menu
        for event in pygame.event.get():
            # print("current game mode select: ", main_menu_selection[index_select])
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "quit"
                if event.key == pygame.K_UP:
                    if index_select == 0:
                        index_select = 2
                    else:
                        index_select -= 1
                    current_select = main_menu_selection[index_select]

                if event.key == pygame.K_DOWN:
                    if index_select == 2:
                        index_select = 0
                    else:
                        index_select += 1
                    current_select = main_menu_selection[index_select]
                if current_select == "singleplayer":  # index 0
                    screen.blit(images.main_menu1, (0, 0))
                    pygame.display.update()

                if current_select == "multiplayer":  # index 1
                    screen.blit(images.main_menu2, (0, 0))
                    pygame.display.update()

                if current_select == "quit":  # index 2
                    screen.blit(images.main_menu3, (0, 0))
                    pygame.display.update()

                if event.key == pygame.K_RETURN:
                    # print(current_select)
                    if current_select == "quit":
                        game_state = "quit"
                    else:
                        game_mode = current_select
                        game_state = "map select"
                        # print("continuing with map:", game_state, "and game mode: ",game_mode)
                    return game_mode, game_state

    # Mapselector


def run_map_select(game_state, game_mode):
    """A function that calls to display the map select screen and lets the user decide the map"""
    current_map = 0
    select_map = 0
    map_select_screen(select_map + 1, screen=pygame.display.set_mode((800, 456)))
    # Keyboard choose map
    while game_state == "map select":
        map_select_screen(select_map + 1)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Goes back to main menu
                    game_state = "main menu"
                if event.key == pygame.K_DOWN:
                    select_map += 1
                    if select_map > 3:
                        select_map = 0
                elif event.key == pygame.K_UP:
                    select_map -= 1
                    if select_map < 0:
                        select_map = 3
                elif event.key == pygame.K_RETURN:  # Select map
                    if select_map == 0:
                        current_map = maps.map0
                    elif select_map == 1:
                        current_map = maps.map1
                    elif select_map == 2:
                        current_map = maps.map2
                    elif select_map == 3:
                        current_map = maps.map3
                    game_state = "game_time"
    return game_mode, current_map, game_state

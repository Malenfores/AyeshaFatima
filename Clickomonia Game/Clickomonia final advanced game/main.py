from theme_manager import ThemeManager
import pygame
import sys

from settings import *
from menu import Menu
from difficulty import DifficultyManager
from game import Game
from ui import UI
from player_manager import PlayerManager
from portal_effect import MagicPortalEffect

# ==========================================
# INITIALIZATION
# ==========================================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption(
    "Candy Clickomania Deluxe"
)

clock = pygame.time.Clock()

menu = Menu()

difficulty = DifficultyManager()

game = Game(difficulty)

ui = UI()
theme_manager = ThemeManager()
player_manager = PlayerManager()
magic_fx = MagicPortalEffect(duration_ms=WAND_ANIMATION_DURATION)

state = MENU
player_name = ""
name_input = ""
ENTER_NAME = 99
running = True

# ==========================================
# END SCREEN (GAME OVER / WIN)
# ==========================================

def draw_end_screen(screen, title, title_color, score, pdata):

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("arial", 72, True)
    big_font = pygame.font.SysFont("arial", 40, True)

    lines = [
        (title, title_font, title_color),
        (f"Player : {player_name}", big_font, WHITE),
        (f"Score : {score}", big_font, WHITE),
        (f"Best Score : {pdata['high_score']}", big_font, WHITE),
        (f"Games Played : {pdata['games_played']}", big_font, WHITE),
        (f"Wins : {pdata['games_won']}", big_font, WHITE),
        (f"Losses : {pdata['games_lost']}", big_font, WHITE),
    ]

    start_y = 110
    step_y = 70

    for i, (text, font, color) in enumerate(lines):
        img = font.render(text, True, color)
        screen.blit(img, img.get_rect(center=(WIDTH // 2, start_y + i * step_y)))

    info = big_font.render("Click Anywhere To Return", True, (255, 255, 0))
    screen.blit(
        info,
        info.get_rect(center=(WIDTH // 2, start_y + len(lines) * step_y + 30))
    )

# ==========================================
# PLAYER RECORDS SCREEN
# ==========================================

def draw_records_screen(screen, players):

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(230)
    overlay.fill((15, 15, 30))
    screen.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("arial", 55, True)
    header_font = pygame.font.SysFont("arial", 26, True)
    row_font = pygame.font.SysFont("arial", 24)
    small_font = pygame.font.SysFont("arial", 22)

    title = title_font.render("PLAYER RECORDS", True, (255, 220, 50))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    if not players:

        empty = row_font.render(
            "No players yet. Play a game to create a record!",
            True,
            WHITE
        )
        screen.blit(empty, (WIDTH // 2 - empty.get_width() // 2, 200))

    else:

        # Sort players by high_score, descending
        sorted_players = sorted(
            players.items(),
            key=lambda item: item[1].get("high_score", 0),
            reverse=True
        )

        top_name, top_data = sorted_players[0]

        crown_text = f"TOP PLAYER : {top_name}  (High Score : {top_data.get('high_score', 0)})"
        crown = header_font.render(crown_text, True, (255, 215, 0))
        screen.blit(crown, (WIDTH // 2 - crown.get_width() // 2, 100))

        # Table header
        col_x = [110, 430, 630, 830, 1030]
        headers = ["PLAYER", "HIGH SCORE", "PLAYED", "WINS", "LOSSES"]

        header_y = 160

        pygame.draw.rect(
            screen,
            (40, 40, 70),
            (60, header_y - 8, WIDTH - 120, 40),
            border_radius=8
        )

        for x, h in zip(col_x, headers):
            label = header_font.render(h, True, (200, 200, 255))
            screen.blit(label, (x, header_y))

        row_y = header_y + 50
        row_height = 42

        for i, (name, data) in enumerate(sorted_players):

            if row_y > HEIGHT - 60:
                more = small_font.render(
                    f"... and {len(sorted_players) - i} more",
                    True,
                    (180, 180, 180)
                )
                screen.blit(more, (110, row_y))
                break

            is_top = (name == top_name)
            row_color = (255, 215, 0) if is_top else WHITE

            if is_top:
                pygame.draw.rect(
                    screen,
                    (60, 50, 20),
                    (60, row_y - 6, WIDTH - 120, row_height),
                    border_radius=6
                )

            display_name = ("* " + name) if is_top else name

            values = [
                display_name,
                str(data.get("high_score", 0)),
                str(data.get("games_played", 0)),
                str(data.get("games_won", 0)),
                str(data.get("games_lost", 0)),
            ]

            for x, v in zip(col_x, values):
                cell = row_font.render(v, True, row_color)
                screen.blit(cell, (x, row_y))

            row_y += row_height

    back_text = row_font.render(
        "Click Anywhere Or Press ESC To Return",
        True,
        (255, 255, 0)
    )
    screen.blit(
        back_text,
        (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 45)
    )

# ==========================================
# MAIN LOOP
# ==========================================

while running:

    theme_manager.draw_background(screen, pygame.time.get_ticks())

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # ==========================================
    # EVENTS
    # ==========================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()

            sys.exit()

        # ==========================
        # Keyboard
        # ==========================

        if event.type == pygame.KEYDOWN:

            if state == ENTER_NAME:
                if event.key == pygame.K_RETURN and name_input.strip():
                    player_name = name_input.strip()
                    state = PLAYING
                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                else:
                    if hasattr(event,"unicode") and event.unicode.isprintable():
                        name_input += event.unicode

            if state == PLAYING:

                if event.key == pygame.K_p:

                    game.toggle_pause()

                elif event.key == pygame.K_h:

                    game.find_hint()

                elif event.key == pygame.K_s:

                    game.shuffle_board()

                elif event.key == pygame.K_r:

                    game.reset()

                elif event.key == pygame.K_ESCAPE:

                    state = MENU

            elif state == RECORDS:

                if event.key == pygame.K_ESCAPE:

                    state = MENU

        # ==========================
        # Mouse
        # ==========================

        if event.type == pygame.MOUSEBUTTONDOWN:

            x, y = event.pos

            # ==========================
            # MENU
            # ==========================

            if state == MENU:

                if menu.start_button.collidepoint(x, y):

                    game.reset()

                    state = ENTER_NAME

                elif menu.difficulty_button.collidepoint(x, y):

                    state = DIFFICULTY

                elif menu.records_button.collidepoint(x, y):

                    player_manager.load()

                    state = RECORDS

                elif menu.exit_button.collidepoint(x, y):

                    pygame.quit()

                    sys.exit()

            # ==========================
            # RECORDS
            # ==========================

            elif state == RECORDS:

                state = MENU

            # ==========================
            # DIFFICULTY
            # ==========================

            elif state == DIFFICULTY:

                if difficulty.easy_button.collidepoint(x, y):

                    difficulty.set_mode("Easy")

                    game = Game(difficulty)

                    state = MENU

                elif difficulty.medium_button.collidepoint(x, y):

                    difficulty.set_mode("Medium")

                    game = Game(difficulty)

                    state = MENU

                elif difficulty.hard_button.collidepoint(x, y):

                    difficulty.set_mode("Hard")

                    game = Game(difficulty)

                    state = MENU

                elif difficulty.back_button.collidepoint(x, y):

                    state = MENU

            # ==========================
            # PLAYING
            # ==========================

            elif state == PLAYING:

                # While the magic portal animation is playing, ignore all
                # clicks so the board can't be touched mid-conjure
                if game.is_wand_active():
                    continue

                # ----------------------
                # RESUME BUTTON
                # ----------------------
                if game.is_paused():

                    if ui.resume_button.collidepoint(x, y):

                        game.toggle_pause()

                    continue

                # Pause Button
                if ui.pause_button.collidepoint(x, y):

                    game.toggle_pause()

                # Shuffle Button
                elif ui.shuffle_button.collidepoint(x, y):

                    game.shuffle_board()

                # Hint Button
                elif ui.hint_button.collidepoint(x, y):

                    game.find_hint()

                # Restart Button
                elif ui.restart_button.collidepoint(x, y):

                    game.reset()
                elif ui.mute_button.collidepoint(x,y):
                    game.sound_manager.toggle_mute()
                elif ui.wand_button.collidepoint(x,y):
                    if game.can_use_wand():
                        game.use_magic_wand()
                        if game.is_wand_active():
                            magic_fx.activate(screen, mode=game.wand_mode())
                elif ui.theme_button.collidepoint(x,y):
                    theme_manager.next_theme()

                # Quit Button
                elif ui.quit_button.collidepoint(x, y):

                    state = MENU

                else:

                    board_width = COLS * CELL_SIZE

                    board_height = ROWS * CELL_SIZE

                    if (

                        BOARD_X <= x < BOARD_X + board_width

                        and

                        BOARD_Y <= y < BOARD_Y + board_height

                    ):

                        col = (

                            x - BOARD_X

                        ) // CELL_SIZE

                        row = (

                            y - BOARD_Y

                        ) // CELL_SIZE

                        game.handle_click(

                            row,

                            col

                        )

            # ==========================
            # GAME OVER
            # ==========================

            elif state == GAME_OVER:

                if event.button == 1:
                    state = MENU
                    game.reset()
                    name_input = ""


            # ==========================
            # WIN
            # ==========================

            elif state == WIN:

                game.reset()

                state = MENU

    # ==========================================
    # HOVER HIGHLIGHT
    # ==========================================

    if state == PLAYING:

        board_width = COLS * CELL_SIZE

        board_height = ROWS * CELL_SIZE

        if (

            BOARD_X <= mouse_x < BOARD_X + board_width

            and

            BOARD_Y <= mouse_y < BOARD_Y + board_height

        ):

            col = (

                mouse_x - BOARD_X

            ) // CELL_SIZE

            row = (

                mouse_y - BOARD_Y

            ) // CELL_SIZE

            game.board.highlight_group(

                row,

                col

            )

        else:

            game.board.clear_selection()

    # ==========================================
    # UPDATE
    # ==========================================

    if state == PLAYING:

        if game.is_wand_active():

            # Hold the board still while the portal conjures the result;
            # once the 3-second animation completes, reveal it and let the
            # normal win/game-over checks below transition the screen.
            if magic_fx.is_finished():

                game.finish_wand()

                magic_fx.deactivate()

        elif not game.is_paused():

            game.update()

        if game.is_win():

            player_manager.update(player_name, game.get_score(), True)
            state = WIN

        elif game.is_game_over():

            player_manager.update(player_name, game.get_score(), False)
            state = GAME_OVER

    # ==========================================
    # DRAW
    # ==========================================

    if state == MENU:

        menu.draw(

            screen,

            game.get_high_score()

        )

    elif state == DIFFICULTY:

        difficulty.draw(screen)

    elif state == RECORDS:

        draw_records_screen(screen, player_manager.players)

    elif state == PLAYING:

        game.draw(screen)

        ui.draw_hud(

            screen,

            game.get_score(),

            game.get_high_score(),

            difficulty.get_mode(),

            game.get_time_left(),

            wand_enabled=game.can_use_wand(),

            wand_glow_elapsed=game.wand_glow_elapsed()

        )
        
        screen.blit(pygame.font.SysFont("arial",24).render("Theme: "+theme_manager.name(),True,WHITE),(950,700))
        
        notif = game.get_wand_notification()
        if notif and not game.is_wand_active():
            ui.draw_wand_notification(screen, notif["text"], notif["elapsed"], notif["duration"])
        
        if (not game.is_wand_active()) and pygame.time.get_ticks() < getattr(game,"wand_message_timer",0):
            f=pygame.font.SysFont("arial",48,bold=True)
            t=f.render("MAGIC WAND ACTIVATED!",True,(255,255,0))
            screen.blit(t,(WIDTH//2-t.get_width()//2,10))

        # Draw Hint
        for row, col in game.get_hint():

            pygame.draw.rect(

                screen,

                WHITE,

                (

                    BOARD_X + col * CELL_SIZE,

                    BOARD_Y + row * CELL_SIZE,

                    CELL_SIZE,

                    CELL_SIZE

                ),

                3

            )

        # Pause Overlay
        if game.is_paused():

            ui.draw_pause_screen(screen)

        # Magic Wand portal animation (drawn last so it covers everything
        # else on screen while the result is being "conjured")
        if game.is_wand_active():

            magic_fx.draw(screen)

    # ==========================================
    # GAME OVER
    # ==========================================

    elif state == ENTER_NAME:

        screen.fill((20,20,40))
        f=pygame.font.SysFont("arial",60,True)
        screen.blit(f.render("Enter Your Name",True,WHITE),(420,180))
        box=pygame.Rect(390,300,500,60)
        pygame.draw.rect(screen,WHITE,box,2)
        t=pygame.font.SysFont("arial",40).render(name_input,True,WHITE)
        screen.blit(t,(box.x+10,box.y+10))

    elif state == GAME_OVER:

        pdata = player_manager.get_player(player_name)

        if getattr(game, "ended_by_wand", False):

            end_title = "GAME END"
            end_color = (200, 120, 255)

        else:

            end_title = "GAME OVER"
            end_color = (255, 80, 80)

        draw_end_screen(
            screen,
            end_title,
            end_color,
            game.get_score(),
            pdata
        )

    # ==========================================
    # WIN
    # ==========================================

    elif state == WIN:

        pdata = player_manager.get_player(player_name)

        draw_end_screen(
            screen,
            "YOU WIN!",
            (80, 255, 120),
            game.get_score(),
            pdata
        )

    # ==========================================
    # DISPLAY
    # ==========================================

    pygame.display.flip()

    clock.tick(FPS)

# ==========================================
# EXIT
# ==========================================

pygame.quit()

sys.exit()
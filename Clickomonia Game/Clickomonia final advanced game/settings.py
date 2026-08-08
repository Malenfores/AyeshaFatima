# ===========================================
# WINDOW SETTINGS
# ===========================================

WIDTH = 1280
HEIGHT = 720
FPS = 60

TITLE = "Candy Clickomania Deluxe"

# ===========================================
# BOARD SETTINGS
# ===========================================

ROWS = 10
COLS = 10

# Ball Size
CELL_SIZE = 60

# Board Position
BOARD_X = 40
BOARD_Y = 60

BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE

# ===========================================
# GAME SETTINGS
# ===========================================

TARGET_SCORE = 5000
MIN_GROUP_SIZE = 2

ANIMATION_SPEED = 12
PARTICLE_COUNT = 15

SHOW_HINT_TIME = 5

# How long the full-screen magic portal animation plays (ms) before the
# Magic Wand's actual result is revealed.
WAND_ANIMATION_DURATION = 3000

# Group size thresholds for a "nice pop" celebration animation
NICE_POP_SIZE = 6
AWESOME_POP_SIZE = 10

# ===========================================
# SOUND SETTINGS
# ===========================================

MUSIC_VOLUME = 0.40
SOUND_VOLUME = 0.70

# ===========================================
# COLORS
# ===========================================

WHITE = (255,255,255)
BLACK = (0,0,0)

RED = (255,60,60)
GREEN = (50,220,120)
BLUE = (60,120,255)
YELLOW = (255,220,0)

GRAY = (120,120,120)

BACKGROUND = (55,10,40)

HUD_COLOR = (35,35,35)

BUTTON_COLOR = (255,120,60)

BUTTON_HOVER = (255,170,90)

# ===========================================
# CANDY COLORS
# ===========================================

CANDY_COLORS = [

    (255,80,80),      # Red
    (80,120,255),     # Blue
    (80,220,120),     # Green
    (255,220,50),     # Yellow
    (220,80,255),     # Purple
    (255,140,50),     # Orange
    (0,255,255),      # Cyan
    (255,105,180)     # Pink

]

# ===========================================
# GAME STATES
# ===========================================

MENU = 0
DIFFICULTY = 1
PLAYING = 2
PAUSED = 3
GAME_OVER = 4
WIN = 5
RECORDS = 6

# ===========================================
# FONTS
# ===========================================

TITLE_FONT_SIZE = 54
MENU_FONT_SIZE = 38
HUD_FONT_SIZE = 28
SMALL_FONT_SIZE = 22
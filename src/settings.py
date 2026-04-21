
# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Elemental Tower Defense"

# UI
UI_BAR_HEIGHT  = 110          # bottom HUD bar
GAME_HEIGHT    = SCREEN_HEIGHT - UI_BAR_HEIGHT   # 610px playfield

# Colors
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (100, 100, 100)
DARK_GRAY  = (40,  40,  40)
MID_GRAY   = (60,  60,  60)
LIGHT_GRAY = (180, 180, 180)
GREEN      = (34,  139, 34)
DARK_GREEN = (20,  90,  20)
RED        = (220, 50,  50)
BLUE       = (50,  100, 220)
YELLOW     = (255, 215, 0)
GOLD       = (212, 175, 55)
ORANGE     = (210, 120, 30)
BROWN      = (101, 67,  33)
ICE        = (160,220,255)

# Grid
TILE_SIZE = 64
COLS = SCREEN_WIDTH // TILE_SIZE          # 20
ROWS = GAME_HEIGHT  // TILE_SIZE          # 9

# Player
STARTING_MONEY = 9100
STARTING_LIVES = 10

# Tower slot bar
TOWER_SLOTS     = 10
SLOT_SIZE       = 80
SLOT_PADDING    = 8

# Waves
TIME_BETWEEN_WAVES = 15        # seconds between end of one wave and start of next

# Default level to load on startup
DEFAULT_LEVEL = "levels/level_1.json"

# Projectiles
PROJECTILE_SPEED  = 300    # pixels per second (same for all towers)
PROJECTILE_RADIUS = 5      # pixels

# Element colors (used for upgrade screen slots)
ELEMENT_COLORS = {
    "earth":  (101, 67,  33),
    "fire":   (210, 120, 30),
    "water":  (50,  100, 220),
    "wind":   (180, 180, 180),
    "spirit": (180, 100, 255),
}
ELEMENT_NAMES = ["earth", "fire", "water", "wind", "spirit"]

# Upgrade costs per level (index = upgrading TO this level, e.g. index 2 = cost to reach level 2)
# Element upgrade cost: UPGRADE_COST_BASE * new_level
UPGRADE_COST_BASE     = 15    # cost multiplier per level
# Tower level-up cost: TOWER_LEVELUP_COST * new_level
TOWER_LEVELUP_COST    = 40
 
# Upgrade effects per level gained
UPGRADE_DAMAGE_PER_LEVEL      = 5     # earth: +damage per element level
UPGRADE_FIRE_RATE_PER_LEVEL   = 0.3   # water: +firing_rate per element level
UPGRADE_RANGE_PER_LEVEL       = 1     # wind:  +range (tiles) per element level
UPGRADE_CRIT_PER_LEVEL        = 0.05  # spirit: +cit_rate per element level
UPGRADE_DOT_PER_LEVEL         = 2     # fire: +dot damage per element level

# Damage over time
DOT_TICK_INTERVAL = 3.0    # seconds between DOT ticks
DOT_DURATION      = 10.0   # total seconds DOT lasts

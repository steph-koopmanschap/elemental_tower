
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
STARTING_MONEY = 100
STARTING_LIVES = 10

# Tower slot bar
TOWER_SLOTS     = 10
SLOT_SIZE       = 80
SLOT_PADDING    = 8

# Tower definitions  { id, name, cost, damage, description, color, unlocked }
TOWER_DEFS = [
    {
        "id": "earth", "name": "Earth Tower", "cost": 10, "damage": 5,
        "description": "A sturdy tower made of rock and soil. Slow but reliable. Good for early waves.",
        "color": BROWN, "unlocked": True,
    },
    {
        "id": "fire", "name": "Fire Tower", "cost": 25, "damage": 15,
        "description": "Burns enemies with intense heat. High damage but costs more to build.",
        "color": ORANGE, "unlocked": True,
    },
    {
        "id": "water", "name": "Water Tower", "cost": 20, "damage": 10,
        "description": "Slows enemies with a torrent of water while dealing moderate damage.",
        "color": BLUE, "unlocked": True,
    },
    {
        "id": "wind", "name": "Wind Tower", "cost": 30, "damage": 12,
        "description": "Pushes enemies back with gale-force blasts. Can hit multiple targets.",
        "color": LIGHT_GRAY, "unlocked": True,
    },
    {
        "id": "ice", "name": "Ice Tower", "cost": 35, "damage": 8,
        "description": "Freezes enemies solid. Low damage but hard-freezes targets in place.",
        "color": ICE, "unlocked": True,
    },
    {"id": "t6",  "name": "???", "cost": 0, "damage": 0, "description": "Not yet discovered.", "color": GRAY, "unlocked": False},
    {"id": "t7",  "name": "???", "cost": 0, "damage": 0, "description": "Not yet discovered.", "color": GRAY, "unlocked": False},
    {"id": "t8",  "name": "???", "cost": 0, "damage": 0, "description": "Not yet discovered.", "color": GRAY, "unlocked": False},
    {"id": "t9",  "name": "???", "cost": 0, "damage": 0, "description": "Not yet discovered.", "color": GRAY, "unlocked": False},
    {"id": "t10", "name": "???", "cost": 0, "damage": 0, "description": "Not yet discovered.", "color": GRAY, "unlocked": False},
]

"""
config.py
Central constants for the Snake – Advanced Edition game.
Import this module anywhere rather than hard-coding magic numbers.
"""
import os

CELL          = 10              
SCREEN_WIDTH  = 720
SCREEN_HEIGHT = 480
COLS          = SCREEN_WIDTH  // CELL   
ROWS          = SCREEN_HEIGHT // CELL    
RENDER_FPS    = 60

BASE_STEPS    = 8               
STEPS_PER_LVL = 2               
FOODS_PER_LVL = 5               

PU_FIELD_MS   = 8_000           
PU_EFFECT_MS  = 5_000           
PU_SPAWN_MS   = 20_000          

POISON_FIELD_MS = 6_000         
POISON_SPAWN_MS = 12_000        

OBS_START_LEVEL = 3             
OBS_BASE_COUNT  = 4             
OBS_PER_LEVEL   = 2             
OBS_MIN_REACH   = 30            

BLACK    = (0,   0,   0)
WHITE    = (255, 255, 255)
GREY     = (50,  50,  50)
RED      = (220, 50,  50)
GREEN    = (0,   200, 0)
BLUE     = (40,  140, 255)
YELLOW   = (255, 220, 40)
ORANGE   = (255, 140, 0)
SILVER   = (192, 192, 192)
GOLD     = (255, 215, 0)
POISON_C = (140, 0,   30)       
OBS_C    = (90,  95,  120)      
GRID_LN  = (22,  22,  28)       

SNAKE_COLOR_PRESETS = [
    [0,   200, 0],              
    [40,  140, 255],            
    [255, 220, 40],             
    [255, 140, 0],              
    [80,  220, 220],            
    [160, 80,  255],            
]

FOOD_TYPES = [
    {"value": 5,  "color": WHITE,  "weight": 60, "lifetime_ms": 8_000, "label": "common"},
    {"value": 15, "color": SILVER, "weight": 25, "lifetime_ms": 5_000, "label": "rare"},
    {"value": 30, "color": GOLD,   "weight": 10, "lifetime_ms": 3_000, "label": "epic"},
    {"value": 50, "color": ORANGE, "weight": 5,  "lifetime_ms": 2_000, "label": "legendary"},
]

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME",     "snake_game"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "5432")),
}

SETTINGS_FILE    = "settings.json"
DEFAULT_SETTINGS = {
    "snake_color": [0, 200, 0],     
    "grid":        False,           
    "sound":       True,            
}

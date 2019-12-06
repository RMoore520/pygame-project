#game options/settings
TITLE = "The Big Yeet"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'comic sans'
HS_FILE = 'highscore.txt'
SPRITESHEET = "spritesheet_jumper.png"

#Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_GRAV_SPACE = 0.6
PLAYER_JUMP = 22

#Game properties
BOOST_POWER = 60
POW_SPAWN_PCT = 7
CLOUD_LAYER = 0
PLATFORM_LAYER = 1
POW_LAYER = 1
PLAYER_LAYER = 2
MOB_LAYER = 2

#Startng platforms
PLATFORM_LIST = [(0, HEIGHT - 60),
                (WIDTH / 2 - 50, HEIGHT * 3 / 4 - 50),
                (125, HEIGHT - 350),
                (350, 200),
                (175, 100)]

# Main Color RGB Values
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

DARKESTBLUE = (0, 25, 152)
DARKERBLUE = (19, 61, 145)
DARKBLUE = (19, 90, 183)
LIGHTBLUE = (26, 107, 213)
SKYBLUE = (43, 210, 229)
BGCOLOR = SKYBLUE

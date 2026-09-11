import pygame
import nltk
import random
from nltk.corpus import words


# RUNDOWN SCRABBLE ASSIGNMENT  -  MOUNTAINS ENVIRONMENT EDITION
#
# Description: A simplified Scrabble game for 2 to 4 players, played with the mouse.
#              Players take turns placing letter tiles on a 15x15 board. Tiles placed
#              in one turn must form a straight line and connect to the board. The first
#              word must cover the centre star. Words are checked against NLTK's English
#              word list so only real words score points. The player with the most points
#              when the bag and all hands are empty wins.
#
#              THEME - Mountains Environment: this edition rewards exploring the mountain
#              ecosystem. When a player spells the name of a mountain animal, plant or
#              landform (e.g. IBEX, PINE, GLACIER), they earn BONUS points and the game
#              shows a short fact about how that thing lives in or shapes the mountains.
#              This ties learning about the ecosystem and responsible recreation into the
#              normal scrabble scoring, without changing how the game is played.
#
# Level 1: Menu system with PLAY, HOW TO PLAY and QUIT buttons, plus a screen to pick
#          how many players (2 to 4) before the game starts.
# Level 2: A full 15x15 board is drawn. Players select a tile from their hand and click
#          an empty square to place it. Right-click takes a just-placed tile back.
# Level 3: Turn rules are enforced (straight line, no gaps, must connect, first word on
#          the centre star). Each tile has its standard Scrabble point value.
# Level 4: The word formed is checked against the NLTK English word list. Real words score
#          points; fake words are rejected with a message. Scores, the current player, the
#          tiles left in the bag and the active hand are all shown in a side panel.
# Level 4+: All input and output is graphics-based using Pygame. SUBMIT, RECALL and PASS
#           buttons control the turn, and the game ends with a win/tie message.
#
# Used Python documentation and the Pygame reference for help with graphics and events.
# Used NLTK documentation for help with the English word list used to check words.
# Used functions and modular design so each screen and rule has its own function.
# Used pygame blit and draw.rect to build every UI element on the screen.
# Took a lot of time to plan the board layout, the side panel and the turn rules.
#
# SHAHEER RASHID


# 1. SETTINGS
WIDTH  = 1000
HEIGHT = 700

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rundown Scrabble")
clock = pygame.time.Clock() # clock from documantation

# Fonts used throughout the UI
font_big = pygame.font.SysFont("Arial", 44, bold=True)
font_med = pygame.font.SysFont("Arial", 30, bold=True)
font_small = pygame.font.SysFont("Arial", 22)
font_tiny = pygame.font.SysFont("Arial", 14)

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GRAY = (130, 130, 130)
LIGHT_GRAY = (220, 220, 215)
CREAM = (255, 248, 220)
TAN = (210, 180, 140)
DARK_TAN = (160, 120, 70)
YELLOW = (255, 215, 0)
PINK = (255, 182, 193)
BROWN = (101, 67, 33)

# Game states (which screen we are on)
STATE_MENU = 0
STATE_SELECT = 1
STATE_GAME = 2
STATE_HELP = 3
STATE_QUIT = 4

# Standard Scrabble letter point values
LETTER_VALUES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
    'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3,
    'Q':10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
    'Y': 4, 'Z':10
}

# Standard Scrabble tile counts (how many of each letter go in the bag)
LETTER_DIST = {
    'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E':12, 'F': 2, 'G': 3, 'H': 2,
    'I': 9, 'J': 1, 'K': 1, 'L': 4, 'M': 2, 'N': 6, 'O': 8, 'P': 2,
    'Q': 1, 'R': 6, 'S': 4, 'T': 6, 'U': 4, 'V': 2, 'W': 2, 'X': 1,
    'Y': 2, 'Z': 1
}

# Board layout numbers
BOARD_SIZE = 15
CELL = 36
BOARD_X = 10
BOARD_Y = 20
PANEL_X = BOARD_X + BOARD_SIZE * CELL + 20

# A colour to tint each player's score line
PLAYER_COLORS = [
    (210, 30, 30),    # Player 1 - red
    (30, 30, 210),    # Player 2 - blue
    (30, 160, 30),    # Player 3 - green
    (180, 110, 0),    # Player 4 - amber
]

# The board is stored as a single (1D) list of 15 x 15 = 225 squares, NOT a 2D
# list. This helper turns a row and column into the matching position in that
# 1D list, so the rest of the code can still think in rows and columns.
def index_of(row, col):
    return row * BOARD_SIZE + col


# Snowflakes for the gentle snow animation on the menu screen. Two PARALLEL 1D
# lists hold the x and y position of each flake (kept separate so we never need
# a 2D list). The flakes fall down the screen and reset to the top.
snow_x = []
snow_y = []
for i in range(45):
    snow_x.append(random.randint(0, WIDTH))
    snow_y.append(random.randint(0, HEIGHT))


# Mountain background loaded from mountain_bg.jpg in the game folder.
# Falls back to the original solid-colour fill if the file is missing.
_mountain_bg = None
try:
    _img = pygame.image.load("mountain_bg.jpg")
    _mountain_bg = pygame.transform.scale(_img, (WIDTH, HEIGHT))
    print(">>> Mountain background loaded!")
except Exception as _e:
    print(">>> Mountain background not found:", _e)

# Semi-transparent dark overlay blitted over the photo so text stays readable.
_dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
_dark_overlay.fill((0, 0, 0, 110))

# Letter tile PNGs: A.png through Z.png in the game folder.
# Falls back to drawn coloured rectangles if any file is missing.
_tile_imgs_board = {}   # letter -> Surface scaled to board cell size
_tile_imgs_hand  = {}   # letter -> Surface scaled to hand tile size
for _letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    try:
        _img = pygame.image.load(_letter + ".png")
        _tile_imgs_board[_letter] = pygame.transform.scale(_img, (CELL - 1, CELL - 1))
        _tile_imgs_hand[_letter]  = pygame.transform.scale(_img, (50, 52))
    except Exception:
        pass
print(">>> Letter tile PNGs loaded:", len(_tile_imgs_board), "/ 26")

# Snowflake PNG for the animated snow on the menu screen.
_snowflake_img = None
try:
    _sf = pygame.image.load("snowflake.png")
    _snowflake_img = pygame.transform.scale(_sf, (14, 14))
    print(">>> Snowflake PNG loaded!")
except Exception as _e:
    print(">>> Snowflake PNG not found, using circles:", _e)

# Board cell PNG for empty squares on the playing board.
_board_cell_img = None
try:
    _bc = pygame.image.load("board_cell.png")
    _board_cell_img = pygame.transform.scale(_bc, (CELL - 1, CELL - 1))
    print(">>> Board cell PNG loaded!")
except Exception as _e:
    print(">>> Board cell PNG not found, using rectangles:", _e)


# 2. WORD LIST SETUP
# Load NLTK's English word list so we can check if a typed word is real.
# If the 'words' data is not downloaded yet, download it once. The words are
# stored in a set in UPPERCASE because the tiles on the board are uppercase,
# and a set makes the "is this a real word?" check very fast.
print(">>> Loading dictionary...")
try:
    word_list = words.words()
except LookupError:
    print(">>> Downloading NLTK word list...")
    nltk.download('words')
    word_list = words.words()

VALID_WORDS = set()
for w in word_list:
    if len(w) >= 2:   # single-letter "words" like A/I are never valid
        VALID_WORDS.add(w.upper())
print(">>> Dictionary ready:", len(VALID_WORDS), "words")


# 2.5 MOUNTAINS ENVIRONMENT THEME DATA
# A dictionary of words connected to the mountain ecosystem. The key is the word
# (UPPERCASE, to match the board tiles) and the value is a short fact about how
# that animal, plant or landform fits into the mountains. Spelling one of these
# words earns the player MOUNTAIN_BONUS extra points and shows the fact, so the
# game teaches the player about the environment while they play.
MOUNTAIN_BONUS = 5

MOUNTAIN_WORDS = {
    # --- Animals adapted to mountains ---
    "GOAT":   "Mountain goats have rubbery hooves that grip steep, rocky cliffs.",
    "IBEX":   "The ibex is a wild goat that climbs near-vertical rock faces.",
    "YAK":    "Yaks have thick wool and large lungs to survive high, thin air.",
    "PUMA":   "Pumas roam mountain slopes hunting deer; give them space.",
    "LYNX":   "The lynx has wide, furry paws that act like snowshoes.",
    "BEAR":   "Bears feed on mountain berries and should never be fed by people.",
    "PIKA":   "Pikas store dried plants for winter and are harmed by warming peaks.",
    "ELK":    "Elk migrate up and down mountains following fresh green plants.",
    "DEER":   "Deer graze alpine meadows; quiet hikers are less likely to scare them.",
    "HARE":   "The mountain hare turns white in winter to hide in the snow.",
    "MARMOT": "Marmots whistle a warning and hibernate through the cold months.",
    "CONDOR": "Condors ride mountain air currents to soar without flapping.",
    "EAGLE":  "Eagles nest on high cliffs and hunt across the valleys below.",

    # --- Plants adapted to mountains ---
    "PINE":   "Pine trees have needles and bark that resist mountain cold.",
    "FIR":    "Fir trees grow in a cone shape so heavy snow slides off them.",
    "MOSS":   "Moss holds water and protects thin mountain soil from washing away.",
    "FERN":   "Ferns grow in shady, damp spots low on the mountain slopes.",
    "CEDAR":  "Cedars are tough evergreens that anchor steep mountain soil.",
    "SPRUCE": "Spruce forests give shelter and food to many mountain animals.",
    "LICHEN": "Lichen survives on bare rock and is the first life on new ground.",

    # --- Landforms and features of the mountain environment ---
    "PEAK":   "A peak is the highest point of a mountain.",
    "SNOW":   "Mountain snow melts in spring to feed rivers far downstream.",
    "RIVER":  "Rivers begin high in the mountains from melting snow and ice.",
    "ROCK":   "Loose mountain rock can slide, so stay on marked trails.",
    "SLOPE":  "A steep slope sheds water fast, so its soil erodes easily.",
    "RIDGE":  "A ridge is the long narrow top edge between two slopes.",
    "ALPINE": "The alpine zone sits above the treeline where only small plants grow.",
    "GLACIER":"A glacier is a slow river of ice that carves mountain valleys.",
    "VALLEY": "Valleys between mountains shelter forests, rivers and wildlife.",
    "FOREST": "Mountain forests hold the soil and clean the air and water.",
    "STREAM": "Clear mountain streams carry meltwater and host fragile life.",
    "SUMMIT": "The summit is the very top; leave no trace when you reach it.",
    "CLIFF":  "Cliffs give nesting birds safety from ground predators.",
    "CAVE":   "Mountain caves shelter bats and stay cool all year round.",
    "TRAIL":  "Staying on the trail protects fragile plants from being trampled.",
    "TUNDRA": "Alpine tundra has tiny plants that take years to recover if damaged.",
    "MEADOW": "Alpine meadows burst with wildflowers in the short summer.",
}


def get_mountain_fact(word):
    # If the given word is part of the mountain ecosystem, return its fact.
    # Otherwise return an empty string. Used by submit_turn to award the bonus.
    if word in MOUNTAIN_WORDS:
        return MOUNTAIN_WORDS[word]
    return ""


# 3. GAME DATA
# These globals hold the whole state of the current game. They are set up
# properly by setup_game() when the player presses START GAME.
board = []
tile_bag = []
num_players = 2
player_hands = []
player_scores = []
current_player = 0
selected_tile = -1
placed_this_turn = []
game_message = ""
game_over = False
consecutive_passes = 0
eco_fact = ""   # the latest mountain-ecosystem fact to show in the panel


# 4. GAME HELPER FUNCTIONS

def make_bag():
    # Build the bag of letters using the standard tile counts, then shuffle it.
    bag = []
    for letter in LETTER_DIST:
        count = LETTER_DIST[letter]
        for i in range(count):
            bag.append(letter)
    random.shuffle(bag)
    return bag


def setup_game(how_many_players):
    # Start a brand new game with the chosen number of players.
    global board, tile_bag, num_players, player_hands, player_scores
    global current_player, selected_tile, placed_this_turn
    global game_message, game_over, consecutive_passes, eco_fact

    num_players = how_many_players
    tile_bag = make_bag()
    player_hands = []
    player_scores = []
    current_player = 0
    selected_tile = -1
    placed_this_turn = []
    game_over = False
    consecutive_passes = 0
    eco_fact = ""
    game_message = "Player 1's turn!  Spell mountain words for bonus points!"

    # Build an empty board as one flat (1D) list of 225 squares.
    # None means the square is empty.
    board = []
    for i in range(BOARD_SIZE * BOARD_SIZE):
        board.append(None)

    # Give every player a score of 0 and a starting hand of 7 tiles.
    # Each player's hand is stored as a STRING of letters (e.g. "AEIOTRS"),
    # so player_hands is a simple list of strings rather than a 2D list.
    for i in range(num_players):
        player_scores.append(0)
        hand = ""
        for j in range(7):
            if len(tile_bag) > 0:
                hand = hand + tile_bag.pop()
        player_hands.append(hand)


def refill_hand(player_index):
    # Top a player's hand back up to 7 tiles (or until the bag runs out).
    while len(player_hands[player_index]) < 7 and len(tile_bag) > 0:
        player_hands[player_index] = player_hands[player_index] + tile_bag.pop()


def recall_tiles():
    # Take back every tile the current player placed this turn and put them
    # back in their hand. Used by RECALL, PASS and the MENU button.
    global selected_tile, placed_this_turn

    for spot in placed_this_turn:
        row = spot[0]
        col = spot[1]
        letter = board[index_of(row, col)]
        if letter is not None:
            board[index_of(row, col)] = None
            player_hands[current_player] = player_hands[current_player] + letter

    placed_this_turn = []
    selected_tile = -1


def board_has_existing_tiles():
    # Returns True if there are already tiles on the board from past turns
    # (not counting the ones placed this turn).
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[index_of(row, col)] is not None and (row, col) not in placed_this_turn:
                return True
    return False


def touches_existing_tile():
    # Returns True if at least one tile placed this turn sits next to a tile
    # that was already on the board (up, down, left or right).
    for spot in placed_this_turn:
        row = spot[0]
        col = spot[1]
        neighbours = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for step in neighbours:
            n_row = row + step[0]
            n_col = col + step[1]
            if 0 <= n_row < BOARD_SIZE and 0 <= n_col < BOARD_SIZE:
                if board[index_of(n_row, n_col)] is not None and (n_row, n_col) not in placed_this_turn:
                    return True
    return False


def tiles_form_line():
    # Checks that the tiles placed this turn are all in one straight line
    # (same row OR same column) with no empty gaps between them.
    if len(placed_this_turn) <= 1:
        return True

    rows = []
    cols = []
    for spot in placed_this_turn:
        rows.append(spot[0])
        cols.append(spot[1])

    same_row = len(set(rows)) == 1
    same_col = len(set(cols)) == 1

    # If they are not all in one row and not all in one column, it is not a line.
    if same_row == False and same_col == False:
        return False

    # Walk along the line and make sure there are no empty squares in between.
    if same_row:
        row = rows[0]
        for col in range(min(cols), max(cols) + 1):
            if board[index_of(row, col)] is None:
                return False
    else:
        col = cols[0]
        for row in range(min(rows), max(rows) + 1):
            if board[index_of(row, col)] is None:
                return False

    return True


def get_main_word():
    # Reads the full word formed along the line of placed tiles. It starts at a
    # placed tile and walks backwards to the start of the word, then forwards to
    # the end, including any older tiles it connects to. This is the word that
    # gets checked against the NLTK word list.
    rows = []
    cols = []
    for spot in placed_this_turn:
        rows.append(spot[0])
        cols.append(spot[1])

    # Decide if the word runs across (same row) or down (same column).
    # When only one tile is placed we must look at the board context: if there
    # are existing tiles directly above or below, the word runs vertically.
    if len(placed_this_turn) == 1:
        r = rows[0]
        c = cols[0]
        has_vertical_neighbour = (
            (r > 0 and board[index_of(r - 1, c)] is not None) or
            (r < BOARD_SIZE - 1 and board[index_of(r + 1, c)] is not None)
        )
        horizontal = not has_vertical_neighbour
    else:
        horizontal = len(set(rows)) == 1

    word = ""
    if horizontal:
        row = rows[0]
        col = min(cols)
        # Walk left to the very start of the word.
        while col > 0 and board[index_of(row, col - 1)] is not None:
            col = col - 1
        # Walk right collecting every letter until we hit an empty square.
        while col < BOARD_SIZE and board[index_of(row, col)] is not None:
            word = word + board[index_of(row, col)]
            col = col + 1
    else:
        col = cols[0]
        row = min(rows)
        while row > 0 and board[index_of(row - 1, col)] is not None:
            row = row - 1
        while row < BOARD_SIZE and board[index_of(row, col)] is not None:
            word = word + board[index_of(row, col)]
            row = row + 1

    return word


def calc_turn_score():
    # Adds up the point values of all the tiles placed this turn.
    score = 0
    for spot in placed_this_turn:
        row = spot[0]
        col = spot[1]
        letter = board[index_of(row, col)]
        if letter is not None:
            score = score + LETTER_VALUES[letter]
    return score


def submit_turn():
    # Runs when the player presses SUBMIT. Checks every rule in order and either
    # rejects the move with a message or scores it and moves to the next player.
    global current_player, selected_tile, placed_this_turn
    global game_message, game_over, consecutive_passes, eco_fact

    # Rule: at least one tile must be placed.
    if len(placed_this_turn) == 0:
        game_message = "Place at least one tile before submitting!"
        return

    # Rule: the tiles must form a straight line with no gaps.
    if tiles_form_line() == False:
        game_message = "Tiles must be in a straight line with no gaps!"
        return

    # Rule: the first word must cover the centre star; later words must connect.
    if board_has_existing_tiles() == False:
        if (7, 7) not in placed_this_turn:
            game_message = "First word must cover the centre star square!"
            return
    else:
        if touches_existing_tile() == False:
            game_message = "Your tiles must connect to tiles already on the board!"
            return

    # Rule: the word must be a real English word (NLTK check).
    word = get_main_word()
    if len(word) < 2:
        game_message = "Words must be at least 2 letters long!"
        return
    if word not in VALID_WORDS:
        game_message = word + " is not a real word!  Try again."
        return

    # The move is legal, so work out the score.
    turn_score = calc_turn_score()

    # THEME: if the word is part of the mountain ecosystem, add the bonus and
    # remember its fact so the panel can teach the player about the environment.
    fact = get_mountain_fact(word)
    if fact != "":
        turn_score = turn_score + MOUNTAIN_BONUS
        eco_fact = word + ": " + fact
    else:
        eco_fact = ""

    player_scores[current_player] = player_scores[current_player] + turn_score
    placed_this_turn = []
    selected_tile = -1
    consecutive_passes = 0

    # Tell the player how they did before passing to the next player.
    if fact != "":
        scored_player = current_player
        refill_hand(current_player)
        current_player = (current_player + 1) % num_players
        game_message = ("Player " + str(scored_player + 1) + " spelled a mountain word!  +"
                        + str(MOUNTAIN_BONUS) + " bonus points.")
    else:
        refill_hand(current_player)
        current_player = (current_player + 1) % num_players

    # If the bag is empty and someone has run out of tiles, the game ends.
    if len(tile_bag) == 0:
        all_empty = True
        for i in range(num_players):
            if len(player_hands[i]) > 0:
                all_empty = False
        if all_empty:
            end_game()
            return

    # Only show the plain "next turn" message if there was no bonus message,
    # so the player still gets to read their mountain-word reward.
    if fact == "":
        game_message = "Player " + str(current_player + 1) + "'s turn!"


def pass_turn():
    # Runs when the player presses PASS. Takes back their tiles and skips them.
    global current_player, game_message, consecutive_passes

    recall_tiles()
    consecutive_passes = consecutive_passes + 1

    # If everyone passes twice in a row, the game ends.
    if consecutive_passes >= num_players * 2:
        end_game()
        return

    current_player = (current_player + 1) % num_players
    game_message = "Player " + str(current_player + 1) + "'s turn!  (passed)"


def end_game():
    # Works out the winner (or a tie) and shows the final message.
    global game_over, game_message

    game_over = True
    best = max(player_scores)

    winners = []
    for i in range(num_players):
        if player_scores[i] == best:
            winners.append(i + 1)

    if len(winners) == 1:
        game_message = "Game Over!  Player " + str(winners[0]) + " wins with " + str(best) + " points!"
    else:
        names = ""
        for i in range(len(winners)):
            names = names + str(winners[i])
            if i < len(winners) - 1:
                names = names + " and "
        game_message = "Game Over!  Tie between Players " + names + " with " + str(best) + " points!"


# 5. DRAWING FUNCTIONS
# Each screen and each piece of the UI has its own function to keep things tidy.

def draw_text(text, the_font, colour, x, y):
    # Helper: draw text at an exact position.
    surf = the_font.render(text, True, colour)
    screen.blit(surf, (x, y))


def draw_centered_text(text, the_font, colour, y):
    # Helper: draw text centred across the whole window.
    surf = the_font.render(text, True, colour)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


def draw_snow():
    # Animate the falling snow on the menu. Each loop draws one flake, moves it
    # down a little, and sends it back to the top once it falls off the screen.
    # Because the menu is redrawn 60 times a second, this makes the snow fall.
    for i in range(len(snow_x)):
        if _snowflake_img is not None:
            # Centre the snowflake image on the flake's position.
            screen.blit(_snowflake_img, (snow_x[i] - 7, snow_y[i] - 7))
        else:
            pygame.draw.circle(screen, WHITE, (snow_x[i], snow_y[i]), 2)
        snow_y[i] = snow_y[i] + 2
        if snow_y[i] > HEIGHT:
            snow_y[i] = 0
            snow_x[i] = random.randint(0, WIDTH)


def draw_menu(mouse_x, mouse_y, mouse_button, state):
    # The main menu. Use the downloaded mountain photo if available.
    if _mountain_bg is not None:
        screen.blit(_mountain_bg, (0, 0))
        screen.blit(_dark_overlay, (0, 0))
    else:
        screen.fill((70, 100, 130))
        pygame.draw.polygon(screen, (90, 110, 120), [(0, 200), (180, 70), (360, 200)])
        pygame.draw.polygon(screen, (110, 125, 135), [(220, 200), (430, 50), (640, 200)])
        pygame.draw.polygon(screen, (90, 110, 120), [(560, 200), (800, 90), (1000, 200)])
        pygame.draw.polygon(screen, WHITE, [(150, 95), (180, 70), (210, 95)])
        pygame.draw.polygon(screen, WHITE, [(400, 75), (430, 50), (460, 75)])
        pygame.draw.polygon(screen, WHITE, [(770, 113), (800, 90), (830, 113)])

    # The animated falling snow sits on top of the background.
    draw_snow()

    draw_centered_text("RUNDOWN SCRABBLE", font_big, WHITE, 60)
    draw_centered_text("Mountains Environment Edition - explore the ecosystem!", font_small, CREAM, 120)

    button_width = 280
    button_height = 70
    button_x = WIDTH // 2 - button_width // 2

    # Each button: its label, the state it leads to, and its colour.
    buttons = [
        ("PLAY",        STATE_SELECT, (50, 150, 50)),
        ("HOW TO PLAY", STATE_HELP,   (50, 100, 200)),
        ("QUIT",        STATE_QUIT,   (190, 50, 50)),
    ]

    for i in range(len(buttons)):
        label = buttons[i][0]
        next_state = buttons[i][1]
        colour = buttons[i][2]
        button_y = 210 + i * 120
        rect = pygame.Rect(button_x, button_y, button_width, button_height)

        pygame.draw.rect(screen, colour, rect)

        # Highlight the button when the mouse is over it; act on a click.
        if rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, YELLOW, rect, 4)
            if mouse_button == 1:
                state = next_state
        else:
            pygame.draw.rect(screen, WHITE, rect, 2)

        draw_text(label, font_med, WHITE,
                  button_x + button_width // 2 - font_med.size(label)[0] // 2,
                  button_y + button_height // 2 - font_med.size(label)[1] // 2)

    return state


def draw_select(mouse_x, mouse_y, mouse_button, state):
    # The screen where the player chooses 2, 3 or 4 players.
    global num_players

    if _mountain_bg is not None:
        screen.blit(_mountain_bg, (0, 0))
        screen.blit(_dark_overlay, (0, 0))
    else:
        screen.fill((34, 100, 34))
    draw_centered_text("How many players?", font_med, WHITE, 110)

    # Three number buttons: 2, 3 and 4.
    for n in range(2, 5):
        box_x = WIDTH // 2 - 205 + (n - 2) * 160
        rect = pygame.Rect(box_x, 230, 110, 110)

        # The currently chosen number is filled yellow.
        if n == num_players:
            pygame.draw.rect(screen, YELLOW, rect)
            number_colour = BLACK
        else:
            pygame.draw.rect(screen, (50, 130, 50), rect)
            number_colour = WHITE

        if rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, WHITE, rect, 4)
            if mouse_button == 1:
                num_players = n
        else:
            pygame.draw.rect(screen, WHITE, rect, 2)

        draw_text(str(n), font_big, number_colour,
                  box_x + 55 - font_big.size(str(n))[0] // 2,
                  285 - font_big.size(str(n))[1] // 2)

    # START GAME button.
    start_rect = pygame.Rect(WIDTH // 2 - 110, 430, 220, 60)
    pygame.draw.rect(screen, (30, 150, 30), start_rect)
    if start_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, YELLOW, start_rect, 4)
        if mouse_button == 1:
            setup_game(num_players)
            state = STATE_GAME
    else:
        pygame.draw.rect(screen, WHITE, start_rect, 2)
    draw_centered_text("START GAME", font_med, WHITE, 460 - font_med.size("START GAME")[1] // 2)

    # Back button in the corner.
    back_rect = pygame.Rect(20, 20, 100, 40)
    pygame.draw.rect(screen, GRAY, back_rect)
    if back_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, WHITE, back_rect, 3)
        if mouse_button == 1:
            state = STATE_MENU
    draw_text("Back", font_small, WHITE,
              70 - font_small.size("Back")[0] // 2,
              40 - font_small.size("Back")[1] // 2)

    return state


def draw_help(mouse_x, mouse_y, mouse_button, state):
    # The HOW TO PLAY screen with all the rules.
    if _mountain_bg is not None:
        screen.blit(_mountain_bg, (0, 0))
        screen.blit(_dark_overlay, (0, 0))
    else:
        screen.fill((20, 60, 140))
    draw_centered_text("HOW TO PLAY", font_med, WHITE, 20)

    help_lines = [
        "1. Players take turns placing letter tiles on the board.",
        "2. Click a tile in your hand to select it  (it turns yellow).",
        "3. Click an empty board square to place the selected tile.",
        "4. Right-click a tile you just placed to take it back.",
        "5. All tiles you place in one turn must be in a straight line.",
        "6. Your word must connect to tiles already on the board.",
        "7. The very FIRST word must cover the centre star  ( * ).",
        "8. Words are checked against a real English dictionary.",
        "9. Click SUBMIT to confirm your word and earn points.",
        "10. Click RECALL to take back ALL tiles you placed this turn.",
        "11. Click PASS to skip your turn entirely.",
        "",
        "Scoring:  Add up the small numbers on each tile you placed.",
        "Rare letters like Q and Z are worth more points!",
        "",
        "MOUNTAINS THEME:  Spell the name of a mountain animal, plant or",
        "landform (e.g. IBEX, PINE, GLACIER) to earn +5 BONUS points and",
        "learn a fact about how it lives in or shapes the mountains.",
        "",
        "The game ends when the bag is empty and all hands are empty,",
        "or if all players pass twice in a row.",
        "The player with the most points wins!",
    ]

    y = 76
    for line in help_lines:
        draw_text(line, font_small, CREAM, 40, y)
        y = y + 25

    # Back to menu button.
    back_rect = pygame.Rect(WIDTH // 2 - 100, 636, 200, 50)
    pygame.draw.rect(screen, GRAY, back_rect)
    if back_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, WHITE, back_rect, 3)
        if mouse_button == 1:
            state = STATE_MENU
    draw_centered_text("Back to Menu", font_small, WHITE, 649)

    return state


def draw_board():
    # Draws the 15x15 board: the placed tiles, the centre star and empty squares.
    pygame.draw.rect(screen, BROWN,
                     pygame.Rect(BOARD_X - 3, BOARD_Y - 3,
                                 BOARD_SIZE * CELL + 6, BOARD_SIZE * CELL + 6))

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x = BOARD_X + col * CELL
            y = BOARD_Y + row * CELL
            cell_rect = pygame.Rect(x, y, CELL - 1, CELL - 1)
            letter = board[index_of(row, col)]

            if letter is not None:
                # A tile is here: use the PNG image if loaded, else draw a rectangle.
                if letter in _tile_imgs_board:
                    screen.blit(_tile_imgs_board[letter], (x, y))
                    if (row, col) in placed_this_turn:
                        _hl = pygame.Surface((CELL - 1, CELL - 1), pygame.SRCALPHA)
                        _hl.fill((255, 215, 0, 100))
                        screen.blit(_hl, (x, y))
                else:
                    if (row, col) in placed_this_turn:
                        pygame.draw.rect(screen, YELLOW, cell_rect)
                    else:
                        pygame.draw.rect(screen, TAN, cell_rect)
                    pygame.draw.rect(screen, DARK_TAN, cell_rect, 1)
                    draw_text(letter, font_small, BLACK,
                              x + CELL // 2 - font_small.size(letter)[0] // 2, y + 3)
                    draw_text(str(LETTER_VALUES[letter]), font_tiny, (80, 80, 80),
                              x + CELL - 11, y + CELL - 14)

            elif row == 7 and col == 7:
                # The centre star square.
                pygame.draw.rect(screen, PINK, cell_rect)
                draw_text("*", font_small, RED,
                          x + CELL // 2 - font_small.size("*")[0] // 2,
                          y + CELL // 2 - font_small.size("*")[1] // 2)
            else:
                # An empty square: use the board cell PNG if loaded, else plain colour.
                if _board_cell_img is not None:
                    screen.blit(_board_cell_img, (x, y))
                else:
                    pygame.draw.rect(screen, CREAM, cell_rect)

            pygame.draw.rect(screen, (180, 160, 120), cell_rect, 1)


def draw_panel(mouse_x, mouse_y):
    # Draws the right-hand side panel and returns the four button rects and the
    # list of tile rects so the click handling can use them.
    panel_rect = pygame.Rect(PANEL_X - 5, 0, WIDTH - PANEL_X + 5, HEIGHT)
    pygame.draw.rect(screen, (245, 240, 228), panel_rect)
    pygame.draw.rect(screen, BROWN, panel_rect, 2)

    px = PANEL_X
    py = 8

    draw_text("SCRABBLE", font_med, BROWN, px + 10, py)
    py = py + 40
    pygame.draw.rect(screen, BROWN, pygame.Rect(px, py, WIDTH - px - 4, 2))
    py = py + 6

    # Scores for every player. The current player gets a "> " arrow.
    draw_text("SCORES:", font_small, BLACK, px + 5, py)
    py = py + 26
    for i in range(num_players):
        if i == current_player and game_over == False:
            prefix = "> "
        else:
            prefix = "  "
        score_text = prefix + "Player " + str(i + 1) + ":  " + str(player_scores[i]) + " pts"
        draw_text(score_text, font_small, PLAYER_COLORS[i], px + 5, py)
        py = py + 24

    py = py + 4
    pygame.draw.rect(screen, BROWN, pygame.Rect(px, py, WIDTH - px - 4, 2))
    py = py + 6

    draw_text("Tiles left in bag:  " + str(len(tile_bag)), font_small, BLACK, px + 5, py)
    py = py + 28
    pygame.draw.rect(screen, BROWN, pygame.Rect(px, py, WIDTH - px - 4, 2))
    py = py + 6

    # The current player's hand of tiles.
    draw_text("Player " + str(current_player + 1) + "'s Hand:", font_small,
              PLAYER_COLORS[current_player], px + 5, py)
    py = py + 26

    hand = player_hands[current_player]
    tile_rects = []
    for i in range(len(hand)):
        letter = hand[i]
        tx = px + 5 + i * 54
        ty = py
        tile_rect = pygame.Rect(tx, ty, 50, 52)
        tile_rects.append(tile_rect)

        if letter in _tile_imgs_hand:
            screen.blit(_tile_imgs_hand[letter], (tx, ty))
            if i == selected_tile:
                _hl = pygame.Surface((50, 52), pygame.SRCALPHA)
                _hl.fill((255, 215, 0, 100))
                screen.blit(_hl, (tx, ty))
        else:
            if i == selected_tile:
                pygame.draw.rect(screen, YELLOW, tile_rect)
            else:
                pygame.draw.rect(screen, TAN, tile_rect)
            pygame.draw.rect(screen, DARK_TAN, tile_rect, 2)
            draw_text(letter, font_med, BLACK,
                      tx + 25 - font_med.size(letter)[0] // 2, ty + 7)
            draw_text(str(LETTER_VALUES[letter]), font_tiny, (80, 80, 80),
                      tx + 38, ty + 37)

    py = py + 62

    # The four control buttons.
    submit_rect = pygame.Rect(px + 5, py, 122, 40)
    recall_rect = pygame.Rect(px + 133, py, 122, 40)
    py = py + 46
    pass_rect = pygame.Rect(px + 5, py, 122, 40)
    menu_rect = pygame.Rect(px + 133, py, 122, 40)
    py = py + 52

    button_defs = [
        (submit_rect, "SUBMIT", (0, 160, 0)),
        (recall_rect, "RECALL", (200, 120, 0)),
        (pass_rect,   "PASS",   (180, 0, 0)),
        (menu_rect,   "MENU",   (80, 80, 80)),
    ]
    for button in button_defs:
        rect = button[0]
        label = button[1]
        colour = button[2]
        pygame.draw.rect(screen, colour, rect)
        if rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, WHITE, rect, 3)
        else:
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)
        draw_text(label, font_small, WHITE,
                  rect.centerx - font_small.size(label)[0] // 2,
                  rect.centery - font_small.size(label)[1] // 2)

    pygame.draw.rect(screen, BROWN, pygame.Rect(px, py, WIDTH - px - 4, 2))
    py = py + 8

    # The status message, in green normally and red when it is a warning.
    if game_over:
        message_colour = BLUE
    elif "real word" in game_message or "must" in game_message or "Place" in game_message or "First" in game_message:
        message_colour = RED
    else:
        message_colour = (0, 100, 0)

    # Word-wrap the message so it fits inside the panel.
    max_width = WIDTH - px - 12
    words_in_message = game_message.split()
    line = ""
    for word in words_in_message:
        test_line = line + word + " "
        if font_small.size(test_line)[0] > max_width and line != "":
            draw_text(line.strip(), font_small, message_colour, px + 5, py)
            py = py + 24
            line = word + " "
        else:
            line = test_line
    if line != "":
        draw_text(line.strip(), font_small, message_colour, px + 5, py)
        py = py + 24

    # THEME: the mountain ecosystem fact box. Shows the latest fact the player
    # earned by spelling a mountain word, so the game teaches as it is played.
    py = py + 10
    fact_box = pygame.Rect(px, py, WIDTH - px - 4, HEIGHT - py - 8)
    pygame.draw.rect(screen, (225, 240, 230), fact_box)
    pygame.draw.rect(screen, (40, 110, 70), fact_box, 2)

    draw_text("MOUNTAIN ECO-FACT", font_small, (40, 110, 70), px + 6, py + 6)
    fy = py + 34

    if eco_fact == "":
        # Nothing earned yet: gently nudge the player towards the theme.
        draw_text("Spell mountain words like", font_tiny, (60, 90, 70), px + 6, fy)
        draw_text("IBEX, PINE or GLACIER for", font_tiny, (60, 90, 70), px + 6, fy + 16)
        draw_text("+" + str(MOUNTAIN_BONUS) + " points and a fact!", font_tiny, (60, 90, 70), px + 6, fy + 32)
    else:
        # Word-wrap the earned fact so it fits inside the box.
        fact_max_width = WIDTH - px - 14
        fact_words = eco_fact.split()
        fact_line = ""
        for word in fact_words:
            test_line = fact_line + word + " "
            if font_tiny.size(test_line)[0] > fact_max_width and fact_line != "":
                draw_text(fact_line.strip(), font_tiny, (20, 70, 40), px + 6, fy)
                fy = fy + 16
                fact_line = word + " "
            else:
                fact_line = test_line
        if fact_line != "":
            draw_text(fact_line.strip(), font_tiny, (20, 70, 40), px + 6, fy)

    return submit_rect, recall_rect, pass_rect, menu_rect, tile_rects


def handle_game_click(mouse_x, mouse_y, mouse_button, buttons, tile_rects, state):
    # Deals with mouse clicks during the game: selecting/placing tiles, pressing
    # the buttons, and right-clicking to take a tile back.
    global selected_tile, placed_this_turn

    submit_rect = buttons[0]
    recall_rect = buttons[1]
    pass_rect = buttons[2]
    menu_rect = buttons[3]

    if mouse_button == 1:
        # Did the player click one of the tiles in their hand?
        for i in range(len(tile_rects)):
            if tile_rects[i].collidepoint(mouse_x, mouse_y):
                selected_tile = i
                return state

        # Did the player click a board square?
        rel_x = mouse_x - BOARD_X
        rel_y = mouse_y - BOARD_Y
        if 0 <= rel_x < BOARD_SIZE * CELL and 0 <= rel_y < BOARD_SIZE * CELL:
            col = rel_x // CELL
            row = rel_y // CELL
            # Place the selected tile if that square is empty.
            if selected_tile >= 0 and game_over == False and board[index_of(row, col)] is None:
                hand = player_hands[current_player]
                board[index_of(row, col)] = hand[selected_tile]
                placed_this_turn.append((row, col))
                # Remove the chosen letter from the hand string by joining the
                # part before it to the part after it.
                player_hands[current_player] = hand[:selected_tile] + hand[selected_tile + 1:]
                selected_tile = -1
            return state

        # Otherwise, check the control buttons.
        if game_over == False:
            if submit_rect.collidepoint(mouse_x, mouse_y):
                submit_turn()
            elif recall_rect.collidepoint(mouse_x, mouse_y):
                recall_tiles()
            elif pass_rect.collidepoint(mouse_x, mouse_y):
                pass_turn()

        if menu_rect.collidepoint(mouse_x, mouse_y):
            recall_tiles()
            state = STATE_MENU

    elif mouse_button == 3:
        # Right-click takes back a tile you placed this turn.
        rel_x = mouse_x - BOARD_X
        rel_y = mouse_y - BOARD_Y
        if 0 <= rel_x < BOARD_SIZE * CELL and 0 <= rel_y < BOARD_SIZE * CELL:
            col = rel_x // CELL
            row = rel_y // CELL
            if (row, col) in placed_this_turn:
                letter = board[index_of(row, col)]
                board[index_of(row, col)] = None
                placed_this_turn.remove((row, col))
                player_hands[current_player] = player_hands[current_player] + letter

    return state


def draw_game(mouse_x, mouse_y, mouse_button, state):
    # Draws the whole game screen and then handles any click on it.
    if _mountain_bg is not None:
        screen.blit(_mountain_bg, (0, 0))
        screen.blit(_dark_overlay, (0, 0))
    else:
        screen.fill(LIGHT_GRAY)
    draw_board()
    buttons = draw_panel(mouse_x, mouse_y)
    submit_rect = buttons[0]
    recall_rect = buttons[1]
    pass_rect   = buttons[2]
    menu_rect   = buttons[3]
    tile_rects  = buttons[4]
    state = handle_game_click(mouse_x, mouse_y, mouse_button,
                              (submit_rect, recall_rect, pass_rect, menu_rect),
                              tile_rects, state)
    return state


# 6. MAIN LOOP
current_state = STATE_MENU
mouse_x = 0
mouse_y = 0
running = True

while running:

    # mouse_button is 0 normally, and becomes 1 (left) or 3 (right) on a click.
    mouse_button = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x = event.pos[0]
            mouse_y = event.pos[1]
            mouse_button = event.button
        if event.type == pygame.MOUSEMOTION:
            mouse_x = event.pos[0]
            mouse_y = event.pos[1]

    # Draw whichever screen we are on, and let it return the next state.
    if current_state == STATE_MENU:
        current_state = draw_menu(mouse_x, mouse_y, mouse_button, current_state)
    elif current_state == STATE_SELECT:
        current_state = draw_select(mouse_x, mouse_y, mouse_button, current_state)
    elif current_state == STATE_GAME:
        current_state = draw_game(mouse_x, mouse_y, mouse_button, current_state)
    elif current_state == STATE_HELP:
        current_state = draw_help(mouse_x, mouse_y, mouse_button, current_state)
    else:
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
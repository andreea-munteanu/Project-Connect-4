import random
import time
from turtle import left
import pygame
import numpy as np

# reading input from input file:
with open('4inaROW.txt', 'r') as file:
    content = file.read()
    OPPONENT, ROWS, COLS, FIRST_PLAYER = content.split()
    ROWS, COLS = int(ROWS), int(COLS)
    # print("OPPONENT =", OPPONENT, ', ROWS = ', ROWS, ', COLS = ', COLS, ', FIRST PLAYER = ', FIRST_PLAYER)
    assert 4 <= ROWS <= 10 and 4 <= COLS <= 10, 'Board must be at least 4x4 and at most 9x9.'
file.close()

# available free cells:
FREE_CELLS = ROWS * COLS

# RGB colours
YELLOW = (255, 230, 5)
RED = (204, 0, 0)
BLUE = (0, 128, 255)
BLACK = (0, 0, 0)
WHITE = (230, 230, 230)

# Initialize the pygame
SQUARE_SIZE = 100
WINDOW_SIZE = (SQUARE_SIZE * COLS, SQUARE_SIZE * (ROWS + 1))
H = (ROWS + 1) * SQUARE_SIZE
W = COLS * SQUARE_SIZE
RADIUS = SQUARE_SIZE // 2 - 5  # error

pygame.init()
TITLE = 'Connect-Four Game'
icon = pygame.image.load('connect4.png')  # icon
pygame.display.set_icon(icon)
screen = pygame.display.set_mode(WINDOW_SIZE)  # set window size
screen.fill(WHITE)  # set background colour to white
pygame.display.set_caption(TITLE)  # set title of the window
clock = pygame.time.Clock()  # create clock so that game doesn't refresh that often
music_file = 'Su Turno.ogg'
pygame.mixer.init()
pygame.mixer.music.load(music_file)
pygame.mixer.music.play(-1)  # If the loops is -1 then the music will repeat indefinitely.
FONT = pygame.font.Font(None, 32)


class Piece(object):
    """
    Class for game board piece.

    Methods for for:
    - initialization
    - GUI representation of piece
    - virtual board update after one of the two players drops piece

    """
    def __init__(self, my_colour, board):
        self.colour = my_colour
        self.board = board

    # draw coloured piece at position (row_count, col_count):
    def draw_piece(self, circle_colour, row_count, col_count):
        pygame.draw.circle(screen, circle_colour,
                           (col_count * SQUARE_SIZE + SQUARE_SIZE // 2,
                            row_count * SQUARE_SIZE + SQUARE_SIZE // 2 + SQUARE_SIZE),
                           RADIUS)
        pygame.display.update()

    # update board after dropping piece at position (row_count, col_count):
    def drop_piece(self, board, player_colour: (int, int, int), row_count: int, col_count: int):
        # 1 for player, 2 for CPU
        if player_colour == YELLOW:
            board[row_count][col_count] = 1
        elif player_colour == RED:
            board[row_count][col_count] = 2


"""_______________________ GENERAL USE FUNCTIONS __________________ """


# get next free row on column col
def next_free_row_on_col(board, column):
    last = -1
    for i in range(ROWS):
        if board[i][column] == 0:
            last = i
    return last  # -1 if column is full


# remaining available moves (columns):
def get_available_moves(board):
    available_cols = []
    for col_count in range(COLS):
        if next_free_row_on_col(board, col_count) != -1:
            available_cols.append(col_count)
    return available_cols


# first available column:
def first_available_column(board):
    global COLS
    for col_count in range(0, COLS):
        if board[0][col_count] == 0:
            return col_count
    return -1


# decrement value:
def decrement(value: int):
    return value - 1


# variable for determining who won the game:
# 1 - human
# 2 - computer/player2
# 0 - tie
winner = 0


# checks whether current state is final state:
def check_win(board, player_colour: (int, int, int)) -> bool:
    """
    :param board: virtual board
    :param player_colour: colour for player (YELLOW for player1, RED for player2/computer)
    :return: boolean value (true if player_colour wins, false otherwise)
    """
    global winner

    def get_board_value(our_colour: (int, int, int)):
        if our_colour == RED:
            return 2
        elif our_colour == YELLOW:
            return 1
        else:
            return -1

    value = get_board_value(player_colour)

    # horizontally:
    def horizontal_win() -> bool:
        # for each row, check whether there are 4 consecutive pieces of the same colour:
        for col in range(COLS - 3):
            for row in range(ROWS):
                if board[row][col] == board[row][col + 1] == board[row][col + 2] == board[row][col + 3] == value:
                    return True
        # if no row has 4 consecutive identical pieces:
        return False

    # vertically:
    def vertical_win() -> bool:
        # check whether there are 4 identical pieces on a column:
        for row in range(ROWS - 3):
            for col in range(COLS):
                if board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col] == value:
                    return True
        return False

    # diagonally:
    def diagonal_win() -> bool:
        def get_all_diagonals():  # checked; works
            # main diagonals:
            diags = [board[::-1, :].diagonal(i) for i in range(-board.shape[0] + 1, board.shape[1])]
            # secondary diagonals:
            diags.extend(board.diagonal(i) for i in range(board.shape[1] - 1, -board.shape[0], -1))
            diags_list = []
            for i in diags:
                diags_list.append(list(i))
            return diags_list  # as list

        # all board diagonals:
        diagonals = get_all_diagonals()

        # parse all diagonals to check for 4 identical pieces:
        for diag_i in diagonals:
            # print(diag_i, "  :  ", end='')
            for elem in range(len(diag_i) - 3):
                # print(diag_i[elem], end='; ')
                if diag_i[elem] == diag_i[elem + 1] == diag_i[elem + 2] == diag_i[elem + 3] == value:
                    return True
        return False

    # at least one type of win has to be true for player 'colour' to win:
    if horizontal_win() or vertical_win() or diagonal_win():
        winner = value
        return True
    return False


# game is over when one colour wins (or when table is full):
def is_game_over(board) -> bool:
    """
    :param board: virtual board
    :return: boolean value (true if either player wins or if there are no moves left, false otherwise)
    """
    return check_win(board, RED) or check_win(board, YELLOW) or FREE_CELLS == 0


# printing board in terminal:
def print_board(board):
    for i in range(ROWS):
        for j in range(COLS):
            if j < COLS - 1:
                print(int(board[i][j]), end='|')
            else:
                print(int(board[i][j]))
    print('\n')


class BoxMessage(object):
    """
    Class for GUI box message.

    Methods for:
    - initialization
    - pygame event corresponding to mouse click (on the box)
    - GUI representation of the text box

    """
    def __init__(self, x, y, w, h, text='Level'):
        self.rect = pygame.Rect(x, y, w, h)  # Rect(left, top, width, height) -> Rect
        self.text = text
        self.colour = WHITE
        self.text_box = FONT.render(text, True, BLUE)
        self.clicked = False

    def click_box(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # if click within box --> change colour from WHITE to BLUE
            if self.rect.collidepoint(event.pos):
                self.clicked = 1 - self.clicked
                self.colour = BLUE
                self.text_box = FONT.render(self.text, True, BLUE)
            self.colour = BLUE if self.clicked else WHITE

    def draw(self):
        screen.blit(self.text_box, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.colour, self.rect, 2)


# class for GUI
class GameBoard(object):
    """
    Class for GUI.

    Methods for:
    - initialization
    - resetting virtual board to all 0s
    - GUI representation of virtual board and its pieces at a given time

    """
    global ROWS, COLS, SQUARE_SIZE

    # initialization:
    def __init__(self):
        self.rows = ROWS
        self.cols = COLS
        self.board = np.zeros((ROWS, COLS))
        self.font = pygame.font.SysFont('Calibri', 32)

    # restart:
    def restart(self):
        self.board = np.zeros((ROWS, COLS))  # board is free again

    # draw board and its coloured pieces
    def draw_board(self):
        for row_count in range(ROWS):
            for col_count in range(COLS):
                pygame.draw.rect(screen, BLUE,
                                 (col_count * SQUARE_SIZE, row_count * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE,
                                  SQUARE_SIZE))
                circle_colour = (0, 0, 0)
                if self.board[row_count][col_count] == 0:  # free cell
                    circle_colour = WHITE
                elif self.board[row_count][col_count] == 1:  # human player
                    circle_colour = YELLOW
                elif self.board[row_count][col_count] == 2:  # CPU player
                    circle_colour = RED
                # initializing game_board.board piece with circle_colour
                board_piece = Piece(circle_colour, self.board)
                board_piece.draw_piece(circle_colour, row_count, col_count)
        # update display:
        pygame.display.update()


# gameBoard object:
game_board = GameBoard()
game_board.draw_board()


class Player(object):
    """
    Class for player.

    Methods for:
    - initialization
    - incrementing score

    """
    def __init__(self, player_colour, score, ply):  #: (int, int, int), score: int, ply: int):
        self.colour = player_colour
        self.score = score
        # self.strategy = strategy
        self.ply = ply  # for algorithms

    def inc_score(self):
        self.score += 1


# player 2 (either human or computer):
computer = Player(RED, 0, 3)  # colour = RED, score = 0
# player 1 (always human):
human = Player(YELLOW, 0, 3)  # colour = YELLOW, score = 0

# initializing first player:
if FIRST_PLAYER == 'human':
    turn = 1
    colour = YELLOW
elif FIRST_PLAYER == 'computer':
    turn = 2
    colour = RED


def switch_player(player_colour: (int, int, int), player_turn: int):
    """
    :param player_colour: colour piece of current player (RED or YELLOW)
    :param player_turn: integer representing whose turn it is (either 1 or 2)
    :return: switched parameter values
    """
    player_turn = 3 - player_turn
    if player_colour == RED:
        player_colour = YELLOW
    else:
        player_colour = RED
    return player_colour, player_turn


# has the game finished?
running = True


# class for AI (superclass for levels of difficulty):
class AI(object):
    """
    Class for AI implementation.

    Methods for:
    - initialization
    - end of recursion (returns boolean)
    - player making move on virtual board
    - determining best move
    - computing score for player (returns int)
    - final state (returns bool)
    - event handler for when it's human's turn
    - minimax for AI

    """
    global running, computer, human, turn, colour, FREE_CELLS

    def __init__(self, ply: int, player: Player):
        self.ply = ply
        self.player = player  # corresponding to CPU (for score etc.)
        self.board = np.copy(game_board.board)

    # check whether we hit end of recursion (ply is 0 or one/two players win):
    def end_of_recursion(self) -> bool:
        return self.ply == 0 or is_game_over(self.board) is True or not FREE_CELLS

    # make move (player of colour 'player' drops piece in column 'col'):
    @staticmethod
    def make_move(board, col, player):
        row = next_free_row_on_col(board, col)
        board[row][col] = player  # 1 for human, 2 for CPU

    # compute score for player at a given time:
    def compute_score(self, piece: int) -> int:
        """
        ________________ RULES__________________
        player:

        4-piece sequence --> player_score += 1000
        3-piece sequence --> player_score += 500
        2-piece sequence --> player_score += 250
        1-piece sequence --> player_score += 50

        opponent:
        3-piece sequence --> player_score -= 200
        __________________________
        """

        def compute_score(seq_length: int):
            total = 0
            if seq_length == 1:
                total += 50
            elif seq_length == 2:
                total += 250
            elif seq_length == 3:
                total += 500
            elif seq_length == 4:
                total += 1000
            return total

        # horizontally:
        def horizontal_score() -> int:
            total = 0
            for row in range(ROWS):
                seq_length = 1
                for col in range(COLS - 1):
                    if self.board[row][col] == self.board[row][col + 1] == piece:
                        seq_length += 1
                    else:
                        total += compute_score(seq_length)
                        seq_length = 1
            return total

        # vertically:
        def vertical_score() -> int:
            total = 0
            for col in range(COLS):
                seq_length = 1
                for row in range(ROWS - 1):
                    if self.board[row][col] == self.board[row + 1][col] == piece:
                        seq_length += 1
                    else:
                        total += compute_score(seq_length)
                        seq_length = 1
            return total

        # diagonally:
        def diagonal_score():
            total = 0

            def get_all_diagonals():
                # main diagonals:
                diags = [self.board[::-1, :].diagonal(i) for i in range(-self.board.shape[0] + 1, self.board.shape[1])]
                # secondary diagonals:
                diags.extend(self.board.diagonal(i) for i in range(self.board.shape[1] - 1, -self.board.shape[0], -1))
                diags_list = []
                for i in diags:
                    diags_list.append(list(i))
                return diags_list  # as list

                # all board diagonals:

            diagonals = get_all_diagonals()

            # parse all diagonals to check for 4 identical pieces:
            for diag_i in diagonals:
                seq_length = 1
                for elem in range(len(diag_i) - 1):
                    if diag_i[elem] == diag_i[elem + 1] == piece:
                        seq_length += 1
                    else:
                        total += compute_score(seq_length)
                        seq_length = 1
            return total

        return horizontal_score() + vertical_score() + diagonal_score()

    """ ______________________ EVAL FUNCTION ________________________"""

    # eval function for AI:
    @staticmethod
    def static_eval(human_player: Player, computer_player: Player):
        """
        :param human_player: Player variable for human
        :param computer_player: Player variable for AI
        :return: Player at advantage
        ________________________________________________
        f(n) > 0 --> advantageous for human
        f(n) < 0 --> advantageous for computer
        f(n) = 0 --> no one is at advantage
        _________________________________________________
        f(n) = human.score - computer.score
        """
        return human_player.score - computer_player.score

    """ ________________________  FINAL STATE ________________________"""

    @classmethod
    def is_final_state(cls):
        return is_game_over(game_board.board)

    """ ________________________ HANDLE EVENTS _______________________"""

    # event handler for human player:
    def human_handle_events(self):
        global running, turn, colour, FREE_CELLS
        for event in pygame.event.get():  # the event loop
            if event.type == pygame.QUIT:
                running = False
                exit()  # quit game
            # if it's player's turn:
            if turn == 1 and colour == YELLOW:
                # if mouse click:
                if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN and event.button == left:
                    # piece is dropped; update board
                    # pos = pygame.mouse.get_pos()
                    row = event.pos[0]
                    col = int(np.math.floor(row / SQUARE_SIZE))
                    # get #row where piece is dropped:
                    drop_on_row = next_free_row_on_col(self.board, col)
                    piece = Piece(colour, self.board)
                    # update board:
                    if drop_on_row != -1:  # if column is not empty and piece can be dropped:
                        piece.drop_piece(self.board, colour, drop_on_row, col)  # drop piece
                        FREE_CELLS = decrement(FREE_CELLS)  # update number of board free cells
                        game_board.draw_board()  # update GUI board
                        print_board(self.board)  # print board
                        colour, turn = switch_player(colour, turn)  # switch players
                        # update score:
                        if turn == 2:
                            computer.inc_score()
                        else:
                            human.inc_score()
                    # update real board:
                    game_board.board = np.copy(self.board)

                # if mouse is moving, make ball appear like it's in motion:
                elif event.type == pygame.MOUSEMOTION:
                    # position to drop piece:
                    row = event.pos[0]
                    # moving piece to drop:
                    pygame.draw.rect(screen, WHITE, (0, 0, SQUARE_SIZE * COLS, SQUARE_SIZE))
                    pygame.draw.circle(screen, colour, (row, SQUARE_SIZE // 2), RADIUS)

                # update window:
                pygame.display.update()

    # pick optimal move for player of colour 'piece':
    def best_move(self, board, available_moves: [], piece: int, best_score, max_player: int):
        """
        :param board: virtual board
        :param available_moves: list of available columns for dropping piece
        :param piece: value corresponding to player in virtual board (1 for human, 2 for CPU)
        :param best_score: value determining the best column to drop piece out of all options
        :param max_player: int value of either 1 or 2, corresponding to player
        :return: optimal column and its score

        """
        # for better randomization:
        random.shuffle(available_moves)
        # by default, optimal column will be the first available one:
        optimal_column = first_available_column(board)
        # calculating score for every available column:
        for col in available_moves:
            row = next_free_row_on_col(board, col)
            temp_board = board.copy()
            piece_to_drop = Piece(piece, temp_board)
            # drop piece of colour 'piece'
            piece_to_drop.drop_piece(temp_board, piece, row, col)
            self.make_move(temp_board, col, piece)
            score = 0  # score(board, player)
            # for maximizing player, score must be maximized:
            if max_player == 2:
                if score > best_score:
                    best_score = score
                    optimal_column = col
            # for minimizing player, score must be minimized:
            elif max_player == 1:
                if score < best_score:
                    best_score = score
                    optimal_column = col
        return optimal_column, best_score

    """ ___________________________ MINIMAX __________________________"""

    def minimax(self, board, ply_level, alpha, beta, max_player):
        """
        :param board: virtual board game
        :param ply_level: current ply level
        :param alpha:
        :param beta:
        :param max_player: maximizing player (1 for human, 2 for computer)
        :return: new game state
        """
        # first, get available moves:
        available_columns = get_available_moves(game_board.board)

        # is end of recursion?
        if self.end_of_recursion() is True:
            # if either player wins:
            if is_game_over(board):
                if check_win(board, YELLOW):     # player wins
                    return 100000000000000, None
                elif check_win(board, RED):      # computer wins
                    return -100000000000000, None
                else:
                    return 0, None  # tie
            # else, if we reach ply level 0:
            elif ply_level == 0:
                return self.compute_score(2)     # return AI score

        # maximizing player's turn:
        if turn == max_player:
            val = -100000000000000
            column, val = self.best_move(board, available_columns, max_player, val, max_player)
            return column, val

        # minimizing player's turn:
        else:
            val = 100000000000000
            column, val = self.best_move(board, available_columns, 3 - max_player, val, 3 - max_player)
            return column, val


def single_player():
    global turn, running, FIRST_PLAYER, colour, game_board, FREE_CELLS

    # difficulty: easy
    # strategy: random
    class Easy(AI):
        while running:
            for event in pygame.event.get():  # the event loop

                if event.type == pygame.QUIT:
                    running = False
                    exit()  # quit game

                # if mouse click:
                elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN and event.button == left:
                    # piece is dropped; update board
                    pos = pygame.mouse.get_pos()
                    row = event.pos[0]
                    col = int(np.math.floor(row / SQUARE_SIZE))
                    # get #row where piece is dropped:
                    drop_on_row = next_free_row_on_col(game_board.board, col)
                    piece = Piece(colour, game_board.board)
                    # update board:
                    if drop_on_row != -1:  # if column is not empty and piece can be dropped:
                        piece.drop_piece(game_board.board, colour, drop_on_row, col)  # drop piece
                        FREE_CELLS = FREE_CELLS - 1
                        game_board.draw_board()  # update GUI board
                        print_board(game_board.board)  # print board
                        colour, turn = switch_player(colour, turn)  # switch players
                        # update score:
                        if turn == 2:
                            computer.inc_score()
                        else:
                            human.inc_score()

                    pygame.display.update()

                # if mouse is moving, make ball appear like it's in motion:
                elif event.type == pygame.MOUSEMOTION:
                    # position to drop piece:
                    row = event.pos[0]
                    # moving piece to drop:
                    pygame.draw.rect(screen, WHITE, (0, 0, SQUARE_SIZE * COLS, SQUARE_SIZE))
                    pygame.draw.circle(screen, colour, (row, SQUARE_SIZE // 2), RADIUS)
                    pygame.display.update()

                # stop condition:
                if is_game_over(game_board.board):
                    # check who won:
                    if winner == 0:
                        print('Tie!\nScore: ', human.score, '-', computer.score, 'Free cells: ', FREE_CELLS)
                        color_fill = YELLOW
                        text_box: str = "Player 1 wins! Congratulations!"
                    elif winner == 1:
                        print('You won!\nScore:', human.score, '-', computer.score, '\nFree cells: ', FREE_CELLS)
                        color_fill = RED
                        text_box: str = "Player 2 wins! Congratulations!"
                    else:  # if winner == 3
                        print('You lost!\nTotal score:', human.score, '-', computer.score, '\nFree cells: ', FREE_CELLS)
                        color_fill = BLACK
                        text_box: str = "That was a close one! Tie."
                    # update GUI board:

                    screen.fill(color_fill)  # set background colour to white
                    pygame.display.set_caption(TITLE)  # set title of the window
                    winner_box = BoxMessage(H // 3, W // 3, W / 2, 32, text_box)
                    winner_box.draw()
                    pygame.display.update()
                    time.sleep(2)  # sleep for two seconds after showing winner
                    # stop program from running:
                    running = False

                # update screen:
                pygame.display.update()

    # difficulty: medium
    # strategy: random
    class Medium(AI):
        pass

    # difficulty: hard
    # strategy: random
    class Hard(AI):
        pass


# play Connect-4 with a different opponent:
def multiplayer():
    global game_board, running, FREE_CELLS, turn, colour
    while running:
        for event in pygame.event.get():  # the event loop

            if event.type == pygame.QUIT:
                running = False
                exit()  # quit game

            # if mouse click:
            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN and event.button == left:
                # piece is dropped; update board
                pos = pygame.mouse.get_pos()
                row = event.pos[0]
                col = int(np.math.floor(row / SQUARE_SIZE))
                # get #row where piece is dropped:
                drop_on_row = next_free_row_on_col(game_board.board, col)
                piece = Piece(colour, game_board.board)
                # update board:
                if drop_on_row != -1:  # if column is not empty and piece can be dropped:
                    piece.drop_piece(game_board.board, colour, drop_on_row, col)  # drop piece
                    FREE_CELLS = FREE_CELLS - 1
                    game_board.draw_board()  # update GUI board
                    print_board(game_board.board)  # print board
                    colour, turn = switch_player(colour, turn)  # switch players
                    # update score:
                    if turn == 2:
                        computer.inc_score()
                    else:
                        human.inc_score()

                pygame.display.update()

            # if mouse is moving, make ball appear like it's in motion:
            elif event.type == pygame.MOUSEMOTION:
                # position to drop piece:
                row = event.pos[0]
                # moving piece to drop:
                pygame.draw.rect(screen, WHITE, (0, 0, SQUARE_SIZE * COLS, SQUARE_SIZE))
                pygame.draw.circle(screen, colour, (row, SQUARE_SIZE // 2), RADIUS)
                pygame.display.update()

            # stop condition:
            if is_game_over(game_board.board):
                # check who won:
                if winner == 0:
                    print('Tie!\nScore: ', human.score, '-', computer.score, 'Free cells: ', FREE_CELLS)
                    color_fill = YELLOW
                    text_box: str = "Player 1 wins! Congratulations!"
                elif winner == 1:
                    print('You won!\nScore:', human.score, '-', computer.score, '\nFree cells: ', FREE_CELLS)
                    color_fill = RED
                    text_box: str = "Player 2 wins! Congratulations!"
                else:  # if winner == 3
                    print('You lost!\nTotal score:', human.score, '-', computer.score, '\nFree cells: ', FREE_CELLS)
                    color_fill = BLACK
                    text_box: str = "That was a close one! Tie."
                # update GUI board:

                screen.fill(color_fill)  # set background colour to white
                pygame.display.set_caption(TITLE)  # set title of the window
                winner_box = BoxMessage(H // 3, W // 3, W / 2, 32, text_box)
                winner_box.draw()
                pygame.display.update()
                time.sleep(2)  # sleep for two seconds after showing winner
                # stop program from running:
                running = False

            # update screen:
            pygame.display.update()


def play_game():
    if OPPONENT == 'human':
        multiplayer()
    elif OPPONENT == 'computer':
        # create difficulty level buttons:

        level_box_easy = BoxMessage((W-W/3)/2, H/ROWS, W/3*COLS/3, 32, 'Easy')
        level_box_medium = BoxMessage((W-W/3)/2, H/ROWS + 64, W/3*COLS/3, 32, 'MEDIUM')
        level_box_hard = BoxMessage((W-W/3)/2, H/ROWS + 128, W/3*COLS/3, 32, 'HARD')

        boxes = [level_box_easy, level_box_medium, level_box_hard]

        # updating interface:
        screen.fill(WHITE)
        pygame.display.flip()
        pygame.display.update()
        # drawing boxes:
        for box in boxes:
            box.draw()
        
        # choose difficulty level
        for box in boxes:
            # box.click_box(event)
            pass
        # create correspondent AI object
        # play
        pass


if __name__ == "__main__":
    play_game()
    pygame.quit()

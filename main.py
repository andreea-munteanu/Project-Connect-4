from turtle import left
import pygame
import numpy as np

# reading input from input file:
with open('4inaROW.txt', 'r') as file:
    content = file.read()
    OPPONENT, ROWS, COLS, FIRST_PLAYER = content.split()
    ROWS, COLS = int(ROWS), int(COLS)
    # print("OPPONENT =", OPPONENT, ', ROWS = ', ROWS, ', COLS = ', COLS, ', FIRST PLAYER = ', FIRST_PLAYER)
    assert ROWS >= 4 and COLS >= 4, 'Board must be at least 4x4.'
file.close()

# virtual board
board = np.zeros((ROWS, COLS))  # at first, board is free

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
RADIUS = SQUARE_SIZE // 2 - 5

pygame.init()
TITLE = 'Connect-Four Game'
icon = pygame.image.load('connect4.png')  # icon
pygame.display.set_icon(icon)
screen = pygame.display.set_mode(WINDOW_SIZE)  # set window size
screen.fill(WHITE)  # set background colour to white
pygame.display.set_caption(TITLE)  # set title of the window
clock = pygame.time.Clock()  # create clock so that game doesn't refresh that often


# class for piece on the board
class Piece(object):
    def __init__(self, my_colour):
        self.colour = my_colour

    # draw coloured piece at position (row, col):
    def draw_piece(self, circle_colour, row, col):
        pygame.draw.circle(screen, circle_colour,
                           (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2 + SQUARE_SIZE),
                           RADIUS)
        pygame.display.update()


# update board after dropping piece at position (row, col)
def drop_piece(colour, row, col):
    # 1 for player, 2 for CPU
    if colour == YELLOW:
        board[row][col] = 1
    elif colour == RED:
        board[row][col] = 2


# get next free row on column col
def last_free_row_on_col(column):
    last = -1
    for i in range(0, ROWS):
        if board[i][column] == 0:
            last = i
        else:
            break
    return last  # -1 if column is full


def check_win(colour: (int, int, int)) -> bool:

    # value = None
    # if colour == RED:
    #     value = 2
    # elif colour == YELLOW:
    #     value = 1

    # horizontally:
    def horizontal_win() -> bool:
        # for each row, check whether there are 4 consecutive pieces of the same colour:
        for i in range(ROWS):
            count = 1
            for j in range(COLS-1):
                if board[i][j] == board[i][j + 1] == 1:
                    count += 1
                else:  # if board[i][j] != board[i][j+1]:
                    if count >= 4:
                        return True
                    else:
                        count = 1
        # if no row has 4 consecutive identical pieces:
        return False

    # vertically:
    def vertical_win() -> bool:
        # check whether there are 4 identical pieces on a column:
        for j in range(COLS):
            count = 1
            for i in range(ROWS - 1):
                if board[i][j] == board[i + 1][j] == 1:
                    count += 1
                else:
                    if count >= 4:
                        return True
                    else:
                        count = 1
        return False

    # diagonally:
    def diagonal_win() -> bool:
        def get_all_diagonals(board):  # checked; works
            # main diagonals:
            diags = [board[::-1, :].diagonal(i) for i in range(-board.shape[0] + 1, board.shape[1])]
            # secondary diagonals:
            diags.extend(board.diagonal(i) for i in range(board.shape[1] - 1, -board.shape[0], -1))
            diagonals = []
            for i in diags:
                diagonals.append(list(i))
            return diagonals  # as list

        # all board diagonals:
        diagonals = get_all_diagonals(board)

        for diag_i in diagonals:
            print(diag_i, "  :  ", end='')
            count = 1
            for elem in range(len(diag_i) - 1):
                print(diag_i[elem], end='; ')
                if diag_i[elem] == diag_i[elem + 1] == 1:
                    count = count + 1
                else:
                    if count >= 4:
                        return True
                    count = 1

        return False

    # at least one
    return horizontal_win() or vertical_win() or diagonal_win()


# game is over when one colour wins (or when table is full):
def is_game_over() -> bool:
    return check_win(RED) or check_win(YELLOW) or FREE_CELLS == 0

# class for Board
class GameBoard(object):
    # initialization
    def __init__(self, rows, cols):
        self.rows = ROWS
        self.cols = COLS

    # draw board and its coloured pieces
    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                pygame.draw.rect(screen, BLUE,
                                 (col * SQUARE_SIZE, row * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                circle_colour = (0, 0, 0)
                if board[row][col] == 0:  # free cell
                    circle_colour = WHITE
                elif board[row][col] == 1:  # human player
                    circle_colour = YELLOW
                elif board[row][col] == 2:  # CPU player
                    circle_colour = RED
                # initializing board piece with circle_colour
                board_piece = Piece(circle_colour)
                board_piece.draw_piece(circle_colour, row, col)
        # update display:
        pygame.display.update()

    # printing board in terminal:
    def print_board(self):
        for i in range(ROWS):
            for j in range(COLS):
                if j < COLS - 1:
                    print(board[i][j], end=' ')
                else:
                    print(board[i][j])
        print('\n')

    # determine whether player with colour 'colour' won the game


# class for player (computer or human):
class Player(object):
    def __init__(self, colour, score, ply):  #: (int, int, int), score: int, ply: int):
        self.colour = colour
        self.score = score
        # self.strategy = strategy
        self.ply = ply  # for algorithms

    def inc_score(self):
        self.score += 1


# class for AI:
class AI(object):
    def __init__(self, strategy: str, ply: int, player: Player):
        self.strategy = strategy
        self.ply = ply
        self.player = player  # corresponding to CPU (for score and the like)

    # check locations for win from position(row, col)
    def winning_move(self, colour) -> int:  # returns col
        pass

    # make move (player of colour 'player' drops ball in column #col):
    def make_move(self, col, player):
        row = last_free_row_on_col(col)
        board[row][col] = player  # 1 for human, 2 for CPU


game_board = GameBoard(ROWS, COLS)
game_board.draw_board()

computer = Player(RED, 0, 3)
human = Player(YELLOW, 0, 3)
print(computer)

# initializing first player:
turn, colour = None, None
if FIRST_PLAYER == 'human':
    turn = 1
    colour = YELLOW
elif FIRST_PLAYER == 'computer':
    turn = 2
    colour = RED


def switch_player(colour, turn):
    turn = 3 - turn
    if colour == RED:
        colour = YELLOW
    else:
        colour = RED
    return colour, turn


running = True

while running:
    for event in pygame.event.get():  # the event loop
        if event.type == pygame.QUIT:
            exit()  # quit game

        # if mouse click:
        elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN and event.button == left:
            # piece is dropped; update board
            pos = pygame.mouse.get_pos()
            row, col = event.pos[0], int(np.math.floor(row / SQUARE_SIZE))
            # get #row where piece is dropped:
            drop_on_row = last_free_row_on_col(col)
            # update board:
            if drop_on_row != -1:  # if column is not empty and piece can be dropped:
                drop_piece(colour, drop_on_row, col)  # drop piece
                FREE_CELLS = FREE_CELLS - 1
                game_board.draw_board()  # update GUI board
                game_board.print_board()  # print board
                colour, turn = switch_player(colour, turn)  # switch players
            pygame.display.update()

        # if mouse is moving, make ball appear like it's in motion:
        elif event.type == pygame.MOUSEMOTION:
            piece = Piece(colour)
            # position to drop piece:
            row = event.pos[0]
            # moving piece to drop:
            pygame.draw.rect(screen, WHITE, (0, 0, SQUARE_SIZE * COLS, SQUARE_SIZE))
            pygame.draw.circle(screen, colour, (row, SQUARE_SIZE // 2), RADIUS)
            pygame.display.update()

        # stop condition:
        # if is_game_over():
        #     running = False

        pygame.display.update()

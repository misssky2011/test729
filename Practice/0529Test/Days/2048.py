import randomTest
import os
import sys
import time


# Initialize the game board
def initialize_board():
    board = [[0] * 4 for _ in range (4)]
    return board


# Display the game board
def print_board(board):
    os.system ('cls' if os.name == 'nt' else 'clear')
    print ("2048 Game\n")
    for row in board:
        print ("\t".join (str (num) if num != 0 else '.' for num in row))
        print ()
    print ("Use W/A/S/D to move, Q to quit.\n")


# Add a new random tile (2 or 4) in a random empty spot
def add_random_tile(board):
    empty_cells = [(r, c) for r in range (4) for c in range (4) if board[r][c] == 0]
    if empty_cells:
        r, c = random.choice (empty_cells)
        board[r][c] = random.choice ([2, 4])


# Check if the game is over (no possible moves)
def is_game_over(board):
    for r in range (4):
        for c in range (4):
            if board[r][c] == 0:
                return False
            if r < 3 and board[r][c] == board[r + 1][c]:
                return False
            if c < 3 and board[r][c] == board[r][c + 1]:
                return False
    return True


# Merge a row or column
def merge_line(line):
    non_zero = [num for num in line if num != 0]
    merged = []
    skip = False
    for i in range (len (non_zero)):
        if skip:
            skip = False
            continue
        if i + 1 < len (non_zero) and non_zero[i] == non_zero[i + 1]:
            merged.append (non_zero[i] * 2)
            skip = True
        else:
            merged.append (non_zero[i])
    return merged + [0] * (4 - len (merged))


# Rotate the board 90 degrees clockwise
def rotate_board(board):
    return [[board[3 - r][c] for r in range (4)] for c in range (4)]


# Move the board in a certain direction
def move_board(board, direction):
    if direction == 'w':
        board = rotate_board (board)
        for i in range (4):
            board[i] = merge_line (board[i])
        board = rotate_board (board)
        board = rotate_board (board)
        board = rotate_board (board)
    elif direction == 's':
        board = rotate_board (board)
        board = rotate_board (board)
        board = rotate_board (board)
        for i in range (4):
            board[i] = merge_line (board[i])
        board = rotate_board (board)
    elif direction == 'a':
        for i in range (4):
            board[i] = merge_line (board[i])
    elif direction == 'd':
        for i in range (4):
            board[i] = merge_line (board[i][::-1])[::-1]
    return board


# Main game loop
def game():
    board = initialize_board ()
    add_random_tile (board)
    add_random_tile (board)

    while True:
        print_board (board)
        if is_game_over (board):
            print ("Game Over!")
            break

        move = input ("Move (W/A/S/D): ").lower ()
        if move == 'q':
            print ("Thanks for playing!")
            break
        if move in ['w', 'a', 's', 'd']:
            board = move_board (board, move)
            add_random_tile (board)
        else:
            print ("Invalid move. Use W/A/S/D to move, Q to quit.")
        time.sleep (0.1)


# Run the game
if __name__ == "__main__":
    game ()

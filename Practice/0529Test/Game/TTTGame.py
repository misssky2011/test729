# 定义棋盘大小
BOARD_SIZE = 3

def print_board(board):
    """打印棋盘"""
    for row in board:
        print(" | ".join(row))
        print("-" * (BOARD_SIZE * 4 - 1))

def check_win(board, player):
    """检查是否有玩家获胜"""
    # 检查行
    for row in board:
        if all(cell == player for cell in row):
            return True
    # 检查列
    for col in range(BOARD_SIZE):
        if all(board[row][col] == player for row in range(BOARD_SIZE)):
            return True
    # 检查对角线
    if all(board[i][i] == player for i in range(BOARD_SIZE)):
        return True
    if all(board[i][BOARD_SIZE - 1 - i] == player for i in range(BOARD_SIZE)):
        return True
    return False

def is_board_full(board):
    """检查棋盘是否已满（平局情况）"""
    for row in board:
        if " " in row:
            return False
    return True

def play_game():
    """主游戏函数"""
    board = [[" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    players = ["X", "O"]
    current_player = 0
    print("欢迎来到井字棋游戏！")
    while True:
        print_board(board)
        try:
            # 获取玩家输入的坐标
            row = int(input(f"{players[current_player]} 请输入行（0-{BOARD_SIZE - 1}）: "))
            col = int(input(f"{players[current_player]} 请输入列（0-{BOARD_SIZE - 1}）: "))
            if board[row][col]!= " ":
                print("该位置已经有棋子了，请重新选择位置哦。")
                continue
            board[row][col] = players[current_player]
            if check_win(board, players[current_player]):
                print_board(board)
                print(f"{players[current_player]} 获胜啦！恭喜！")
                break
            elif is_board_full(board):
                print_board(board)
                print("平局啦！")
                break
            current_player = (current_player + 1) % 2
        except ValueError:
            print("请输入有效的整数坐标哦，请重新输入。")
        except IndexError:
            print("输入的坐标超出范围了，请重新输入哦。")


if __name__ == "__main__":
    play_game()
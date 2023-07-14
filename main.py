import time
from chess_bot import ChessBot
print("Please wait")
chess = ChessBot()
chess.login()
time.sleep(1)

color = chess.find_match()

print("Color:", color)
if "white" == color:
    chess.highlight_move("e2e4")
    chess.move_piece()
while True:
    try:
        pgn, last_move = chess.get_pgn('')
        best_move = chess.get_best_move()
        chess.highlight_move(best_move)
        chess.move_piece()
    except Exception as e:
        print(e)
        color = chess.find_match()
        print("Color:",color)
        if "white" == color:
            chess.highlight_move("e2e4")
            chess.move_piece()

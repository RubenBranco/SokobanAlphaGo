class SokobanPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valids = board.get_valid_moves()
        candidates = []

        for action in range(self.game.get_action_size()):
            if valids[action] == 0:
                continue

            next_state = self.game.get_next_state(board, action)
            score = self.game.get_score(next_state)
            candidates.append((-score, action))
        candidates.sort()
        
        return candidates[0][1]

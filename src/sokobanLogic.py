class Board():
    """
    Characters described in https://www.sokoban-online.de/sokoban/levell-format/
    Puzzles should come from http://www.abelmartin.com/rj/sokoban_colecciones.html
    """

    _characters = {
        ' ': 0,  # free space
        '@': 1,  # player
        '#': 2,  # wall
        '$': 3,  # box
        '.': 4,  # goal
        '*': 5,  # box in goal
        '+': 6,  # player in goal
    }

    _directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Top, right, down, left

    def __init__(self, text):
        """
        text is the textual representation of a whole sokoban level.
        """
        self.board = []
        self._lines = text.split("\n")

        for i in range(len(self._lines)):
            line = self._lines[i]
            for j, character in enumerate(line):
                self.board[i][j] = self._characters[character]

        self.height = len(self.board)
        self.width = len(self.board[0])

    def __getitem__(self, index):
        return self.board[index]

    def end_test(self):
        """
        Evaluates whether the current state is an end state.
        """
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self[i][j] == "$":
                    return False
        return True

    def get_moves(self):
        """
        Gets all the legal moves.
        """
        playerX, playerY = self._find_player()
        moves = set()

        for direction in self._directions:
            if self[playerX + direction[0]][playerY + direction[1]] != self._characters["#"]:
                moves.add(direction)

        return moves

    def execute_move(self, move):
        """
        Changes the board by executing a move.
        """
        playerX, playerY = self._find_player()
        player_character = self[playerX][playerY]
        target_pos_x, target_pos_y = playerX + move[0], playerY + move[1]
        direction_id = self._directions.index(move)

        # Is it a move where you don't push a box
        if self[target_pos_x][target_pos_y] != self._characters["$"] and self[target_pos_x][target_pos_y] != self._characters["*"]:
            # The new location
            if self[target_pos_x][target_pos_y] == self._characters["."]:
                self[target_pos_x][target_pos_y] = self._characters["+"]
            else:
                self[target_pos_x][target_pos_y] = self._characters["@"]

            # old location
            if player_character == self._characters["+"]:
                self[playerX][playerY] = self._characters["."]
            else:
                self[playerX][playerY] = self._characters[" "]

        # or is it a push move
        else:
            if direction_id == 0:  # top
                beyond_pos_x, beyond_pos_y = target_pos_x, target_pos_y - 1
            elif direction_id == 1:  # right
                beyond_pos_x, beyond_pos_y = target_pos_x + 1, target_pos_y
            elif direction_id == 2:  # down
                beyond_pos_x, beyond_pos_y = target_pos_x, target_pos_y + 1
            else:  # left
                beyond_pos_x, beyond_pos_y = target_pos_x - 1, target_pos_y
            pass

    def _find_player(self):
        """
        Finds the position x,y of the player.
        """
        for i in range(len(self.board)):
            for j in range(len(self[i])):
                if self[i][j] == self._characters["@"] or self[i][j] == self._characters["+"]:
                    return (i, j)
        return None

        def _get_surrounding_pos(self):
            pass

import numpy as np


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

    _num_to_char = {v: k for k, v in _characters.items()}

    _directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Top, right, down, left

    def __init__(self, text):
        """
        text is the textual representation of a whole sokoban level.
        """
        self._lines = text.split("\n")
        self.width = max(list(map(lambda x: len(self._lines[x]), range(len(self._lines)))))
        self.height = len(self._lines)

        self.board = np.empty((self.width, self.height), dtype=int)
        for i in range(len(self._lines)):
            line = self._lines[i]
            for j, character in enumerate(line):
                self.board[j][i] = self._characters[character]


    # def __getitem__(self, index):
    #     return self.board[index]

    # def __setitem__(self, index, value):
    #     self.board[index] = value

    def __str__(self):
        """
        Returns a string representation of the puzzle state.
        """
        string = ""
        
        for x in range(self.width):
            line_str = ""
            for y in range(self.height):
                line_str += self._num_to_char[self.board[x][y]]
            line_str += "\n"
            string += line_str
        
        return string

    def end_test(self):
        """
        Evaluates whether the current state is an end state.
        """
        for x in range(self.width):
            for y in range(self.height):
                if self._num_to_char[self.board[x][y]] == "$":
                    return False
        return True

    def get_moves(self):
        """
        Gets all the legal moves.
        """
        playerX, playerY = self._find_player()
        moves = set()

        for direction in self._directions:
            target_pos_x, target_pos_y = playerX + direction[0], playerY + direction[1]
            beyond_pos_x, beyond_pos_y = self._get_beyond_coords(self._directions.index(direction))
            target_character = self.board[target_pos_x][target_pos_y]
            beyond_character = self.board[beyond_pos_x][beyond_pos_y]

            if target_character in [self._characters['$'], self._characters['*']]:
                if beyond_character != self._characters['#']:
                    moves.add(direction)
            if target_character != self._characters["#"]:
                moves.add(direction)

        return moves

    def execute_move(self, move):
        """
        Changes the board by executing a move.
        """
        playerX, playerY = self._find_player()
        player_character = self.board[playerX][playerY]
        target_pos_x, target_pos_y = playerX + move[0], playerY + move[1]
        target_character = self.board[target_pos_x][target_pos_y]
        direction_id = self._directions.index(move)
        beyond_pos_x, beyond_pos_y = self._get_beyond_coords(direction_id)
        beyond_character = self.board[beyond_pos_x][beyond_pos_y]

        # Is it a move where you don't push a box
        if target_character != self._characters["$"] and target_character != self._characters["*"]:
            # The new location
            if target_character == self._characters["."]:
                self.board[target_pos_x][target_pos_y] = self._characters["+"]
            else:
                self.board[target_pos_x][target_pos_y] = self._characters["@"]

            # old location
            if player_character == self._characters["+"]:
                self.board[playerX][playerY] = self._characters["."]
            else:
                self.board[playerX][playerY] = self._characters[" "]

        # or is it a push move
        else:
            if beyond_character == self._characters["."]:
                self.board[beyond_pos_x][beyond_pos_y] = self._characters["*"]
            else:
                self.board[beyond_pos_x][beyond_pos_y] = self._characters["$"]

            if target_character == self._characters["*"]:
                self.board[target_pos_x][target_pos_y] = self._characters["+"]
            else:
                self.board[target_pos_x][target_pos_y] = self._characters["@"]

            if player_character == self._characters["+"]:
                self.board[playerX][playerY] = self._characters["."]
            else:
                self.board[playerX][playerY] = self._characters[" "]

    def count_stars(self):
        """
        Verifies the number of boxes in the goal.
        """
        number = 0
        
        for x in range(self.width):
            for y in range(len(self.board[x])):
                if self.board[x][y] == self._characters["*"]:
                    number += 1

        return number
    
    def median_distance(self):
        """
        Returns the median distance of all boxes to all goals using manhattan distance
        """

        def manhattan_distance(coord1, coord2):
            """
            Manhattan distance between two coordinates.
            """
            return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

        boxes = self._find_unattended_boxes()
        goals = self._find_unattended_goals()
        distances = []
        
        for box in boxes:
            for goal in goals:
                distances.append(manhattan_distance(box, goal))
        
        return int(sum(distances) / len(distances)) if distances else 0
        
    def _find_unattended_boxes(self):
        """
        Finds the positions of the unattended(goal-less) boxes.
        """
        positions = []

        for x in range(self.width):
            for y in range(self.height):
                if self.board[x][y] == self._characters["$"]:
                    positions.append((x,y))

        return positions

    def _find_unattended_goals(self):
        """
        Finds the position of all goals without a box.
        """
        positions = []

        for x in range(self.width):
            for y in range(self.height):
                if self.board[x][y] == self._characters["."]:
                    positions.append((x,y))

        return positions

    def _find_player(self):
        """
        Finds the position x,y of the player.
        """
        for x in range(self.width):
            for y in range(self.height):
                if self.board[x][y] == self._characters["@"] or self.board[x][y] == self._characters["+"]:
                    return (x, y)
        return None

    def _get_beyond_coords(self, direction_id):
        """
        Gets the coordinates equivelant of travelling 2 squares in one direction.
        """
        move = self._directions[direction_id]
        playerX, playerY = self._find_player()
        target_pos_x, target_pos_y = playerX + move[0], playerY + move[1]

        if direction_id == 0:  # top
            beyond_pos_x, beyond_pos_y = target_pos_x, target_pos_y - 1
        elif direction_id == 1:  # right
            beyond_pos_x, beyond_pos_y = target_pos_x + 1, target_pos_y
        elif direction_id == 2:  # down
            beyond_pos_x, beyond_pos_y = target_pos_x, target_pos_y + 1
        else:  # left
            beyond_pos_x, beyond_pos_y = target_pos_x - 1, target_pos_y

        return beyond_pos_x, beyond_pos_y

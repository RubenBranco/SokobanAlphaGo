import numpy as np
import sys
sys.path.append('pytorch_classification')
from pytorch_classification.utils import Bar, AverageMeter
import time


class Arena():
    def __init__(self, player, game, display=None, time_out=10000):
        """
        Input:
            player 1: one function that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it. 
                    Is necessary for verbose mode.
        """
        self.player = player
        self.game = game
        self.display = display
        self.time_out = time_out

    def playGame(self, verbose=False):
        """
        Executes one episode of a game.
        Returns:
            either
                1 if solved
            or
                0 if not
        """
        board = self.game.get_initial_board()
        it = 0
        while self.game.has_puzzle_ended(board) == 0 and it < self.time_out:
            it += 1
            if verbose:
                assert(self.display)
                print("Turn ", str(it))
                self.display(board)
            action = self.player(board)

            valids = self.game.get_valid_moves(
                board, 1)

            if valids[action] == 0:
                print(action)
                assert valids[action] > 0
            board = self.game.get_next_state(board, action)
        if verbose:
            assert(self.display)
            print("Game over: Turn ", str(it), "Result ",
                  str(self.game.has_puzzle_ended(board)))
            self.display(board)
        return self.game.has_puzzle_ended(board)

    def playGames(self, num, verbose=False):
        """
        Plays num games.
        Returns:
            solved: number of solved puzzles
            timed_out: number of timed_out puzzles
        """
        eps_time = AverageMeter()
        bar = Bar('Arena.playGames', max = num)
        end = time.time()
        eps = 0
        maxeps = int(num)

        num = int(num / 2)
        solved = 0
        timed_out = 0

        for _ in range(num):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == 1:
                solved += 1
            else:
                timed_out += 1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=maxeps, et=eps_time.avg,
                                                                                                       total=bar.elapsed_td, eta=bar.eta_td)
            bar.next()

        bar.finish()

        return solved, timed_out

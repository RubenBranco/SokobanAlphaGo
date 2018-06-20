from mcts import MCTS
import numpy as np
from collections import deque
import sys
sys.path.append('pytorch_classification')
from pytorch_classification.utils import Bar, AverageMeter
import time
from random import shuffle
import os
from arena import Arena
from pickle import Pickler, Unpickler
import sys


class Coach():
    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.mcts = MCTS(self.game, self.nnet, self.args)
        self.train_history = []
        self.skip_first = False

    def executeEpisode(self):
        """
        This function executes one episode of self-play.
        As the puzzle is explored, each turn is added as a training example to
        trainExamples. The game is played till the puzzle ends or the limit is reached. 
        After the puzzle ends, the outcome of the game is used to assign values to 
        each example in trainExamples.
        It uses a temp=1 if episodeStep < tempThreshold, and thereafter
        uses temp=0.
        Returns:
            trainExamples: a list of examples of the form (canonicalBoard,pi,v)
                            pi is the MCTS informed policy vector.
        """
        trainExamples = []
        board = self.game.get_initial_board()
        episodeStep = 0

        while True:
            episodeStep += 1
            canonicalBoard = board
            temp = int(episodeStep < self.args.tempThreshold)

            pi = self.mcts.getActionProb(canonicalBoard, temp=temp)
            sym = self.game.get_symmetries(canonicalBoard, pi)
            for b, p in sym:
                trainExamples.append([b, p, None])

            action = np.random.choice(len(pi), p=pi)
            board = self.game.get_next_state(board, action)

            r = self.game.has_puzzle_ended(board)

            if r != 0:
                return [(x[0], x[1], r) for x in trainExamples]

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximium length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it solves >= updateThreshold fraction of puzzles.
        """

        for i in range(1, self.args.numIters + 1):
            # bookkeeping
            print('------ITER ' + str(i) + '------')
            # examples of the iteration
            if not self.skip_first or i > 1:
                iterationTrainExamples = deque(
                    [], maxlen=self.args.maxlenOfQueue)

                eps_time = AverageMeter()
                bar = Bar('Self Play', max=self.args.numEps)
                end = time.time()

                for eps in range(self.args.numEps):
                    # reset search tree
                    self.mcts = MCTS(self.game, self.nnet, self.args)
                    iterationTrainExamples += self.executeEpisode()

                    # bookkeeping + plot progress
                    eps_time.update(time.time() - end)
                    end = time.time()
                    bar.suffix = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps+1, maxeps=self.args.numEps, et=eps_time.avg,
                                                                                                               total=bar.elapsed_td, eta=bar.eta_td)
                    bar.next()
                bar.finish()

                # save the iteration examples to the history
                self.train_history.append(iterationTrainExamples)

            if len(self.train_history) > self.args.numItersForTrainExamplesHistory:
                print("len(trainExamplesHistory) =", len(
                    self.train_history), " => remove the oldest trainExamples")
                self.train_history.pop(0)
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)
            self.saveTrainExamples(i - 1)

            # shuffle examlpes before training
            trainExamples = []
            for e in self.train_history:
                trainExamples.extend(e)
            shuffle(trainExamples)

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(
                folder=self.args.checkpoint, filename='temp.pth.tar')

            self.nnet.train(trainExamples)
            nmcts = MCTS(self.game, self.nnet, self.args)

            print('PITTING AGAINST PREVIOUS VERSION')
            arena = Arena(lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), self.game)
            wins, timeouts = arena.playGames(self.args.arenaCompare)

            if wins + timeouts > 0 and float(wins)/(wins + timeouts) < self.args.updateThreshold:
                print('REJECTING NEW MODEL')
                self.nnet.load_checkpoint(
                    folder=self.args.checkpoint, filename='temp.pth.tar')
            else:
                print('ACCEPTING NEW MODEL')
                self.nnet.save_checkpoint(
                    folder=self.args.checkpoint, filename=self.getCheckpointFile(i))
                self.nnet.save_checkpoint(
                    folder=self.args.checkpoint, filename='best.pth.tar')

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(
            folder, self.getCheckpointFile(iteration) + ".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.train_history)
        f.closed

    def loadTrainExamples(self):
        modelFile = self.args.load_folder_file
        examplesFile = modelFile + ".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            print("File with trainExamples found. Read it.")
            with open(examplesFile, "rb") as f:
                self.train_history = Unpickler(f).load()
            f.closed
            # examples based on the model were already collected (loaded)
            self.skip_first = True

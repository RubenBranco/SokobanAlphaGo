from sokobanGame import Sokoban as game
import argparse
from nnwrapper import NNetWrapper as nn
from coach import Coach
import torch
import os
import sys


if __name__ == "__main__":
    description = "Sokoban Solver"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-lr', '--learning_rate', dest="lr",
                        type=float, default=0.001, help="Learning Rate")
    parser.add_argument('-dout', '--drop_out', dest="dropout",
                        type=float, default=0.3, help="Drop Out")
    parser.add_argument('-ep', '--epochs', type=int,
                        dest="epochs", default=10, help="Epochs of training")
    parser.add_argument('-bs', '--batch_size', type=int,
                        dest="batch_size", default=64)
    parser.add_argument('-chnm', '--num_channels', type=int,
                        dest="num_channels", default=512)
    parser.add_argument('-iter', '--num_iters', type=int,
                        dest="numIters", default=1000)
    parser.add_argument('-nEps', '--num_eps', type=int,
                        dest="numEps", default=100)
    parser.add_argument("-tmpT", '--temp_threshold',
                        type=int, dest="tempThreshold", default=15)
    parser.add_argument("-uT", "--update_threshold",
                        type=float, dest="updateThreshold", default=0.6)
    parser.add_argument('-qmaxlen', '--max_queue_len',
                        dest='maxlenOfQueue', type=int, default=200000)
    parser.add_argument('-nummcts', '--numMCTS', type=int,
                        dest='numMCTSSims', default=25)
    parser.add_argument("-aComp", "--arenaCompare", type=int,
                        dest='arenaCompare', default=40)
    parser.add_argument('-cpuct', '--cpuct', type=int, dest='cpuct', default=1)
    parser.add_argument('-cp', '--checkpoint',
                        dest='checkpoint', type=str, default='./temp/')
    parser.add_argument('-cuda', '--cuda', dest='cuda', action='store_true',
                        default=torch.cuda.is_available())
    parser.add_argument('-load', '--load_model',
                        dest='load_model', action='store_true')
    parser.add_argument('-loadf', '--load_folder_file',
                        dest='load_folder_file', type=str)
    parser.add_argument('-iterexamp', '--num_iters_example',
                        dest='numItersForTrainExamplesHistory', type=int, default=20)
    args = parser.parse_args()

    fh = open(os.path.join("..", "data", "puzzle1.txt"))
    fcontent = fh.read()
    fh.close()

    sys.setrecursionlimit(10000)
    g = game(fcontent)

    nnet = nn(g, args)

    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file)

    c = Coach(g, nnet, args)
    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
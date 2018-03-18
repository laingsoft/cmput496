"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
import traceback
import sys
import os
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import gtp_connection
import numpy as np
import re

class GtpConnection(gtp_connection.GtpConnection):

    def __init__(self, go_engine, board, outfile = 'gtp_log', debug_mode = False):
        """
        GTP connection of Go1

        Parameters
        ----------
        go_engine : GoPlayer
            a program that is capable of playing go by reading GTP commands
        komi : float
            komi used for the current game
        board: GoBoard
            SIZExSIZE array representing the current board state
        """
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)

    
    def policy_moves_cmd(self, args):

        gtp_connection.GtpConnection.policy_moves_cmd(self, args)
        

    def atari_capture(self):
            #capture the last move if:

            #1 - It only has one liberty left
            #2 - The move is legal



        return None


    def atari_defense(self):
        last_move = board.last_move
        if last_move == None:
            return None

        #Run away / play on the last liberty. only makes sense if there is more than 1 liberty after this

        #capture - getting liberties by capturing stones

        return None

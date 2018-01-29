"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.

Extended for CMPUT496 Assignment 1
"""
import traceback
import sys
import os
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import gtp_connection
import numpy as np
import re

class GtpConnectionGo1(gtp_connection.GtpConnection):

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
        self.commands["hello"] = self.hello_cmd
        
        self.commands["score"] = self.score_cmd
    

    def hello_cmd(self, args):
        """ Dummy Hello Command """
        self.respond("Hello! " + self.go_engine.name)
        
        
    def score_cmd(self, args):
        board = self.board.get_twoD_board()

        #First we count the number of stones
        scores = {1:0, 2:0, 0:0}
        for row in board:
            for position in row:
                scores[position] +=1

        #Next we look at all of the open positions
        #And try to see which territory they are

        # Create some iterators
            

        print(board)
        self.respond(self.floodfill(board, (0,0), []))


 

    def floodfill(self, board, position, closed):
        closed.append(position)
        i, j = position
        
        black, white = False, False
        
        #print((not 0 < i < self.board.size-1) or (not 0 < j < self.board.size-1))
        if (not 0 <= i < self.board.size-1) or (not 0 <= j < self.board.size-1):
            return -1
        
        # A colour of 3 means the whole region is neutral
        color = board[i,j]
        right, left, top, bottom = 0,0,0,0
        if color == 0:
            #only go in 4 directions
            #print(i, j, j > self.board.size-1, self.board.size)
            if (i, j+1) not in closed:
                right = self.floodfill(board, (i, j+1), closed)
                if right == 3: 
                    color = 3
                    return color
            if (i+1, j) not in closed:
                bottom  = self.floodfill(board, (i+1, j), closed)
                if bottom == 3:
                    color = 3
                    return color
            if (i-1, j) not in closed:
                top = self.floodfill(board, (i-1, j), closed)
                if top == 3:
                    color = 3
                    return color
            if (i, j-1) not in closed:
                left = self.floodfill(board, (i, j-1), closed)
                if left == 3:
                    color = 3
                    return color
            #print("RIGHT: {0}, BOTTOM:{1}, LEFT:{2}, TOP: {3}".format(right, bottom, left, top))
            #return(0)
        else:
            if top == 1 or bottom == 1 or left == 1 or right == 1:
                black = True
            if top == 2 or bottom == 2 or left == 2 or right == 2:
                white = True
                
            if black and white:
                color = 3
            elif black:
                color = 1
            elif white:
                color = 2
            
            return color

        #print(right, left, top, bottom)
        #return (right, left, top, bottom)



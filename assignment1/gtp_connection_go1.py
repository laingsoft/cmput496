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

        # First we count the number of stones
        # 1 is black, 2 is white, 0 is border and 3 is neutral
        scores = {1:0, 2:0, 0:0, 3:0}
        for row in board:
            for position in row:
                scores[position] +=1

        # Next we look at all of the open positions and try to see 
        # which territory they are
        
        # Find all empty spaces
        empty_spaces = self.board.get_empty_positions("b")
        
        # Change the empty space array to be zero-indexed
        zero_index = []
        
        for i in empty_spaces:
            tup = self.board._point_to_coord(i)
            zero_index.append((tup[0]-1, tup[1]-1))
        
        # Get the scores for the controlled regions
        for i in zero_index:
            scores[self.floodfill(board, i, [])] += 1
        
        # Finally, add the komi
        scores[2] += self.komi
        
        # Return the winner in the correct format
        # 0 indicates a tie as specified
        if scores[1] > scores[2]:
            self.respond("B+" + str(scores[1]-scores[2]))
        elif scores[2] > scores[1]:
            self.respond("W+" + str(scores[2]-scores[1]))
        else:
            self.respond(0)


    def floodfill(self, board, position, closed):
        closed.append(position)
        i, j = position
        
        black, white = False, False

        if (not 0 <= i < self.board.size) or (not 0 <= j < self.board.size):
            return -1
        
        # A colour of 3 means the whole region is neutral
        color = board[i,j]
        right, left, top, bottom = 0,0,0,0
        if color == 0:
            # Only go in four directions
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

            test = [right, left, bottom, top]
            
            if 1 in test and 2 in test:
                return 3
            else:
                if 1 in test:
                    return 1
                if 2 in test:
                    return 2

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

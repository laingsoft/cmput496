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
import time
import copy

class node:
    def __init__(self, state):
        self.state = state

        
class GtpConnectionGo2(gtp_connection.GtpConnection):

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
        self.commands["go_safe"] = self.safety_cmd
        self.argmap["go_safe"] = (1, 'Usage: go_safe {w,b}')
        
        self.commands["timelimit"] = self.timelimit
        self.argmap["timelimit"] = (1, 'Usage: timelimit seconds')
        self.timelimit = 1

        self.commands["solve"] = self.solve

    def safety_cmd(self, args):
        try:
            color= GoBoardUtil.color_to_int(args[0].lower())
            safety_list = self.board.find_safety(color)
            safety_points = []
            for point in safety_list:
                x,y = self.board._point_to_coord(point)
                safety_points.append(GoBoardUtil.format_point((x,y)))
            self.respond(safety_points)
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))

    def negamax(self, pnode, color, curtime, delta):
        if int(time.time() - curtime) > delta:
            #If the timelimit is passed, just return the heuristic value of the move
            return pnode.state.score(self.go_engine.komi)

        #Generate all of the children of the current node
        children = GoBoardUtil.generate_legal_moves(pnode.state, GoBoardUtil.color_to_int(color))
        #Which value is the best? I dunno?
        best = float("-inf")
        #Children list comes out as a string for some reason.
        children = children.split(" ")
        children.append('')
        #Go through the children
        movew = ''
        for child in children:
            #If the time is expired, return the score and the child
          
            
            nodecopy = node(pnode.state.copy())
            if child == '':
                child = None
                val = nodecopy.state.move(child, GoBoardUtil.color_to_int(color))

            else:
                coord = GoBoardUtil.move_to_coord(child, self.board.size)
                point = self.board._coord_to_point(coord[0], coord[1])
                val = nodecopy.state.move(point, GoBoardUtil.color_to_int(color))

            if nodecopy.state.end_of_game():
                return pnode.state.score(self.go_engine.komi)
            
            if color == "b":
                moved, score = self.negamax(nodecopy, "w", curtime, delta)
            
            else:
                moved, score = self.negamax(nodecopy, "b", curtime, delta)

            #best = max(best, score)
            if(best < -score):
                best = -score
                movew = moved
            if int(time.time() - curtime) > delta:
                # return movew, best
                return pnode.state.score(self.go_engine.komi)
                

        #print("returning")
        print("movew", movew)
        return best, movew

    def timelimit(self, args):
        self.timelimit = int(args[0])
        self.respond("")

    def solve(self, args):
        # Create a copy of our current environment as the root of the tree.
        root = node(self.board)
        negamaxResult = self.negamax(root,
                                                              GoBoardUtil.int_to_color(self.board.current_player),
                                                              time.time(),
                                                              self.timelimit
        )
        #print(negamaxResult)
        self.respond("{0} {1}".format(GoBoardUtil.int_to_color(negamaxResult[0]), ""))
        
        
        

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

    def negamax(self, node, color, curtime, delta):
        if int(time.time() - curtime) > delta:
            return node.state.score
    
        children = GoBoardUtil.generate_legal_moves(node.state, GoBoardUtil.color_to_int(color))
        print(children.split(" "))
        for child in children.split(" "):
            nodecopy = copy.deepcopy(node)
            coord = GoBoardUtil.move_to_coord(child, self.board.size)
            point = self.board._coord_to_point(coord[0], coord[1])
            print(color)
            nodecopy.state.move(point, GoBoardUtil.color_to_int(color))
            print("finally")
            best = float("-inf")
            print("best")
            if color == "b":
                v = self.negamax(nodecopy, "w", time, delta)
                best = max(best, v)
            else:
                print("here")
                v = self.negamax(nodecopy, "b", time, delta)
                print("run")
                best = max(best, v)
            return best

    def timelimit(self, args):
        self.timelimit = args
        self.respond("")

    def solve(self, args):
        # Create a copy of our current environment as the root of the tree.
        root = node(self.board)
        self.respond(self.negamax(root, GoBoardUtil.int_to_color(self.board.current_player), time.time(), self.timelimit))
        
        
        
    

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

    def negamax(self, node, color, curtime, delta, α, β):
        if (int(time.time() - curtime) > delta) or 
            print("score -- ", node.state.score(self.go_engine.komi))
            return node.state.score(self.go_engine.komi)[0]
    
        children = GoBoardUtil.generate_legal_moves(node.state, GoBoardUtil.color_to_int(color))
        best = float("-inf")
        for child in children.split(" "):
            #print("trying", child)
            if int(time.time() - curtime) > delta:
                break
            nodecopy = copy.deepcopy(node)
            if child == '':
                child = None
                nodecopy.state.move(child, GoBoardUtil.color_to_int(color))
            else:
                coord = GoBoardUtil.move_to_coord(child, self.board.size)
                point = self.board._coord_to_point(coord[0], coord[1])
                # print(color)
                # print(coord)
                nodecopy.state.move(point, GoBoardUtil.color_to_int(color))
            if color == "b":
                v = -self.negamax(nodecopy, "w", curtime, delta, -β, -α) #alpha and beta switch with each negamax call
                #print(v)
                best = max(best, v)
            else:
                v = -self.negamax(nodecopy, "b", curtime, delta, -β, -α) #alpha and beta switch with each negamax call
                best = max(best, v)
            α = max( α, v )                 #alpha-beta
            if α ≥ β                        #alpha-beta
                break                       #alpha-beta
        #print("returning")
        return best


    def timelimit(self, args):
        self.timelimit = args
        self.respond("")

    def solve(self, args):
        # Create a copy of our current environment as the root of the tree.
        root = node(self.board)
        α = float("-inf")   #initialized to - infinity
        β = float("inf")    #initialized to +infinity
        self.respond(self.negamax(root, GoBoardUtil.int_to_color(self.board.current_player), time.time(), self.timelimit), α, β) #alpha and beta added
        

        
        
    

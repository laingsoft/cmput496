
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
from feature import Features_weight
from feature import Feature

class sim:
    def __init__(self, move,prob, best_move_prob, strength):
        self.move = move
        self.sim = int(round((prob / best_move_prob) * strength))
        self.winrate = (((prob / best_move_prob)+1) * 0.5)
        self.wins = int(round(round(self.winrate,1)*self.sim))
        
    def __lt__(self, other):
        return self.winrate < other.winrate
        

class GtpConnection(gtp_connection.GtpConnection):

    def __init__(self, go_engine, board, outfile = 'gtp_log', debug_mode = False):
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        
        self.commands["prior_knowledge"] = self.prior_knowledge_cmd
        self.commands["genmove"] = self.genmove_cmd
    
    def prior_knowledge_cmd(self, args):
        moves = []
        gamma_sum = 0.0
        empty_points = self.board.get_empty_points()
        color = self.board.current_player
        probs = np.zeros(self.board.maxpoint)
        all_board_features = Feature.find_all_features(self.board)
        for move in empty_points:
            if self.board.check_legal(move, color) and not self.board.is_eye(move, color):
                moves.append(move)
                probs[move] = Feature.compute_move_gamma(Features_weight, all_board_features[move])
                gamma_sum += probs[move]
        if len(moves) != 0:
            assert gamma_sum != 0.0
            for m in moves:
                probs[m] = probs[m] / gamma_sum
                
        best_move = np.argmax(probs)
        best_move_prob = probs[best_move]
        
        result = []
        for i in moves:
            result.append(sim(i, probs[i], best_move_prob, 10))
            
        result.sort(reverse = True)
        
        response = ""
        for i in result:
            response += str(GoBoardUtil.sorted_point_string([i.move], self.board.NS)) + " " + str(i.wins)+ " " + str(i.sim) + " "
        
        self.respond(response)
        
    def genmove_cmd(self, args):
        """
        generate a move for the specified color

        Arguments
        ---------
        args[0] : {'b','w'}
            the color to generate a move for
            it gets converted to  Black --> 1 White --> 2
            color : {0,1}
            board_color : {'b','w'}
        """
        try:
            board_color = args[0].lower()
            color = GoBoardUtil.color_to_int(board_color)
            self.debug_msg("Board:\n{}\nko: {}\n".format(str(self.board.get_twoD_board()),
                                                          self.board.ko_constraint))
            move = self.go_engine.get_move(self.board, color)
            if move is None:
                self.respond("pass")
                return

            if not self.board.check_legal(move, color):
                move = self.board._point_to_coord(move)
                board_move = GoBoardUtil.format_point(move)
                self.respond("Illegal move: {}".format(board_move))
                raise RuntimeError("Illegal move given by engine")

            # move is legal; play it
            self.board.move(move,color)

            self.debug_msg("Move: {}\nBoard: \n{}\n".format(move, str(self.board.get_twoD_board())))
            move = self.board._point_to_coord(move)
            board_move = GoBoardUtil.format_point(move)
            self.respond(board_move)
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))
            raise
        

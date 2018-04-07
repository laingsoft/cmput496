
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

class GtpConnection(gtp_connection.GtpConnection):

    def __init__(self, go_engine, board, outfile = 'gtp_log', debug_mode = False):
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        
        self.commands["prior_knowledge"] = self.prior_knowledge_cmd
    
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
        print(GoBoardUtil.sorted_point_string([np.argmax(probs)], self.board.NS))
        

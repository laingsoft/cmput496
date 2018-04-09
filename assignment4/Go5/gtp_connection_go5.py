
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
    
    def prior_knowledge_cmd(self, args):
        moves = []
        gamma_sum = 0.0
        empty_points = self.board.get_empty_points()
        color = self.board.current_player
        #probs = np.zeros(self.board.maxpoint)
        probs = {}
        all_board_features = Feature.find_all_features(self.board)
        
        for move in empty_points:
            if self.board.check_legal(move, color) and not self.board.is_eye(move, color):
                moves.append(move)
                probs[move] = Feature.compute_move_gamma(Features_weight, all_board_features[move])
                gamma_sum += probs[move]
                
        #passing is always allowed, add it
        moves.append("PASS")
        probs["PASS"] = Feature.compute_move_gamma(Features_weight, all_board_features["PASS"])
        gamma_sum += probs["PASS"]
        
        if len(moves) != 0:
            assert gamma_sum != 0.0
            for m in moves:
                probs[m] = probs[m] / gamma_sum
 
        best_move = max(probs.items(), key = lambda x: x[1])[0]
        best_move_prob = probs[best_move]
        
        result = []
        for i in moves:
            result.append(sim(i, probs[i], best_move_prob, 10))
            
        result.sort(reverse = True)
        
        response = ""
        for i in result:
            if i.move == "PASS":
                response += "Pass " + str(i.wins)+ " " + str(i.sim) + " "
            else:
                response += str(GoBoardUtil.sorted_point_string([i.move], self.board.NS)) + " " + str(i.wins)+ " " + str(i.sim) + " "
        
        self.respond(response)
        
    

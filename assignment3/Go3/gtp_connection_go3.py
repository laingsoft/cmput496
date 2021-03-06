
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
        self.commands["policy_moves"] = self.policy_moves_cmd
    
    def policy_moves_cmd(self, args):
        #first we need to call the atari_capture
        #first we check the atari capture
        capture_result = self.atari_capture()
        #If it's the first move / no captures go to defense
        if capture_result == None:
            defense_result = self.atari_defense()
            #if the defense is wrong, just do a random / delegate
            if defense_result == None:
                gtp_connection.GtpConnection.policy_moves_cmd(self, args)
            else:
                response = "AtariDefense " + GoBoardUtil.sorted_point_string(defense_result, self.board.NS)
                self.respond(response)
        else:
            response = "AtariCapture " + GoBoardUtil.sorted_point_string(capture_result, self.board.NS)
            self.respond(response)

        
        

    def atari_capture(self):
        #capture the last move if:
        last_move = self.board.last_move
        if last_move == None:
            return None
        opponent = GoBoardUtil.opponent(self.board.current_player)
        x, y = GoBoardUtil.point_to_coord(last_move, self.board.NS)
        
        if (self.board._liberty(last_move, opponent) == 1):
            capture_point = self.board._single_liberty(last_move, opponent)
            bcopy = self.board.copy()
            legal = bcopy.move(capture_point, self.board.current_player)
            filtered_moves = GoBoardUtil.filter_moves(self.board,[capture_point], self.go_engine.check_selfatari)
            if legal and  len(filtered_moves):
                return filtered_moves
        
        
        #1 - It only has one liberty left
        #2 - The move is legal



        return None


    def atari_defense(self):
        last_move = self.board.last_move
        if last_move == None:
            return None
  
        before_last_move = self.board.copy()
        before_last_move.undo_move()
        opponent = GoBoardUtil.opponent(self.board.current_player)

        S, E, S_eyes = self.board.find_S_and_E(self.board.current_player)
        run_moves = []
        for i in S:
            if self.board._liberty(i, self.board.current_player) == 1 and before_last_move._liberty(i, self.board.current_player) != 1:
                #If there is only one liberty, defend it
                #Check if it was only the last move
                
                run_away_point = self.board._single_liberty(i, self.board.current_player)
                bcopy = self.board.copy()
                bcopy.move(run_away_point, self.board.current_player)
                if bcopy._liberty(run_away_point, self.board.current_player) > 1:
                    run_moves.append(run_away_point)
                #next check if capturing any of the opponents stones would increase the liberty
                sprime, ep, s_prime_eyes = self.board.find_S_and_E(opponent)
                for y in sprime:
                    capture_point = self.board._single_liberty(y, opponent)
                    bcopy = self.board.copy()
                    bcopy.move(capture_point, self.board.current_player)
                    if(bcopy._liberty(i, self.board.current_player) > 1):      
                        run_moves.append(capture_point)

        filtered_moves = GoBoardUtil.filter_moves(self.board,run_moves, self.go_engine.check_selfatari)
        if not len(filtered_moves):
            return None
        else:
            return run_moves


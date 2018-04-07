
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
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        
        self.commands["prior_knowledge"] = self.prior_knowledge_cmd
    
    def prior_knowledge_cmd(self, args):
        
        self.respond("Not implemented")

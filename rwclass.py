# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 20:31:30 2016

@author: sylom
"""

import pickle

class RWClass:
    
    @staticmethod
    def readFile(file):
        with open(file, 'rb') as f:
            return pickle.load(f)
            
    @staticmethod
    def writeFile(file,obj):
        with open(file, 'wb') as f:
            return pickle.dump(obj,f)
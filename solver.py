# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 20:27:44 2016

@author: sylom
"""

class AC3:
    
    def __init__(self,X,D,C):
        (R1,R2) = C
        self.X = X
        self.D = D
        self.R1 = R1
        self.R2 = R2
        
    def arcReduce(self,x,y):
        change = False
        for vx in self.D[x]:
            if all( any( not(c(vx,vy)) for c in self.R2[(x,y)]) for vy in self.D[y]):
                self.D[x].remove(vx)
                change = True
        return change
        
    def solve(self):
        self.ac3()
        return (self.X,self.D, (self.R1,self.R2))
            
    def ac3(self):
        for x in self.X:
            for c in self.R1[x]:
                self.D[x] = list(filter(c,self.D[x]))
        worklist = list(self.R2.keys())
        while worklist:
            (x,y) = worklist.pop()
            if self.arcReduce(x,y):
                worklist = list(set(list(filter(lambda c: not(c[0] == y) and c[1] == x, list(self.R2.keys()))) + worklist))
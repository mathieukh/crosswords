# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 19:49:12 2016

@author: sylom
"""
import numpy as np
import crossword as cr

array = np.array(
[
    ['-','-','-','-','*','-','-','-','-'],
    ['-','*','-','*','*','*','-','*','-'],
    ['-','-','-','-','*','-','-','-','-'],
    ['*','-','*','-','-','-','*','-','*'],
    ['-','-','-','-','*','-','-','-','-'],
    ['*','-','*','-','-','-','*','-','*'],
    ['-','-','-','-','*','-','-','-','-'],
    ['-','*','-','*','*','*','-','*','-'],
    ['-','-','-','-','*','-','-','-','-']
]);

dico = [line.rstrip('\n') for line in open('850-mots-us.txt')]

"""
dico = []
dico += ['SITE','CANS']
dico += ['BEES','SIDE']
dico += ['ANT', 'SUN']
dico += ['IDAS','AXIS','IDLY','DEER','EAST','READ','SUB','IVE','ENDED','TEE','LOS','SASSY','STAND','ALI','EVE','DRIVE','RED','SEE']
"""

crossword = cr.Crossword(array, dico)

a = cr.Crossword.generateCrossword(8,8,20)
#crossword.displayCrossword()

#sol = crossword.CSP.solve()

#crosswordSolved = crossword.getCrossword()
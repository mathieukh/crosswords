# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 19:49:12 2016

@author: sylom
"""

import crossword as cr
import numpy as np

arrayA = np.array(
[
    ['-','-','-','*','*'],
    ['-','-','-','-','*'],
    ['-','-','-','-','-'],
    ['*','-','-','-','-'],
    ['*','*','-','-','-'],
]);

arrayB = np.array(
[
    ['*','-','-','-','*','*','*'],
    ['-','-','-','-','-','*','*'],
    ['-','-','*','-','-','-','*'],
    ['-','-','-','-','-','-','-'],
    ['*','-','-','-','*','-','-'],
    ['*','*','-','-','-','-','-'],
    ['*','*','*','-','-','-','*'],
]);

arrayC = np.array(
[
    ['*','*','*','-','-','-','*','*','*'],
    ['*','*','-','-','-','-','-','*','*'],
    ['*','-','-','-','-','-','-','-','*'],
    ['-','-','-','-','*','-','-','-','-'],
    ['-','-','-','*','*','*','-','-','-'],
    ['-','-','-','-','*','-','-','-','-'],
    ['*','-','-','-','-','-','-','-','*'],
    ['*','*','-','-','-','-','-','*','*'],
    ['*','*','*','-','-','-','*','*','*']
]);

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



dico850 = [str.upper(line.rstrip('\n')) for line in open('850-mots-us.txt')]
dico22600 = [str.upper(line.rstrip('\n')) for line in open('22600-mots-fr.txt')]
dico58000 = [str.upper(line.rstrip('\n')) for line in open('58000-mots-us.txt')]

dico850_valued = [ (d,0) for d in dico850]
dicoReduit = [str.upper(line.rstrip('\n')) for line in open('dico_androide.txt')]
dicoReduit_valued = [ (d,1) for d in dicoReduit]
dico_v =  dicoReduit_valued + dico850_valued

C = cr.getCrossword(array)
#cr.solve_valued(C,dico_v)
cr.solve(C,dico850)
cr.displayCrossword(C)
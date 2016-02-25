# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 16:59:14 2016

@author: Lucie
"""

from tkinter import*
import numpy as np

fenetre = Tk()

cases=[]

array = np.array([['-','*','-','-'],
                  ['*','-','*','-']]);

l=0
c=0


for ligne in array:
    l=l+1
    larg=ligne.size
    for colonne in ligne:
        c=c+1
        if(colonne=='-'):
            Button(fenetre, bg="white", width=5, height=2).grid(row=l, column=c-(l-1)*larg)
        elif(colonne=='*'):
            Button(fenetre, bg="black", width=5, height=2).grid(row=l, column=c-(l-1)*larg)
        else:
            Button(fenetre, text='%s' %colonne, bg="white", width=5, height=2).grid(row=l, column=c-(l-1)*larg)
        
 
def alert():
    showinfo("alerte", "Bravo!")

menubar = Menu(fenetre)

menu1 = Menu(menubar, tearoff=0)
menu1.add_command(label="Créer", command=alert)
menu1.add_command(label="Editer", command=alert)
menu1.add_separator()
menu1.add_command(label="Quitter", command=fenetre.quit)
menubar.add_cascade(label="Fichier", menu=menu1)

menu2 = Menu(menubar, tearoff=0)
menu2.add_command(label="Couper", command=alert)
menu2.add_command(label="Copier", command=alert)
menu2.add_command(label="Coller", command=alert)
menubar.add_cascade(label="Editer", menu=menu2)

menu3 = Menu(menubar, tearoff=0)
menu3.add_command(label="A propos", command=alert)
menubar.add_cascade(label="Aide", menu=menu3)

fenetre.config(menu=menubar)      

fenetre.mainloop()
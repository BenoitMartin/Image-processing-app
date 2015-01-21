from __future__ import division
from Tkinter import *
from tkFileDialog import askopenfilename
import Image, ImageTk
import sys
import cv
import numpy

def simple_region_growing(img, seed, threshold=20, conn=8):
    """
Cet algorithme extrait une region de l'image en entree dependant de la position de depart et des conditions d'arrets.
L'image en entree doit etre une image 8 bit and la graine un pixel aux coordonnees (x,y).
Le seuil corresponds a la difference entre l'intensite du pixel exterieur et l'intensite de la region.
Si il n'y a pas de nouveau pixel trouve, l'algorithme s'arrete.
La connexite peut etre de 4 ou 8. En sortie, nous avons une image 8 bits (0 ou 255). L'extrait de la region selectionnee est mis en avant en blanc.

"""

#On recupere les dimensions de l'image
    try:
        dims = cv.GetSize(img)
    except TypeError:
        raise TypeError("(%s) img : IplImage attendue!" % (sys._getframe().f_code.co_name))

# On teste l'image
    if not(img.depth == cv.IPL_DEPTH_8U):
        raise TypeError("(%s) 8U image attendue!" % (sys._getframe().f_code.co_name))
    elif not(img.nChannels is 1):
        raise TypeError("(%s) 1C image attendue!" % (sys._getframe().f_code.co_name))
		
# On teste le seuil des pixels en fonction de leur intensite
    if (not isinstance(threshold, int)) : 
        raise TypeError("(%s) Int attendu!" % (sys._getframe().f_code.co_name))
    elif threshold < 0:
        raise ValueError("(%s) Valeur positive attendu!" % (sys._getframe().f_code.co_name))
		
# On teste la graine (points remarquables de l'image)
    if not((isinstance(seed, tuple)) and (len(seed) is 2) ) : 
        raise TypeError("(%s) (x, y) variable attendus!" % (sys._getframe().f_code.co_name))
    
    if (seed[0] or seed[1] ) < 0 :
        raise ValueError("(%s) La graine doit avoir des valeurs positives!" % (sys._getframe().f_code.co_name))
    elif ((seed[0] > dims[0]) or (seed[1] > dims[1])):
        raise ValueError("(%s) Les valeurs de la graine sont superieures a la taille de l'image!" % (sys._getframe().f_code.co_name))
    
# On teste la connexite
    if (not isinstance(conn, int)) : 
        raise TypeError("(%s) Int attendu!" % (sys._getframe().f_code.co_name))
    if conn == 4:
        orient = [(1, 0), (0, 1), (-1, 0), (0, -1)] # connexite 4
    elif conn == 8:
        orient = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)] # connexite 8
    else:
        raise ValueError("(%s) Type de connexite inconnu (4 ou 8 disponibles)!" % (sys._getframe().f_code.co_name))

    reg = cv.CreateImage( dims, cv.IPL_DEPTH_8U, 1)
    cv.Zero(reg)

#Parametres
    mean_reg = float(img[seed[1], seed[0]])
    size = 1
    pix_area = dims[0]*dims[1]

    contour = [] # Deviendra [ [[x1, y1], val1],..., [[xn, yn], valn] ]
    contour_val = []
    dist = 0

    cur_pix = [seed[0], seed[1]]

#Dispersion
    while(dist<threshold and size<pix_area):
    #Ajout des pixels
        for j in range(len(orient)):
            #Selection d'un nouveau candidat
            temp_pix = [cur_pix[0] +orient[j][0], cur_pix[1] +orient[j][1]]

            #On verifie qu'il appartienne a l'image
            is_in_img = dims[0]>temp_pix[0]>0 and dims[1]>temp_pix[1]>0 #on retourne un booleen
            #On selectionne ce candidat si il n'a jamais ete pris avant
            if (is_in_img and (reg[temp_pix[1], temp_pix[0]]==0)):
                contour.append(temp_pix)
                contour_val.append(img[temp_pix[1], temp_pix[0]] )
                reg[temp_pix[1], temp_pix[0]] = 150
        #On ajoute le pixel du contour le plus proche dedans

        dist = abs(int(numpy.mean(contour_val)) - mean_reg)

        dist_list = [abs(i - mean_reg) for i in contour_val ]
        dist = min(dist_list)    #On recupere la distance minimale
        index = dist_list.index(min(dist_list)) #Indice moyen de la distance
        size += 1 # Mise a jour de la taille de la region
        reg[cur_pix[1], cur_pix[0]] = 255

        #La mise a jour implique que la taille soit un reel( un flottant)
        mean_reg = (mean_reg*size + float(contour_val[index]))/(size+1)
        #Mise a jour de la graine
        cur_pix = contour[index]

        #Suppression du pixel du voisinage
        del contour[index]
        del contour_val[index]       

    return reg



if __name__ == "__main__":
    root = Tk()

    #Mise en place d'un canvas avec des scrollbar (barre de defilement)
    frame = Frame(root, bd=2, relief=SUNKEN)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    xscroll = Scrollbar(frame, orient=HORIZONTAL)
    xscroll.grid(row=1, column=0, sticky=E+W)
    yscroll = Scrollbar(frame)
    yscroll.grid(row=0, column=1, sticky=N+S)
    canvas = Canvas(frame, bd=0, xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    xscroll.config(command=canvas.xview)
    yscroll.config(command=canvas.yview)
    frame.pack(fill=BOTH,expand=1)

#On y ajoute l'image en affichant un menu de selection
    File = askopenfilename(parent=root, initialdir="./",title='Choisis ton image')
    img = ImageTk.PhotoImage(Image.open(File))
    canvas.create_image(0,0,image=img,anchor="nw")
    canvas.config(scrollregion=canvas.bbox(ALL))
    
# On calcule l'epaisseur de l'intima-media
    def calctaille(out_img):
    total=0         
    nb=0
    for j in range(0 , cv.GetSize(out_img)[0]):
        cpt=0
        for i in range(0 , cv.GetSize(out_img)[1]):
            if out_img[i,j] == 255:
                cpt += 1
                
        total=total+cpt
        if cpt != 0:
            nb += 1 
    moy = total / nb
    print "La taille est de : " + str(moy)

#Fonction appelee lorsque l'on clique avec la souris
    def printcoords(event):
        #On affiche dans la console les coordonnees X & Y
        print (event.x,event.y)
    seed = (event.x,event.y)
    threshold = 20
    img = cv.LoadImage(File, cv.CV_LOAD_IMAGE_GRAYSCALE)
    out_img = simple_region_growing(img, seed, threshold)
    calctaille(out_img)
    cv.SaveImage('sortie.png', out_img)
    print "Ouvrez le fichier sortie.png pour visualiser"
    #Evenement du clic de la souris
    canvas.bind("<Button 1>",printcoords)
    
    cv.WaitKey(0)
    root.mainloop()
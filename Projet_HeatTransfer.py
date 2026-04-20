#region ATTENTION /!\
# Lorsque vous voulez commencez à coder : Toujours écrire au préalable dans le terminal cette liste de commande (sans le tiret) : 
#   - git status
#   - git fetch origin
#   - git pull
# Lorsque vous avez fini de coder : Toujours écrire dans le termine cette liste de commande (sans le tiret) :
#   - git status
#   - git add .                 Le point est important !
#   - git commit -m"..."        avec ... étant la description de ce que vous avez modifié dans le code 
#   - git push origin main
#endregion

import numpy as np
import matplotlib.pyplot as pltt

#region Dimension de la surface
eM = 20 # cm
eI = 12
eS = 3
eB = 5
lM = 300
hM = 200
hB = 10
k = 1,5

lgMurExterieur = eM - 1
lgIsolant = lgMurExterieur + eI - 1
lgEnduit = lgIsolant + eS - 1
lgMurInterieur = lgEnduit + eB - 1
lgMurInterieurAvantAir = tuple(lgEnduit) + k - 1
lgMurInterieurApresAir = tuple(lgMurInterieur) - k - 1
#endregion

#region Dimension de la matrice
n = hM
m = eM + eI + eS + eB
#endregion

#region Pas
p = 20
#endregion

#region Precision
precisionResultat = 0
precisionAAtteindre = 10e-2
#endregion

#region Compteurs
cptIteration = 0
cptAlveoles = 0
#endregion

temperatureTempon = 0

T=np.zeros((n, m))

for i in range(n):
    T[i][0] = 1
    T[i][m - 1] = 1


while precisionResultat >= precisionAAtteindre :
    precisionResultat = 0
    print("Itirération : ", cptIteration)
    cptIteration += 1
    #region Test si l'on calcule les températures sur la ligne

    for i in range(n):
        for j in range(m):
            temperatureTempon = T[i][j]
            #region Plaque du haut :
            if i == 0 :
                if j == 0 :                                 # Coin B
                    T[i][j] = 1
                elif j < lgMurExterieur :                   # Plaque du haut mur extérieur
                    T[i][j] = 1
                elif j == lgMurExterieur :                  # Coin haut |e| mur extérieur et isolant
                    T[i][j] = 1
                elif j < lgIsolant :                        # Plaque du haut isolant
                    T[i][j] = 1
                elif j == lgIsolant :                       # Coin haut |e| isolant et enduit
                    T[i][j] = 1
                elif j < lgEnduit :                         # Plaque du haut enduit
                    T[i][j] = 1
                elif j == lgEnduit :                        # Coin haut |e| enduit et mur inétieur
                    T[i][j] = 1
                elif j < lgMurInterieur :                   # Plaque du haut mur intérieur
                    T[i][j] = 1
                elif j == lgMurInterieur :                  # Coin C
                    T[i][j] = 1
            #endregion

            #region Centre
            elif i < n and j > 0 :              # |e| la plaque du haut et du bas et après la plaque de gauche
                if j < lgMurExterieur :
                    T[i][j] = 1 
                elif j == lgMurExterieur : 
                    T[i][j] = 1
                elif j < lgIsolant :
                    T[i][j] = 1
                elif j == lgIsolant :
                    T[i][j] = 1
                elif j < lgEnduit :
                    if i % p == 0 and j == eS / 2 :             # Position sur les sources de chaleur (à vérifier si incrément de i ≠ 1cm) => Boucle ?
                        T[i][j] = 1
                    else :
                        T[i][j] = 1
                elif j == lgEnduit :
                    T[i][j] = 1
                elif j < lgMurInterieur :
                    if j < lgMurInterieurAvantAir :
                        T[i][j] = 1
                    elif j == lgMurInterieurAvantAir :
                        T[i][j] = 1
                    elif j < lgMurInterieurApresAir :
                        T[i][j] = 1
                    elif j == lgMurInterieurApresAir :
                        T[i][j] = 1
                elif j == lgMurInterieur :
                    if i == cptAlveoles + k :                      # Problème si incrément de i = 1cm => Boucle ?
                        cptAlveoles += 1 + k

                    

            #endregion


            #region Plaque du bas :
            if i == n :
                if j == 0 :                                 # Coin A
                    T[i][j] = 1
                elif j < lgMurExterieur :                   # Plaque du bas mur extérieur
                    T[i][j] = 1
                elif j == lgMurExterieur :                  # Coin bas |e| mur extérieur et isolant
                    T[i][j] = 1
                elif j < lgIsolant :                        # Plaque du bas isolant
                    T[i][j] = 1
                elif j == lgIsolant :                       # Coin bas |e| isolant et enduit
                    T[i][j] = 1
                elif j < lgEnduit :                         # Plaque du bas enduit
                    T[i][j] = 1
                elif j == lgEnduit :                        # Coin bas |e| enduit et mur inétieur
                    T[i][j] = 1
                elif j < lgMurInterieur :                   # Plaque du bas mur intérieur
                    T[i][j] = 1
                elif j == lgMurInterieur :                  # Coin D
                    T[i][j] = 1
            #endregion
    #endregion

    #region Test si l'on calcule les températures par bloc 
    for i in range(n) :
        for j in range(m) :
            temperatureTempon = T[i][j]
            if j > 0 :
                if j < lgMurExterieur :
                    if i == 0 :
                        T[i][j] = 1
                    elif i == n - 1 :
                        T[i][j] = 1
                    else :
                        T[i][j] = 1
                elif j == lgMurExterieur :
                    if i == 0 :
                        T[i][j] = 1
                    elif i == n - 1 :
                        T[i][j] = 1
                    else :
                        T[i][j] = 1
    for i in range(n) :
        for j in range(m) :
            temperatureTempon = T[i][j]
            if j < lgIsolant :
                if i == 0 :
                    T[i][j] = 1
                elif i == n - 1 :
                    T[i][j] = 1
                else :
                        T[i][j] = 1
            elif j == lgIsolant :
                if i == 0 :
                    T[i][j] = 1
                elif i == n - 1 :
                    T[i][j] = 1
                else :
                    [i][j] = 1
    for i in range(n) :
        for j in range(m) :
            temperatureTempon = T[i][j]
            if j < lgEnduit :
                if j == eS / 2 - 1 and (i - 1) % p == 0 and i != 0 and i != n - 1:
                    T[i][j] = 1
                elif i == 0 :
                    T[i][j] = 1
                elif i == n - 1 :                               
                    T[i][j] = 1
                else :
                    [i][j] = 1


        # Pour trouver i il faut utiliser le plus grand commun diviseur entre le pas et la distance avec les alvéoles

    #endregion


    precisionResultat -= 5 * 10e-2
    print("\tPrecision : ", precisionResultat)
            
                



print("Test")

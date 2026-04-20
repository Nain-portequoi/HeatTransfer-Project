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

#region Compteur d'itération
cpt = 0
#endregion

temperatureTempon = 0

T=np.zeros((n, m))

for i in range(n):
    T[i][0] = 1
    T[i][m - 1] = 1
    print("Côté gauche et droit")


while precisionResultat >= precisionAAtteindre :
    precisionResultat = 0
    print("Itirération : ", cpt)
    cpt += 1

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
                    if i % p == 0 and j == eS / 2 :             # Position sur les sources de chaleur (à vérifier si i ≠ 1cm)
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
    precisionResultat -= 5 * 10e-2
    print("\tPrecision : ", precisionResultat)
            
                



print("Test")

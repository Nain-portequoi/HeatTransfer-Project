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
    T[i][m] = 1
    print("Côté gauche et droit")


while precisionResultat >= precisionAAtteindre :
    precisionResultat = 0
    print("Itirération : ", cpt)
    cpt += 1

    for i in range(n):
        for j in range(m):
            temperatureTempon = T[i][j]
            if i == 0 and j == 0 :                   # Coin B
                T[i][j] = 1
            if i == 0  and j < eM :                  # Plaque du haut mur extérieur : Flux nul
                T[i][j] = 1
            elif i == n :                # Plaque du bas : Flux nul
                T[i][j] = 1
            elif j < eM :
                T[i][j] = 1              # Mur extérieur
            elif 
            
                



print("Test")

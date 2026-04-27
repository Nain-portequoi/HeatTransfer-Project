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
import matplotlib.pyplot as plt

#region Pas de la matrice
pasMatriceX = 0.5
pasMatriceY = 0.5
#endregion

#region Dimension de la surface
eM = 20.0 # cm
eI = 12.0
eS_cm = 3.0
eB = 5.0
lM = 300.0
hM = 200.0
hB_cm = 10.0
k_cm = 1.5

k_x = int(k_cm / pasMatriceX)
k_y = int(k_cm / pasMatriceY)
hB = int(hB_cm / pasMatriceY)
eS_mid = int((eS_cm/2) / pasMatriceX)

lgMurExterieur_cm = eM - 0.5
lgIsolant_cm = lgMurExterieur_cm + eI - 0.5
lgEnduit_cm = lgIsolant_cm + eS_cm - 0.5
lgMurInterieur_cm = lgEnduit_cm + eB - 0.5
lgMurInterieurAvantAir_cm = lgEnduit_cm + k_cm - 0.5
lgMurInterieurApresAir_cm = lgMurInterieur_cm - k_cm - 0.5

lgMurExterieur = int (lgMurExterieur_cm / pasMatriceX)
lgIsolant = int (lgIsolant_cm / pasMatriceX)
lgEnduit = int (lgEnduit_cm / pasMatriceX)
lgMurInterieur = int (lgMurInterieur_cm / pasMatriceX)
lgMurInterieurAvantAir = int (lgMurInterieurAvantAir_cm / pasMatriceX)
lgMurInterieurApresAir = int (lgMurInterieurApresAir_cm / pasMatriceX)
#endregion

#region Dimension de la matrice
n = int(hM / pasMatriceY)
m = int((eM + eI + eS_cm + eB) / pasMatriceX)
#endregion

#region Pas des sources de chaleurs
pasSources_cm = 20
pasSources = int(pasSources_cm / pasMatriceY)
#endregion

#region Precision
precisionResultat = 1
precisionAAtteindre = 1e-2
#endregion

#region Compteurs
cptIteration = 0
cptAlveolesHaut = 0
cptAlveolesBas = 0
#endregion

temperatureTempon = 10

T=np.zeros((n, m))


while precisionResultat >= precisionAAtteindre :
    precisionResultat = 0
    print("Itirération : ", cptIteration)
    cptIteration += 1
    cptAlveolesBas = 0
    cptAlveolesHaut = 0
    #region Test si l'on calcule les températures sur la ligne
    for i in range(n) :
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
            elif i < n - 1 and j > 0 :              # |e| la plaque du haut et du bas et après la plaque de gauche
                if j < lgMurExterieur :
                    T[i][j] = 1 
                elif j == lgMurExterieur : 
                    T[i][j] = 1
                elif j < lgIsolant :
                    T[i][j] = 1
                elif j == lgIsolant :
                    T[i][j] = 1
                elif j < lgEnduit :
                    if i % pasSources == 0 and j == eS_mid :             # Position sur les sources de chaleur 
                        T[i][j] = 1
                    else :
                        T[i][j] = 1
                elif j == lgEnduit :
                    if i % hB == 0 :
                        T[i][j] = 1
                    else :
                        T[i][j] = 1
                elif j < lgMurInterieur :
                    if j < lgMurInterieurAvantAir :
                        T[i][j] = 1
                    elif j == lgMurInterieurAvantAir :
                        if i == cptAlveolesHaut + k_y :
                            T[i][j] = 1
                        elif i < cptAlveolesBas + hB - k_y:
                            T[i][j] = 1
                        else :
                            T[i][j] = 1
                    elif j < lgMurInterieurApresAir :
                        if i == cptAlveolesHaut + k_y :
                            T[i][j] = 1
                        elif i < cptAlveolesBas + hB - k_y :
                            T[i][j] = 1
                        else :
                            T[i][j] = 1
                    elif j == lgMurInterieurApresAir :
                        if i == cptAlveolesHaut + k_y :
                            cptAlveolesHaut += hB
                            T[i][j] = 1
                        elif i < cptAlveolesBas + hB - k_y :
                            T[i][j] = 1
                        else :
                            cptAlveolesBas += hB
                            T[i][j] = 1
                elif j == lgMurInterieur :
                    if i % hB == 0 :
                        T[i][j] = 1
                    else :
                        T[i][j] = 1

                    

            #endregion


            #region Plaque du bas :
            if i == n - 1:
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



            precisionResultat = max(precisionResultat, abs(T[i][j] - temperatureTempon))
    print("\tPrecision : ", precisionResultat)
            
                
    #region Test si l'on calcule les températures par bloc 
    # for i in range(n) :
    #     for j in range(m) :
    #         temperatureTempon = T[i][j]
    #         if j > 0 :
    #             if j < lgMurExterieur :
    #                 if i == 0 :
    #                     T[i][j] = 1
    #                 elif i == n - 1 :
    #                     T[i][j] = 1
    #                 else :
    #                     T[i][j] = 1
    #             elif j == lgMurExterieur :
    #                 if i == 0 :
    #                     T[i][j] = 1
    #                 elif i == n - 1 :
    #                     T[i][j] = 1
    #                 else :
    #                     T[i][j] = 1
    # for i in range(n) :
    #     for j in range(m) :
    #         temperatureTempon = T[i][j]
    #         if j < lgIsolant :
    #             if i == 0 :
    #                 T[i][j] = 1
    #             elif i == n - 1 :
    #                 T[i][j] = 1
    #             else :
    #                     T[i][j] = 1
    #         elif j == lgIsolant :
    #             if i == 0 :
    #                 T[i][j] = 1
    #             elif i == n - 1 :
    #                 T[i][j] = 1
    #             else :
    #                 [i][j] = 1
    # for i in range(n) :
    #     for j in range(m) :
    #         temperatureTempon = T[i][j]
    #         if j < lgEnduit :
    #             if j == eS / 2 - 1 and (i - 1) % p == 0 and i != 0 and i != n - 1:
    #                 T[i][j] = 1
    #             elif i == 0 :
    #                 T[i][j] = 1
    #             elif i == n - 1 :                               
    #                 T[i][j] = 1
    #             else :
    #                 [i][j] = 1


    #     # Pour trouver i il faut utiliser le plus grand commun diviseur entre le pas et la distance avec les alvéoles

    #endregion

# Calcul du flux (gradient de température)
dT_dy, dT_dx = np.gradient(T, pasMatriceY, pasMatriceX)
flux_x = -dT_dx  # flux en x (loi de Fourier : q = -k * dT/dx, sans le k ici)
flux_y = -dT_dy  # flux en y

intensite = np.sqrt(flux_x**2 + flux_y**2)

# --- Plot 1 : Dégradé de température ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

im = ax1.imshow(
    T,
    cmap='hot',
    origin='lower',
    extent=[0, eM + eI + eS_cm + eB, 0, hM],
    aspect='auto'
)
plt.colorbar(im, ax=ax1, label='Température (°C)')
ax1.set_title('Champ de température')
ax1.set_xlabel('Épaisseur (cm)')
ax1.set_ylabel('Hauteur (cm)')

# --- Plot 2 : Flux (quiver) ---
# Sous-échantillonnage pour ne pas surcharger
pas_fleche = max(1, n // 20)  # ~20 flèches en vertical max

i_idx = np.arange(0, n, pas_fleche)
j_idx = np.arange(0, m, pas_fleche)
J, I = np.meshgrid(j_idx, i_idx)  # grille des indices sous-échantillonnés

# Positions physiques
x_pos = J * pasMatriceX
y_pos = I * pasMatriceY

# Composantes du flux sous-échantillonnées
fx = flux_x[I, J]
fy = flux_y[I, J]

ax2.quiver(
    x_pos, y_pos, fx, fy,
    intensite[I, J],          # couleur selon l'intensité
    cmap='plasma',
    scale=None,               # échelle automatique
    scale_units='xy',
    angles='xy'
)
ax2.set_xlim(0, eM + eI + eS_cm + eB)
ax2.set_ylim(0, hM)
ax2.set_title('Flux thermique')
ax2.set_xlabel('Épaisseur (cm)')
ax2.set_ylabel('Hauteur (cm)')
ax2.set_aspect('equal')

plt.tight_layout()
plt.show()


print("Test")

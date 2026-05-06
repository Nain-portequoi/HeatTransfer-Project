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

pasTemponMatriceX = pasMatriceX
pasTemponMatriceY = pasMatriceY
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

j_source = lgIsolant + eS_mid
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
#endregion

#region Lambda
lbdM = 1.5
lbdI = 0.035
lbdE = 1.1
lbdB = 0.85
lbdA = 0.026
#endregion

#region Température
TempE = 10
TempI = 22
#endregion

#region Coefficent de convection et Phi
hE = 25
hI = 7
phi = 100
#endregion

temperatureTempon = 10

#region Pas variable

# Paramètres du raffinement
nb_fin  = 8    # nœuds dans la zone raffinée
nb_gros = 4    # nœuds dans la zone loin (entre deux singularités)

# ===================== AXE Y =====================
singularites_y = set()

# Bords du mur
singularites_y.add(0.0)
singularites_y.add(hM)

# Sources (tous les pasSources_cm)
for k in range(1, int(hM / pasSources_cm)):
    singularites_y.add(float(k * pasSources_cm))

# Interfaces alvéoles : bord bas et haut de chaque cavité d'air
for k in range(int(hM / hB_cm)):
    y_alv = k * hB_cm
    singularites_y.add(float(y_alv + k_cm))
    singularites_y.add(float(y_alv + hB_cm - k_cm))

singularites_y = sorted(singularites_y)

y_parts = []
for idx, y_sing in enumerate(singularites_y):
    if idx == 0:
        gauche = y_sing
    else:
        gauche = (singularites_y[idx-1] + y_sing) / 2

    if idx == len(singularites_y) - 1:
        droite = y_sing
    else:
        droite = (y_sing + singularites_y[idx+1]) / 2

    if gauche < y_sing:
        dist_g = y_sing - gauche
        y_parts.append(gauche + np.geomspace(0.001 * dist_g, dist_g, nb_fin))

    y_parts.append([y_sing])

    if y_sing < droite:
        dist_d = droite - y_sing
        y_parts.append(y_sing + dist_d - np.geomspace(0.001 * dist_d, dist_d, nb_fin)[::-1])

y = np.unique(np.concatenate(y_parts))
n = len(y)

# ===================== AXE X =====================
singularites_x = set()

singularites_x.add(0.0)
singularites_x.add(float(eM))
singularites_x.add(float(eM + eI))
singularites_x.add(float(eM + eI + eS_cm / 2))       # source n_s
singularites_x.add(float(eM + eI + eS_cm))
singularites_x.add(float(eM + eI + eS_cm + k_cm))            # bord gauche cavité
singularites_x.add(float(eM + eI + eS_cm + eB - k_cm))       # bord droit cavité
singularites_x.add(float(eM + eI + eS_cm + eB))

singularites_x = sorted(singularites_x)

x_parts = []
for idx, x_sing in enumerate(singularites_x):
    if idx == 0:
        gauche = x_sing
    else:
        gauche = (singularites_x[idx-1] + x_sing) / 2

    if idx == len(singularites_x) - 1:
        droite = x_sing
    else:
        droite = (x_sing + singularites_x[idx+1]) / 2

    if gauche < x_sing:
        dist_g = x_sing - gauche
        x_parts.append(gauche + np.geomspace(0.001 * dist_g, dist_g, nb_fin))

    x_parts.append([x_sing])

    if x_sing < droite:
        dist_d = droite - x_sing
        x_parts.append(x_sing + dist_d - np.geomspace(0.001 * dist_d, dist_d, nb_fin)[::-1])

x = np.unique(np.concatenate(x_parts))
m = len(x)

# ===================== INDICES DES SINGULARITÉS =====================
j_bord_ext   = np.searchsorted(x, 0.0)
j_mur_ext    = np.searchsorted(x, eM)
j_isolant    = np.searchsorted(x, eM + eI)
j_source     = np.searchsorted(x, eM + eI + eS_cm / 2)
j_enduit     = np.searchsorted(x, eM + eI + eS_cm)
j_air_gauche = np.searchsorted(x, eM + eI + eS_cm + k_cm)
j_air_droite = np.searchsorted(x, eM + eI + eS_cm + eB - k_cm)
j_mur_int    = np.searchsorted(x, eM + eI + eS_cm + eB)

i_bord_haut  = np.searchsorted(y, 0.0)
i_bord_bas   = np.searchsorted(y, hM)

# Sources en Y
indices_sources_y = [np.searchsorted(y, float(k * pasSources_cm)) 
                     for k in range(1, int(hM / pasSources_cm))]

# Interfaces alvéoles en Y
indices_alv_bas  = [np.searchsorted(y, float(k * hB_cm + k_cm)) 
                    for k in range(int(hM / hB_cm))]
indices_alv_haut = [np.searchsorted(y, float(k * hB_cm + hB_cm - k_cm)) 
                    for k in range(int(hM / hB_cm))]

#endregion

# Réinitialisation de la matrice avec les nouvelles dimensions
T = np.zeros((n, m))

while precisionResultat >= precisionAAtteindre :
    precisionResultat = 0
    print("Itération : ", cptIteration)
    cptIteration += 1
    
    #region Test si l'on calcule les températures sur la ligne
    for i in range(n) :
        dans_cavite = any(
        indices_alv_bas[k] <= i <= indices_alv_haut[k]
        for k in range(len(indices_alv_bas))
        )
        idx_alv = next(
        (k for k in range(len(indices_alv_bas)) if indices_alv_bas[k] <= i <= indices_alv_haut[k]), None
        )
        for j in range(m):
            #region Temperature Tempon
            temperatureTempon = T[i][j]
            #endregion

            #region Gestion des pas
            dx_avant = x[j] - x[j-1] if j > 0 else x[1] - x[0]
            dx_apres = x[j+1] - x[j] if j < m-1 else x[-1] - x[-2]
            dy_avant = y[i] - y[i-1] if i > 0 else y[1] - y[0]
            dy_apres = y[i+1] - y[i] if i < n-1 else y[-1] - y[-2]
            #endregion

            #region C
            # C Intérieur d'un matériau
            c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
            c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
            c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
            c_h = 2 / ((dy_apres + dy_avant) * dy_avant)

            # C Mur extérieur et Isolant
            cMI_g = lbdM * (dy_apres + dy_avant)/(2*dx_avant)
            cMI_d = lbdI * (dy_apres + dy_avant)/(2*dx_apres)
            cMI_b = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_avant)
            cMI_h = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_apres)

            # C Isolant et Enduit
            cIE_g = lbdI * (dy_apres + dy_avant)/(2*dx_avant)
            cIE_d = lbdE * (dy_apres + dy_avant)/(2*dx_apres)
            cIE_b = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_avant)
            cIE_h = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_apres)

            # C Enduit et Mur intérieur
            cEB_g = lbdE * (dy_apres + dy_avant)/(2*dx_avant)
            cEB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
            cEB_b = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_avant)
            cEB_h = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_apres)

            # C Mur intérieur et Air
            cBA_g = lbdB * (dy_apres + dy_avant)/(2*dx_avant)
            cBA_d = lbdA * (dy_apres + dy_avant)/(2*dx_apres)
            cBA_b = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_avant)
            cBA_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_apres)

            # C Mur intérieur et Air
            cAB_g = lbdA * (dy_apres + dy_avant)/(2*dx_avant)
            cAB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
            cAB_b = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_avant)
            cAB_h = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_apres)

            # C Sources
            c1 = lbdE * (dy_apres + dy_avant) / 2
            c2 = lbdE * (dx_apres + dx_avant) / 2
            q_sources = 200 / 9
            #endregion

            #region W
            # Face AB   A régler
            wE_ab = hE * (dy_apres + dy_avant) / (2 * dx_avant)
            wD_ab = lbdM * (dy_apres + dy_avant) / (2 * dx_apres)

            # Face CD   A régler


            # Face BC
            # wG_bc = 


            #endregion
            
            #region Plaque du haut :
            if i == 0 :
                if j == 0 :                                 # Coin B
                    T[i][j] = 1
                elif j < j_mur_ext :                   # Plaque du haut mur extérieur
                    T[i][j] = 1
                elif j == j_mur_ext :                  # Coin haut |e| mur extérieur et isolant
                    T[i][j] = 1
                elif j < j_isolant :                        # Plaque du haut isolant
                    T[i][j] = 1
                elif j == j_isolant :                       # Coin haut |e| isolant et enduit
                    T[i][j] = 1
                elif j < j_enduit :                         # Plaque du haut enduit
                    T[i][j] = 1
                elif j == j_enduit :                        # Coin haut |e| enduit et mur inétieur
                    T[i][j] = 1
                elif j < j_mur_int :                   # Plaque du haut mur intérieur
                    T[i][j] = 1
                elif j == j_mur_int :                  # Coin C
                    T[i][j] = 1
            #endregion

            #region Centre
            elif i < n - 1 :              # |e| la plaque du haut et du bas et après la plaque de gauche
                if j == 0 :
                    T[i][j] = 1

                elif j < j_mur_ext :
                    T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)

                elif j == j_mur_ext : 
                    T[i][j] = (cMI_g * T[i][j - 1] + cMI_b * T[i+1][j] + cMI_h * T[i-1][j] + cMI_d * T[i][j+1])/(cMI_d + cMI_g + cMI_b + cMI_h)

                elif j < j_isolant :
                    T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)

                elif j == j_isolant :
                    T[i][j] = (cIE_g * T[i][j - 1] + cIE_b * T[i+1][j] + cIE_h * T[i-1][j] + cIE_d * T[i][j+1])/(cIE_d + cIE_g + cIE_b + cIE_h)

                elif j < j_enduit :
                    if i in indices_sources_y and j == j_source :             # Position sur les sources de chaleur 
                        T[i][j] = (c1 * (T[i][j-1] / dx_avant + T[i][j+1] / dx_apres) + c2 * (T[i-1][j] / dy_avant + T[i+1][j] / dy_apres) + q_sources) / (c1 * (1/dx_avant + 1/dx_apres) + c2 * (1/dy_avant + 1/dy_apres))
                    else : 
                        T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)

                elif j == j_enduit :
                    T[i][j] = (cEB_g * T[i][j - 1] + cEB_b * T[i+1][j] + cEB_h * T[i-1][j] + cEB_d * T[i][j+1])/(cEB_d + cEB_g + cEB_b + cEB_h)

                elif j < j_mur_int :
                    if j < j_air_gauche :           # mur intérieur plein gauche
                        T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)

                    elif j == j_air_gauche :          # interface mur B / air A
                        if idx_alv is not None and i == indices_alv_bas[idx_alv] :
                            T[i][j] = 1   # ← coin BAS de la cavité (interface B/A + bord bas)
                        elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
                            T[i][j] = 1   # ← coin HAUT de la cavité (interface B/A + bord haut)
                        elif dans_cavite :
                            T[i][j] = (cBA_g * T[i][j-1] + cBA_b * T[i+1][j] + cBA_h * T[i-1][j] + cBA_d * T[i][j+1]) / (cBA_g + cBA_b + cBA_h + cBA_d) # ← interface B/A pure (plein milieu cavité)
                        else :
                            T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud dans lbdB hors cavité

                    elif j < j_air_droite :           # plein air
                        if idx_alv is not None and i == indices_alv_bas[idx_alv] :
                            T[i][j] = 1   # ← bord bas cavité (air + bord horizontal)
                        elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
                            T[i][j] = 1   # ← bord haut cavité (air + bord horizontal)
                        elif dans_cavite :
                            T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud intérieur lbdA pur
                        else :
                            T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud dans lbdB (entre deux cavités)

                    elif j == j_air_droite :          # interface air A / mur B
                        if idx_alv is not None and i == indices_alv_bas[idx_alv] :
                            T[i][j] = 1   # ← coin BAS (interface A/B + bord bas)
                        elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
                            T[i][j] = 1   # ← coin HAUT (interface A/B + bord haut)
                        elif dans_cavite :
                            T[i][j] = (cAB_g * T[i][j-1] + cAB_b * T[i+1][j] + cAB_h * T[i-1][j] + cAB_d * T[i][j+1]) / (cAB_g + cAB_b + cAB_h + cAB_d) # ← interface A/B pure
                        else :
                            T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud dans lbdB hors cavité

                elif j == j_mur_int :
                    T[i][j] = 1
                    
            #endregion


            #region Plaque du bas :
            elif i == n - 1:
                if j == 0 :                                 # Coin A
                    T[i][j] = 1
                elif j < j_mur_ext :                   # Plaque du bas mur extérieur
                    T[i][j] = 1
                elif j == j_mur_ext :                  # Coin bas |e| mur extérieur et isolant
                    T[i][j] = 1
                elif j < j_isolant :                        # Plaque du bas isolant
                    T[i][j] = 1
                elif j == j_isolant :                       # Coin bas |e| isolant et enduit
                    T[i][j] = 1
                elif j < j_enduit :                         # Plaque du bas enduit
                    T[i][j] = 1
                elif j == j_enduit :                        # Coin bas |e| enduit et mur inétieur
                    T[i][j] = 1
                elif j < j_mur_int :                   # Plaque du bas mur intérieur
                    T[i][j] = 1
                elif j == j_mur_int :                  # Coin D
                    T[i][j] = 1
            precisionResultat = max(precisionResultat, abs(T[i][j] - temperatureTempon))
            #endregion
    #endregion



            
    print("\tPrecision : ", precisionResultat)
            

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
    extent=[x[0], x[-1], y[0], y[-1]],
    aspect='auto'
)
plt.colorbar(im, ax=ax1, label='Température (°C)')
ax1.set_title('Champ de température')
ax1.set_xlabel('Épaisseur (cm)')
ax1.set_ylabel('Hauteur (cm)')

# --- Plot 2 : Flux (quiver) ---
# Sous-échantillonnage pour ne pas surcharger
pas_fleche = max(1, n // 20)  # ~20 flèches en vertical max

pas_fleche_i = max(1, n // 20)   # ~20 flèches en Y
pas_fleche_j = max(1, m // 20)   # ~20 flèches en X

for I in range(0, n-1, pas_fleche_i):
    for J in range(0, m-1, pas_fleche_j):
        x_pos = x[J]
        y_pos = y[I]

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

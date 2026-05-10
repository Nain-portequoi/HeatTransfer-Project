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
TEST_PAS_VARIABLE = False
if TEST_PAS_VARIABLE :
    #region Pas variable
    # Paramètres du raffinement
    nb_fin  = 6    # nœuds dans la zone raffinée
    nb_gros = 15    # nœuds dans la zone loin (entre deux singularités)

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
        y_parts.append([y_sing])
        
        if idx < len(singularites_y) - 1:
            y_next = singularites_y[idx + 1]
            dist = y_next - y_sing
            delta_y = min(0.05, dist / 4)
            
            y_parts.append(np.linspace(y_sing + delta_y, y_next - delta_y, nb_gros))

    y = np.unique(np.concatenate(y_parts))
    n = len(y)

    # Vérification
    for s in singularites_y:
        idx = np.searchsorted(y, s)
        if abs(y[idx] - s) > 1e-10:
            print(f"⚠️ Singularité y={s:.6f} absente ! Plus proche : y[{idx}]={y[idx]:.6f}")

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

# ===================== AXE X =====================
    singularites_x = sorted(singularites_x)

    x_parts = []
    for idx, x_sing in enumerate(singularites_x):
        x_parts.append([x_sing])
        
        if idx < len(singularites_x) - 1:
            x_next = singularites_x[idx + 1]
            dist = x_next - x_sing
            delta_x = min(0.05, dist / 4)  # ← jamais plus grand que dist/4
            
            x_parts.append(np.linspace(x_sing + delta_x, x_next - delta_x, nb_gros))

    x = np.unique(np.concatenate(x_parts))
    m = len(x)


    for s in singularites_x:
        idx = np.searchsorted(x, s)
        if abs(x[idx] - s) > 1e-10:
            print(f"⚠️ Singularité x={s:.6f} absente ! Plus proche : x[{idx}]={x[idx]:.6f}")

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

    #print(f"j_mur_int = {j_mur_int}, x[j_mur_int] = {x[j_mur_int]:.6f}, x[-1] = {x[-1]:.6f}")
    #print(f"j_mur_int == m-1 ? {j_mur_int == m - 1}")
    #print(f"n={n}, m={m}")
    #endregion
else :
    #region Test pas uniforme
    n_test = 50
    m_test = 50

    y = np.linspace(0, hM, n_test)
    x = np.linspace(0, eM + eI + eS_cm + eB, m_test)
    n = len(y)
    m = len(x)

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

    indices_sources_y = [np.searchsorted(y, float(k * pasSources_cm))
                        for k in range(1, int(hM / pasSources_cm))]
    indices_alv_bas  = [np.searchsorted(y, float(k * hB_cm + k_cm))
                        for k in range(int(hM / hB_cm))]
    indices_alv_haut = [np.searchsorted(y, float(k * hB_cm + hB_cm - k_cm))
                        for k in range(int(hM / hB_cm))]

    #endregion

# ===== PRINTS DE DEBUG =====
print(f"j_bord_ext = {j_bord_ext}, x[j_bord_ext] = {x[j_bord_ext]:.6f}, x[0] = {x[0]:.6f}")
print(f"j_bord_ext == 0 ? {j_bord_ext == 0}")

print(f"j_mur_ext={j_mur_ext} → x={x[j_mur_ext]:.4f} | avant: {x[j_mur_ext-1]:.4f} | après: {x[j_mur_ext+1]:.4f}")
print(f"j_isolant={j_isolant}  → x={x[j_isolant]:.4f}  | avant: {x[j_isolant-1]:.4f} | après: {x[j_isolant+1]:.4f}")
print(f"j_enduit={j_enduit}   → x={x[j_enduit]:.4f}   | avant: {x[j_enduit-1]:.4f} | après: {x[j_enduit+1]:.4f}")

print("5 premiers x :", x[:5])
print("5 derniers x :", x[-5:])
print("dx min =", np.min(np.diff(x)), "cm")
print("dx max =", np.max(np.diff(x)), "cm")
print("dy min =", np.min(np.diff(y)), "cm")
print("dy max =", np.max(np.diff(y)), "cm")

print(f"TempI = {TempI}")
print(f"TempE = {TempE}")
print(f"hI = {hI}")
print(f"hE = {hE}")


# ===========================

# Initialisation de la matrice 
T = np.linspace(TempE, TempI, m)[np.newaxis, :] * np.ones((n, 1))

print(f"T.shape = {T.shape}")  # doit être (n, m) = (nb lignes Y, nb colonnes X)
print(f"n={n}, m={m}")

print(f"j_source      = {j_source}  → x = {x[j_source]:.4f} cm")
print(f"j_enduit      = {j_enduit}  → x = {x[j_enduit]:.4f} cm")
print(f"j_air_gauche  = {j_air_gauche}  → x = {x[j_air_gauche]:.4f} cm")
print(f"eM+eI+eS/2    = {eM + eI + eS_cm/2:.4f} cm  ← position attendue source")

# ===== CHOIX DU SOLVEUR =====
USE_THOMAS = False  # False = Gauss-Seidel, True = Thomas (ADI)
if USE_THOMAS :
    a_vec = np.zeros(m)
    b_vec = np.zeros(m)
    c_vec = np.zeros(m)
    y_vec = np.zeros(m)
    def thomas(a, b, c, y):
        n = len(b)
        gamma = np.zeros(n)
        beta  = np.zeros(n)

        # Initialisation sur le PREMIER nœud (i=0)
        gamma[0] = -c[0] / b[0]
        beta[0]  = y[0] / b[0]

        # Descente à partir de i=1
        for i in range(1, n):
            denom    = b[i] + a[i] * gamma[i-1]
            gamma[i] = -c[i] / denom
            beta[i]  = (y[i] - a[i] * beta[i-1]) / denom

        # Substitution arrière
        x = np.zeros(n)
        x[-1] = beta[-1]
        for i in range(n-2, -1, -1):
            x[i] = gamma[i] * x[i+1] + beta[i]

        return x

while precisionResultat >= precisionAAtteindre :
    precisionResultat = 0
    print("Itération : ", cptIteration)
    cptIteration += 1
    T_avant = T.copy()       
    if not USE_THOMAS :
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
                cMI_b = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_apres)
                cMI_h = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_avant)

                # C Isolant et Enduit
                cIE_g = lbdI * (dy_apres + dy_avant)/(2*dx_avant)
                cIE_d = lbdE * (dy_apres + dy_avant)/(2*dx_apres)
                cIE_b = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_apres)
                cIE_h = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_avant)

                # C Enduit et Mur intérieur
                cEB_g = lbdE * (dy_apres + dy_avant)/(2*dx_avant)
                cEB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
                cEB_b = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_apres)
                cEB_h = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_avant)

                # C Mur intérieur et Air selon X
                cBA_g = lbdB * (dy_apres + dy_avant)/(2*dx_avant)
                cBA_d = lbdA * (dy_apres + dy_avant)/(2*dx_apres)
                cBA_b = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_apres)
                cBA_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_avant)

                # C Mur intérieur et Air
                cAB_g = lbdA * (dy_apres + dy_avant)/(2*dx_avant)
                cAB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
                cAB_b = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_apres)
                cAB_h = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_avant)

                # C Sources
                c1 = lbdE * (dy_apres + dy_avant) / 2
                c2 = lbdE * (dx_apres + dx_avant) / 2
                q_sources = 100 * 3 / 9
                #endregion

                #region W
                # Face AB   
                wE_ab = hE * (dy_apres + dy_avant) / 2
                wD_ab = lbdM * (dy_apres + dy_avant) / (2 * dx_apres)
                wH_ab = lbdM * dx_apres / (2*dy_avant)
                wB_ab = lbdM * dx_apres / (2*dy_apres)

                # Face CD   
                wI_cd = hI * (dy_apres + dy_avant) / 2
                wG_cd = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
                wH_cd = lbdB * dx_avant / (2*dy_avant)
                wB_cd = lbdB * dx_avant / (2*dy_apres)


                #endregion
                
                #region Plaque du haut :
                if i == 0 :
                    # Face BC
                    wG_bc = dy_apres / (2*dx_avant)
                    wD_bc = dy_apres / (2*dx_apres)
                    if j == 0 :                                 # Coin B
                        wE_B = hE * dy_apres / 2
                        wD_B = lbdM * dy_apres / (2*dx_apres)
                        wB_B = lbdM * dx_apres / (2*dy_apres)
                        T[i][j] = (wE_B * TempE + wD_B * T[i][j+1] + wB_B * T[i+1][j]) / (wE_B + wD_B + wB_B)
                    elif j < j_mur_ext :                        # Plaque du haut mur extérieur
                        wG_bc = wG_bc * lbdM
                        wD_bc = wD_bc * lbdM
                        wB_bc = lbdM * (dx_apres + dx_avant) / (2*dy_apres)
                        T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
                    elif j == j_mur_ext :                       # Coin haut |e| mur extérieur et isolant
                        wG_bc = wG_bc * lbdM
                        wD_bc = wD_bc * lbdI
                        wB_bc = (dx_apres * lbdI + dx_avant * lbdM) / (2*dy_apres)
                        T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
                    elif j < j_isolant :                        # Plaque du haut isolant
                        wG_bc = wG_bc * lbdI
                        wD_bc = wD_bc * lbdI
                        wB_bc = lbdI * (dx_apres + dx_avant) / (2*dy_apres)
                        T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
                    elif j == j_isolant :                       # Coin haut |e| isolant et enduit
                        wG_bc = wG_bc * lbdI
                        wD_bc = wD_bc * lbdE
                        wB_bc = (dx_apres * lbdE + dx_avant * lbdI) / (2*dy_apres)
                        T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
                    elif j < j_enduit :                         # Plaque du haut enduit
                        wG_bc = wG_bc * lbdE
                        wD_bc = wD_bc * lbdE
                        wB_bc = lbdE * (dx_apres + dx_avant) / (2*dy_apres)
                        T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
                    elif j == j_enduit :                        # Coin haut |e| enduit et mur inétieur
                        wG_bc = wG_bc * lbdE
                        wD_bc = wD_bc * lbdB
                        wB_bc = (dx_apres * lbdB + dx_avant * lbdE) / (2*dy_apres)
                        T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
                    elif j < j_mur_int :                        # Plaque du haut mur intérieur
                        wG_bc = wG_bc * lbdB
                        wD_bc = wD_bc * lbdB
                        wB_bc = lbdB * (dx_apres + dx_avant) / (2*dy_apres)
                        T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
                    elif j == j_mur_int :                       # Coin C
                        wC_C = hI * dy_apres / 2
                        wG_C = lbdB * dy_apres / (2*dx_avant)
                        wB_C = lbdB * dx_avant / (2*dy_apres)
                        T[i][j] = (wC_C * TempI + wG_C * T[i][j-1] + wB_C * T[i+1][j]) / (wC_C + wG_C + wB_C)
                #endregion

                #region Centre
                elif i < n - 1 :              # |e| la plaque du haut et du bas et après la plaque de gauche
                    if j == 0 :
                        T[i][j] = (wE_ab * TempE + wD_ab * T[i][j+1] + wH_ab * T[i-1][j] + wB_ab * T[i+1][j]) / (wE_ab + wD_ab + wB_ab + wH_ab)

                    elif j < j_mur_ext :
                        
                        T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)
                        #print("Emplacement : point mur ext : ", {T[i][j]})

                    elif j == j_mur_ext : 
                        T[i][j] = (cMI_g * T[i][j - 1] + cMI_b * T[i+1][j] + cMI_h * T[i-1][j] + cMI_d * T[i][j+1])/(cMI_d + cMI_g + cMI_b + cMI_h)
                        #print(f"Emplacement (enter mur extérieur et isolant): i = {i}, j = {j} et température = {T[i][j]}")

                    elif j < j_isolant :
                        T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)
                        #print("Emplacement : point isolant : ", {T[i][j]})

                    elif j == j_isolant :
                        T[i][j] = (cIE_g * T[i][j - 1] + cIE_b * T[i+1][j] + cIE_h * T[i-1][j] + cIE_d * T[i][j+1])/(cIE_d + cIE_g + cIE_b + cIE_h)

                    elif j < j_enduit :
                        if i in indices_sources_y and j == j_source :             # Position sur les sources de chaleur 
                            T[i][j] = (c1 * (T[i-1][j] / dx_avant + T[i+1][j] / dx_apres) + c2 * (T[1][j-1] / dy_avant + T[1][j+1] / dy_apres) + q_sources / ((dx_apres+dx_avant)/2 * (dy_apres+dy_avant)/2 * 3)) / (c1 * (1/dx_avant + 1/dx_apres) + c2 * (1/dy_avant + 1/dy_apres)) 
                            #print(f"Emplacement : point enduit : {T[i][j]} et emplacement i={i}, j = {j}")
                        else : 
                            #print(f"else générique : i={i}, j={j}")
                            T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)

                    elif j == j_enduit :
                        T[i][j] = (cEB_g * T[i][j - 1] + cEB_b * T[i+1][j] + cEB_h * T[i-1][j] + cEB_d * T[i][j+1])/(cEB_d + cEB_g + cEB_b + cEB_h)

                    elif j < j_mur_int :
                        if j < j_air_gauche :           # mur intérieur plein gauche
                            T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)

                        elif j == j_air_gauche :          # interface mur B / air A
                            if idx_alv is not None and i == indices_alv_bas[idx_alv] :
                                cAlveole_g = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
                                cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
                                cAlveole_d = (lbdB * dy_avant + lbdA * dy_apres) / (2 * dx_apres)
                                cAlveole_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_avant)
                                T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← coin BAS de la cavité (interface B/A + bord bas)
                            elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
                                cAlveole_g = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
                                cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_avant)
                                cAlveole_d = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
                                cAlveole_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_apres)
                                T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← coin HAUT de la cavité (interface B/A + bord haut)
                            elif dans_cavite :
                                T[i][j] = (cBA_g * T[i][j-1] + cBA_b * T[i+1][j] + cBA_h * T[i-1][j] + cBA_d * T[i][j+1]) / (cBA_g + cBA_b + cBA_h + cBA_d) # ← interface B/A pure (plein milieu cavité)
                            else :
                                T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud dans lbdB hors cavité

                        elif j < j_air_droite :           # plein air
                            if idx_alv is not None and i == indices_alv_bas[idx_alv] :
                                cAlveole_g = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
                                cAlveole_b = lbdB * (dx_apres * dx_avant) / (2 * dy_apres)
                                cAlveole_d = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
                                cAlveole_h = lbdA * (dx_avant * dx_apres) / (2*dy_avant)
                                T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← bord bas cavité (air + bord horizontal)
                            elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
                                cAlveole_g = (lbdA * dy_apres + lbdB * dy_avant) / (2 * dx_apres)
                                cAlveole_b = lbdA * (dx_apres * dx_avant) / (2 * dy_apres)
                                cAlveole_d = (lbdA * dy_apres + lbdB * dy_avant) / (2 * dx_apres)
                                cAlveole_h = lbdB * (dx_avant * dx_apres) / (2*dy_avant)
                                T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← bord haut cavité (air + bord horizontal)
                            elif dans_cavite :
                                T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud intérieur lbdA pur
                            else :
                                T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud dans lbdB (entre deux cavités)

                        elif j == j_air_droite :          # interface air A / mur B
                            if idx_alv is not None and i == indices_alv_bas[idx_alv] :
                                #print("Emplacement : coin alvéole inf droit")
                                cAlveole_d = lbdB * (dy_apres + dy_avant) / (2 * dx_apres)
                                cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
                                cAlveole_g = (lbdB * dy_avant + lbdA * dy_apres) / (2 * dx_avant)
                                cAlveole_h = (lbdB * dx_apres + lbdA * dx_avant) / (2 * dy_avant)
                                T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← coin BAS (interface A/B + bord bas)
                            elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
                                #print("Emplacement : coin alvéole sup droit")
                                cAlveole_d = lbdB * (dy_apres + dy_avant) / (2 * dx_apres)
                                cAlveole_h = lbdB * (dx_apres + dx_avant) / (2 * dy_avant)
                                cAlveole_g = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_avant)
                                cAlveole_b = (lbdB * dx_apres + lbdA * dx_avant) / (2 * dy_apres)
                                T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← coin HAUT (interface A/B + bord haut)
                            elif dans_cavite :
                                T[i][j] = (cAB_g * T[i][j-1] + cAB_b * T[i+1][j] + cAB_h * T[i-1][j] + cAB_d * T[i][j+1]) / (cAB_g + cAB_b + cAB_h + cAB_d) # ← interface A/B pure
                            else :
                                #print(f"else générique : i={i}, j={j}")
                                T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud dans lbdB hors cavité
                        else :
                            T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)

                    elif j == j_mur_int :
                        T[i][j] = (wI_cd * TempI + wG_cd * T[i][j-1] + wH_cd * T[i-1][j] + wB_cd * T[i+1][j]) / (wB_cd + wI_cd + wH_cd + wG_cd)
                        
                #endregion


                #region Plaque du bas :
                elif i == n - 1:
                    # Face AD
                    wG_ad = dy_avant / (2*dx_avant)
                    wD_ad = dy_avant / (2*dx_apres)
                    if j == 0 :                                 # Coin A
                        wE_A = hE * dy_avant / 2
                        wD_A = lbdM * dy_avant / (2*dx_apres)
                        wH_A = lbdM * dx_apres / (2*dy_avant)
                        T[i][j] = (wE_A * TempE + wD_A * T[i][j+1] + wH_A * T[i-1][j]) / (wE_A + wD_A + wH_A)
                    elif j < j_mur_ext :                        # Plaque du bas mur extérieur
                        wG_ad = wG_ad * lbdM
                        wD_ad = wD_ad * lbdM
                        wH_ad = lbdM * (dx_apres + dx_avant) / (2*dy_avant)
                        T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
                    elif j == j_mur_ext :                       # Coin bas |e| mur extérieur et isolant
                        wG_ad = wG_ad * lbdM
                        wD_ad = wD_ad * lbdI
                        wH_ad = (dx_apres * lbdI + dx_avant * lbdM) / (2*dy_avant)
                        T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
                    elif j < j_isolant :                        # Plaque du bas isolant
                        wG_ad = wG_ad * lbdI
                        wD_ad = wD_ad * lbdI
                        wH_ad = lbdI * (dx_apres + dx_avant) / (2*dy_avant)
                        T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
                    elif j == j_isolant :                       # Coin bas |e| isolant et enduit
                        wG_ad = wG_ad * lbdI
                        wD_ad = wD_ad * lbdE
                        wH_ad = (dx_apres * lbdE + dx_avant * lbdI) / (2*dy_avant)
                        T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
                    elif j < j_enduit :                         # Plaque du bas enduit
                        wG_ad = wG_ad * lbdE
                        wD_ad = wD_ad * lbdE
                        wH_ad = lbdE * (dx_apres + dx_avant) / (2*dy_avant)
                        T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
                    elif j == j_enduit :                        # Coin bas |e| enduit et mur inétieur
                        wG_ad = wG_ad * lbdE
                        wD_ad = wD_ad * lbdB
                        wH_ad = (dx_apres * lbdB + dx_avant * lbdE) / (2*dy_avant)
                        T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
                    elif j < j_mur_int :                        # Plaque du bas mur intérieur
                        wG_ad = wG_ad * lbdB
                        wD_ad = wD_ad * lbdB
                        wH_ad = lbdB * (dx_apres + dx_avant) / (2*dy_avant)
                        T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
                    elif j == j_mur_int :                       # Coin D
                        wC_D = hI * dy_avant / 2
                        wG_D = lbdB * dy_avant / (2*dx_avant)
                        wH_D = lbdB * dx_avant / (2*dy_avant)
                        T[i][j] = (wC_D * TempI + wG_D * T[i][j-1] + wH_D * T[i-1][j]) / (wC_D + wG_D + wH_D)
                precisionResultat = max(precisionResultat, abs(T[i][j] - temperatureTempon))
                #noeuds_modifies = np.sum(T != T_avant)
                #print(f"Itération {cptIteration} — nœuds modifiés : {noeuds_modifies} / {n*m}")
                #endregion
        #endregion

    else :
        T_ancien = T.copy()
        #region Test si l'on calcule les températures sur la ligne
        for i in range(n) :
            a_vec = np.zeros(m)
            b_vec = np.zeros(m)
            c_vec = np.zeros(m)
            y_vec = np.zeros(m)
            dans_cavite = any(
            indices_alv_bas[k] <= i <= indices_alv_haut[k]
            for k in range(len(indices_alv_bas))
            )
            idx_alv = next(
            (k for k in range(len(indices_alv_bas)) if indices_alv_bas[k] <= i <= indices_alv_haut[k]), None
            )
            for j in range(m):

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
                cMI_b = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_apres)
                cMI_h = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_avant)

                # C Isolant et Enduit
                cIE_g = lbdI * (dy_apres + dy_avant)/(2*dx_avant)
                cIE_d = lbdE * (dy_apres + dy_avant)/(2*dx_apres)
                cIE_b = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_apres)
                cIE_h = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_avant)

                # C Enduit et Mur intérieur
                cEB_g = lbdE * (dy_apres + dy_avant)/(2*dx_avant)
                cEB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
                cEB_b = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_apres)
                cEB_h = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_avant)

                # C Mur intérieur et Air selon X
                cBA_g = lbdB * (dy_apres + dy_avant)/(2*dx_avant)
                cBA_d = lbdA * (dy_apres + dy_avant)/(2*dx_apres)
                cBA_b = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_apres)
                cBA_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_avant)

                # C Mur intérieur et Air
                cAB_g = lbdA * (dy_apres + dy_avant)/(2*dx_avant)
                cAB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
                cAB_b = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_apres)
                cAB_h = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_avant)

                # C Sources
                c1 = lbdE * (dy_apres + dy_avant) / 2
                c2 = lbdE * (dx_apres + dx_avant) / 2
                q_sources = 200 / 9
                #endregion

                #region W
                # Face AB   
                wE_ab = hE * (dy_apres + dy_avant) / 2
                wD_ab = lbdM * (dy_apres + dy_avant) / (2 * dx_apres)
                wH_ab = lbdM * dx_apres / (2*dy_avant)
                wB_ab = lbdM * dx_apres / (2*dy_apres)

                # Face CD   
                wI_cd = hI * (dy_apres + dy_avant) / 2
                wG_cd = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
                wH_cd = lbdB * dx_avant / (2*dy_avant)
                wB_cd = lbdB * dx_avant / (2*dy_apres)


                #endregion
                
                #region Plaque du haut :
                if i == 0 :
                    # Face BC
                    wG_bc = dy_apres / (2*dx_avant)
                    wD_bc = dy_apres / (2*dx_apres)
                    if j == 0 :                                 # Coin B
                        wE_B = hE * dy_apres / 2
                        wD_B = lbdM * dy_apres / (2*dx_apres)
                        wB_B = lbdM * dx_apres / (2*dy_apres)
                        a_vec[j] = 0 ; c_vec[j] = wD_B ; b_vec[j] = -(wE_B+wD_B+wB_B) ; y_vec[j] = -(wE_B*TempE + wB_B*T[i+1][j])
                    elif j < j_mur_ext :                        # Plaque du haut mur extérieur
                        wG_bc = wG_bc * lbdM
                        wD_bc = wD_bc * lbdM
                        wB_bc = lbdM * (dx_apres + dx_avant) / (2*dy_apres)
                        a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
                    elif j == j_mur_ext :                       # Coin haut |e| mur extérieur et isolant
                        wG_bc = wG_bc * lbdM
                        wD_bc = wD_bc * lbdI
                        wB_bc = (dx_apres * lbdI + dx_avant * lbdM) / (2*dy_apres)
                        a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
                    elif j < j_isolant :                        # Plaque du haut isolant
                        wG_bc = wG_bc * lbdI
                        wD_bc = wD_bc * lbdI
                        wB_bc = lbdI * (dx_apres + dx_avant) / (2*dy_apres)
                        a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
                    elif j == j_isolant :                       # Coin haut |e| isolant et enduit
                        wG_bc = wG_bc * lbdI
                        wD_bc = wD_bc * lbdE
                        wB_bc = (dx_apres * lbdE + dx_avant * lbdI) / (2*dy_apres)
                        a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
                    elif j < j_enduit :                         # Plaque du haut enduit
                        wG_bc = wG_bc * lbdE
                        wD_bc = wD_bc * lbdE
                        wB_bc = lbdE * (dx_apres + dx_avant) / (2*dy_apres)
                        a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
                    elif j == j_enduit :                        # Coin haut |e| enduit et mur inétieur
                        wG_bc = wG_bc * lbdE
                        wD_bc = wD_bc * lbdB
                        wB_bc = (dx_apres * lbdB + dx_avant * lbdE) / (2*dy_apres)
                        a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
                    elif j < j_mur_int :                        # Plaque du haut mur intérieur
                        wG_bc = wG_bc * lbdB
                        wD_bc = wD_bc * lbdB
                        wB_bc = lbdB * (dx_apres + dx_avant) / (2*dy_apres)
                        a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
                    elif j == j_mur_int :                       # Coin C
                        wC_C = hI * dy_apres / 2
                        wG_C = lbdB * dy_apres / (2*dx_avant)
                        wB_C = lbdB * dx_avant / (2*dy_apres)
                        a_vec[j] =  wG_bc; c_vec[j] = 0 ; b_vec[j] = -(wC_C+wG_C+wB_C) ; y_vec[j] = -(wC_C * TempI + wB_C*T[i+1][j])
                #endregion

                #region Centre
                elif i < n - 1 :              # |e| la plaque du haut et du bas et après la plaque de gauche
                    if j == 0 :
                        a_vec[j] = 0
                        c_vec[j] = wD_ab
                        b_vec[j] = -(wD_ab + wE_ab + wH_ab + wB_ab)
                        y_vec[j] = -(wH_ab * T[i-1][j] + wB_ab * T[i+1][j] + wE_ab * TempE)

                    elif j < j_mur_ext :
                        a_vec[j] = c_g
                        c_vec[j] = c_d
                        b_vec[j] = -(c_g + c_d + c_h + c_b)
                        y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])
                        #print("Emplacement : point mur ext : ", {T[i][j]})

                    elif j == j_mur_ext : 
                        a_vec[j] = cMI_g
                        c_vec[j] = cMI_d
                        b_vec[j] = -(cMI_g + cMI_d + cMI_h + cMI_b)
                        y_vec[j] = -(cMI_h * T[i-1][j] + cMI_b * T[i+1][j])
                        #print(f"Emplacement (enter mur extérieur et isolant): i = {i}, j = {j} et température = {T[i][j]}")

                    elif j < j_isolant :
                        a_vec[j] = c_g
                        c_vec[j] = c_d
                        b_vec[j] = -(c_g + c_d + c_h + c_b)
                        y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])
                        #print("Emplacement : point isolant : ", {T[i][j]})

                    elif j == j_isolant :
                        a_vec[j] = cIE_g
                        c_vec[j] = cIE_d
                        b_vec[j] = -(cIE_g + cIE_d + cIE_h + cIE_b)
                        y_vec[j] = -(cIE_h * T[i-1][j] + cIE_b * T[i+1][j])

                    elif j < j_enduit :
                        if i in indices_sources_y and j == j_source :             # Position sur les sources de chaleur 
                            cS_g = c2 / dy_avant
                            cS_d = c2 / dy_apres
                            cS_h = c1 / dx_avant
                            cS_b = c1 / dx_apres

                            a_vec[j] = cS_g
                            c_vec[j] = cS_d
                            b_vec[j] = -(cS_g + cS_d + cS_h + cS_b)
                            y_vec[j] = -(cS_h * T[i-1][j] + cS_b * T[i+1][j] + q_sources)
                            #print(f"Emplacement : point enduit : {T[i][j]} et emplacement i={i}, j = {j}")
                        else : 
                            #print(f"else générique : i={i}, j={j}")
                            a_vec[j] = c_g
                            c_vec[j] = c_d
                            b_vec[j] = -(c_g + c_d + c_h + c_b)
                            y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])

                    elif j == j_enduit :
                        a_vec[j] = cEB_g
                        c_vec[j] = cEB_d
                        b_vec[j] = -(cEB_g + cEB_d + cEB_h + cEB_b)
                        y_vec[j] = -(cEB_h * T[i-1][j] + cEB_b * T[i+1][j])

                    elif j < j_mur_int :
                        if j < j_air_gauche :           # mur intérieur plein gauche
                            a_vec[j] = c_g
                            c_vec[j] = c_d
                            b_vec[j] = -(c_g + c_d + c_h + c_b)
                            y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])

                        elif j == j_air_gauche :          # interface mur B / air A
                            if idx_alv is not None and i == indices_alv_bas[idx_alv] : 
                                cAlveole_g = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
                                cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
                                cAlveole_d = (lbdB * dy_avant + lbdA * dy_apres) / (2 * dx_apres)
                                cAlveole_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_avant)
                                a_vec[j] = cAlveole_g
                                c_vec[j] = cAlveole_d
                                b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
                                y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← coin BAS de la cavité (interface B/A + bord bas)
                            elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
                                cAlveole_g = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
                                cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_avant)
                                cAlveole_d = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
                                cAlveole_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_apres)
                                a_vec[j] = cAlveole_g
                                c_vec[j] = cAlveole_d
                                b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
                                y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← coin HAUT de la cavité (interface B/A + bord haut)
                            elif dans_cavite :
                                a_vec[j] = cBA_g 
                                c_vec[j] = cBA_d
                                b_vec[j] = -(cBA_g + cBA_d + cBA_h + cBA_b)
                                y_vec[j] = -(cBA_h * T[i-1][j] + cBA_b * T[i+1][j]) # ← interface B/A pure (plein milieu cavité)
                            else :
                                a_vec[j] = c_g
                                c_vec[j] = c_d
                                b_vec[j] = -(c_g + c_d + c_h + c_b)
                                y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])   # ← nœud dans lbdB hors cavité

                        elif j < j_air_droite :           # plein air
                            if idx_alv is not None and i == indices_alv_bas[idx_alv] :
                                cAlveole_g = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
                                cAlveole_b = lbdB * (dx_apres * dx_avant) / (2 * dy_apres)
                                cAlveole_d = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
                                cAlveole_h = lbdA * (dx_avant * dx_apres) / (2*dy_avant)
                                a_vec[j] = cAlveole_g
                                c_vec[j] = cAlveole_d
                                b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
                                y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← bord bas cavité (air + bord horizontal)
                            elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
                                cAlveole_g = (lbdA * dy_apres + lbdB * dy_avant) / (2 * dx_apres)
                                cAlveole_b = lbdA * (dx_apres * dx_avant) / (2 * dy_apres)
                                cAlveole_d = (lbdA * dy_apres + lbdB * dy_avant) / (2 * dx_apres)
                                cAlveole_h = lbdB * (dx_avant * dx_apres) / (2*dy_avant)
                                a_vec[j] = cAlveole_g
                                c_vec[j] = cAlveole_d
                                b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
                                y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← bord haut cavité (air + bord horizontal)
                            elif dans_cavite :
                                a_vec[j] = c_g * lbdA
                                c_vec[j] = c_d * lbdA
                                b_vec[j] = -(c_g + c_d + c_h + c_b) * lbdA
                                y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j]) * lbdA   # ← nœud intérieur lbdA pur
                            else :
                                a_vec[j] = c_g
                                c_vec[j] = c_d
                                b_vec[j] = -(c_g + c_d + c_h + c_b)
                                y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])   # ← nœud dans lbdB (entre deux cavités)

                        elif j == j_air_droite :          # interface air A / mur B
                            if idx_alv is not None and i == indices_alv_bas[idx_alv] :
                                #print("Emplacement : coin alvéole inf droit")
                                cAlveole_d = lbdB * (dy_apres + dy_avant) / (2 * dx_apres)
                                cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
                                cAlveole_g = (lbdB * dy_avant + lbdA * dy_apres) / (2 * dx_avant)
                                cAlveole_h = (lbdB * dx_apres + lbdA * dx_avant) / (2 * dy_avant)
                                a_vec[j] = cAlveole_g
                                c_vec[j] = cAlveole_d
                                b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
                                y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← coin BAS (interface A/B + bord bas)
                            elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
                                #print("Emplacement : coin alvéole sup droit")
                                cAlveole_d = lbdB * (dy_apres + dy_avant) / (2 * dx_apres)
                                cAlveole_h = lbdB * (dx_apres + dx_avant) / (2 * dy_avant)
                                cAlveole_g = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_avant)
                                cAlveole_b = (lbdB * dx_apres + lbdA * dx_avant) / (2 * dy_apres)
                                a_vec[j] = cAlveole_g
                                c_vec[j] = cAlveole_d
                                b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
                                y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← coin HAUT (interface A/B + bord haut)
                            elif dans_cavite :
                                a_vec[j] = cAB_g
                                c_vec[j] = cAB_d
                                b_vec[j] = -(cAB_g + cAB_d + cAB_h + cAB_b)
                                y_vec[j] = -(cAB_h * T[i-1][j] + cAB_b * T[i+1][j]) # ← interface A/B pure
                            else :
                                #print(f"else générique : i={i}, j={j}")
                                a_vec[j] = c_g
                                c_vec[j] = c_d
                                b_vec[j] = -(c_g + c_d + c_h + c_b)
                                y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])   # ← nœud dans lbdB hors cavité
                        else :
                            a_vec[j] = c_g
                            c_vec[j] = c_d
                            b_vec[j] = -(c_g + c_d + c_h + c_b)
                            y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])

                    elif j == j_mur_int :
                        a_vec[j] = wG_cd
                        c_vec[j] = 0                    # pas de voisin droit
                        b_vec[j] = -(wG_cd + wI_cd + wH_cd + wB_cd)
                        y_vec[j] = -(wH_cd * T[i-1][j] + wB_cd * T[i+1][j] + wI_cd * TempI)
                        
                #endregion

                #region Plaque du bas :
                elif i == n - 1:
                    # Face AD
                    wG_ad = dy_avant / (2*dx_avant)
                    wD_ad = dy_avant / (2*dx_apres)
                    if j == 0 :                                 # Coin A
                        wE_A = hE * dy_avant / 2
                        wD_A = lbdM * dy_avant / (2*dx_apres)
                        wH_A = lbdM * dx_apres / (2*dy_avant)
                        a_vec[j] =  0; c_vec[j] = wD_A ; b_vec[j] = -(wD_A+wE_A+wH_A) ; y_vec[j] = -(wH_A * T[i-1][j] + wE_A * TempE)
                    elif j < j_mur_ext :                        # Plaque du bas mur extérieur
                        wG_ad = wG_ad * lbdM
                        wD_ad = wD_ad * lbdM
                        wH_ad = lbdM * (dx_apres + dx_avant) / (2*dy_avant)
                        a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
                    elif j == j_mur_ext :                       # Coin bas |e| mur extérieur et isolant
                        wG_ad = wG_ad * lbdM
                        wD_ad = wD_ad * lbdI
                        wH_ad = (dx_apres * lbdI + dx_avant * lbdM) / (2*dy_avant)
                        a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
                    elif j < j_isolant :                        # Plaque du bas isolant
                        wG_ad = wG_ad * lbdI
                        wD_ad = wD_ad * lbdI
                        wH_ad = lbdI * (dx_apres + dx_avant) / (2*dy_avant)
                        a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
                    elif j == j_isolant :                       # Coin bas |e| isolant et enduit
                        wG_ad = wG_ad * lbdI
                        wD_ad = wD_ad * lbdE
                        wH_ad = (dx_apres * lbdE + dx_avant * lbdI) / (2*dy_avant)
                        a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
                    elif j < j_enduit :                         # Plaque du bas enduit
                        wG_ad = wG_ad * lbdE
                        wD_ad = wD_ad * lbdE
                        wH_ad = lbdE * (dx_apres + dx_avant) / (2*dy_avant)
                        a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
                    elif j == j_enduit :                        # Coin bas |e| enduit et mur inétieur
                        wG_ad = wG_ad * lbdE
                        wD_ad = wD_ad * lbdB
                        wH_ad = (dx_apres * lbdB + dx_avant * lbdE) / (2*dy_avant)
                        a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
                    elif j < j_mur_int :                        # Plaque du bas mur intérieur
                        wG_ad = wG_ad * lbdB
                        wD_ad = wD_ad * lbdB
                        wH_ad = lbdB * (dx_apres + dx_avant) / (2*dy_avant)
                        a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
                    elif j == j_mur_int :                       # Coin D
                        wC_D = hI * dy_avant / 2
                        wG_D = lbdB * dy_avant / (2*dx_avant)
                        wH_D = lbdB * dx_avant / (2*dy_avant)
                        a_vec[j] =  wG_D; c_vec[j] = 0 ; b_vec[j] = -(wG_D+wC_D+wH_D) ; y_vec[j] = -(wH_D*T[i-1][j] + wC_D * TempI)
                #endregion
            T[i] = thomas(a_vec, b_vec, c_vec, y_vec)
            precisionResultat = max(precisionResultat, np.max(np.abs(T[i] - T_ancien[i])))
                #noeuds_modifies = np.sum(T != T_avant)
                #print(f"Itération {cptIteration} — nœuds modifiés : {noeuds_modifies} / {n*m}")
                
        #endregion



            
    print("\tPrecision : ", precisionResultat)
    #print(f"T[0][0]    = {T[0][0]:.4f}°C")        # coin B — doit être ~10°C
    #print(f"T[0][-1]   = {T[0][-1]:.4f}°C")       # coin C — doit être ~22°C
    #print(f"T[n//2][0] = {T[n//2][0]:.4f}°C")     # milieu bord gauche — ~10-11°C
    #print(f"T[n//2][-1]= {T[n//2][-1]:.4f}°C")    # milieu bord droit — ~21-22°C

# ===== DEBUG =====
print("\t===== DEBUG =====")
print(f"j_mur_int = {j_mur_int}, m-1 = {m-1}")
print(f"x[j_mur_int-2] = {x[j_mur_int-2]:.6f}")
print(f"x[j_mur_int-1] = {x[j_mur_int-1]:.6f}")
print(f"x[j_mur_int]   = {x[j_mur_int]:.6f}")
print(f"j_mur_int == m-1 ? {j_mur_int == m-1}")

i_mid = n // 2 + 3
print(f"\nProfil T au milieu (i={i_mid}, y={y[i_mid]:.2f} cm) :")
for j in range(0, m, m//10):
    print(f"  x={x[j]:.2f} cm → T={T[i_mid][j]:.2f}°C")

print("Colonne bord droit (j=j_mur_int) :")
for i in range(0, n, n//10):
    print(f"  i={i}, y={y[i]:.2f} cm → T={T[i][j_mur_int]:.2f}°C")

# T_init = (TempE + TempI) / 2  # = 16.0
# nb_non_mis_a_jour = np.sum(T == T_init)
# print(f"Nœuds encore à {T_init}°C : {nb_non_mis_a_jour} / {n*m}")
# print(f"Pourcentage : {100*nb_non_mis_a_jour/(n*m):.1f}%")


# # Combien de nœuds dans la zone cavité ?
# nb_cavite = (j_air_droite - j_air_gauche + 1) * n
# nb_alveoles = len(indices_alv_bas)
# nb_noeuds_air = 0
# for k in range(nb_alveoles):
#     nb_noeuds_air += (indices_alv_haut[k] - indices_alv_bas[k] + 1) * (j_air_droite - j_air_gauche + 1)
# print(f"Nœuds attendus dans les cavités : {nb_noeuds_air}")

# mask_init = (T == 16.0)
# import matplotlib.pyplot as plt
# plt.figure()
# plt.imshow(mask_init, origin='lower', aspect='auto',
#            extent=[x[0], x[-1], y[0], y[-1]])
# plt.colorbar(label='1 = jamais mis à jour')
# plt.title('Nœuds bloqués à 16°C')
# plt.xlabel('Épaisseur (cm)')
# plt.ylabel('Hauteur (cm)')
# plt.show()
print(f"j_enduit     = {j_enduit}  → x = {x[j_enduit]:.2f} cm")
print(f"j_air_gauche = {j_air_gauche} → x = {x[j_air_gauche]:.2f} cm")
print(f"j_air_droite = {j_air_droite} → x = {x[j_air_droite]:.2f} cm")
print(f"j_mur_int    = {j_mur_int} → x = {x[j_mur_int]:.2f} cm")

i_mid = n // 2 + 3
print("Profil T complet :")
for j in range(m):
    print(f"  x={x[j]:.3f} cm → T={T[i_mid][j]:.4f}°C")

i_source = indices_alv_bas[0] + (indices_alv_haut[0] - indices_alv_bas[0]) // 2
print(f"\nProfil complet à i={i_source} (milieu source 1, y={y[i_source]:.2f} cm) :")
for j in range(m):
    print(f"  x={x[j]:.3f} cm → T={T[i_source][j]:.4f}°C")
# =================

# Calcul du flux
dT_dy, dT_dx = np.gradient(T, y, x)
flux_x = -dT_dx
flux_y = -dT_dy
intensite = np.sqrt(flux_x**2 + flux_y**2)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# --- Plot 1 : Champ de température ---
im = ax1.imshow(
    T,
    cmap='RdYlBu_r',   # bleu (froid) → jaune → rouge (chaud), bien lisible
    origin='lower',
    extent=[x[0], x[-1], y[0], y[-1]],
    aspect='auto',
    vmin=10,
    vmax=28
)
cbar1 = plt.colorbar(im, ax=ax1, label='Température (°C)')
ax1.set_title('Champ de température', fontsize=13, fontweight='bold')
ax1.set_xlabel('Épaisseur (cm)')
ax1.set_ylabel('Hauteur (cm)')

# Lignes verticales pour repérer les interfaces
for xpos, label in [
    (x[j_mur_ext],    'Mur/Iso'),
    (x[j_isolant],    'Iso/End'),
    (x[j_enduit],     'End'),
    (x[j_air_gauche], 'Air←'),
    (x[j_air_droite], '→Air'),
    (x[j_mur_int],    'Mur int'),
]:
    ax1.axvline(x=xpos, color='white', linewidth=0.8, linestyle='--', alpha=0.6)
    ax1.text(xpos, y[-1]*1.01, label, color='white', fontsize=6,
             ha='center', va='bottom', clip_on=False)

# --- Plot 2 : Flux thermique ---
pas_fleche_i = max(1, n // 25)
pas_fleche_j = max(1, m // 25)

I_idx = np.arange(0, n, pas_fleche_i)
J_idx = np.arange(0, m, pas_fleche_j)
II, JJ = np.meshgrid(I_idx, J_idx, indexing='ij')

X_pos  = x[JJ]
Y_pos  = y[II]
FX_arr = flux_x[II, JJ]
FY_arr = flux_y[II, JJ]
INT_arr = intensite[II, JJ]

# Normaliser les flèches pour qu'elles aient toutes la même longueur
norme = np.sqrt(FX_arr**2 + FY_arr**2)
norme[norme == 0] = 1
FX_norm = FX_arr / norme
FY_norm = FY_arr / norme

sc = ax2.quiver(
    X_pos, Y_pos, FX_norm, FY_norm, INT_arr,
    cmap='plasma',
    angles='xy',
    scale=40,
    width=0.003,
    headwidth=4
)
plt.colorbar(sc, ax=ax2, label='Intensité flux (°C/cm)')
ax2.set_xlim(x[0], x[-1])
ax2.set_ylim(y[0], y[-1])
ax2.set_title('Flux thermique (direction normalisée)', fontsize=13, fontweight='bold')
ax2.set_xlabel('Épaisseur (cm)')
ax2.set_ylabel('Hauteur (cm)')
ax2.set_aspect('auto')

plt.tight_layout()
plt.show()

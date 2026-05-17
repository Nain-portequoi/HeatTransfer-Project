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
import time
t0 = time.time()

# ===== CHOIX =====
USE_THOMAS = False  # False = Gauss-Seidel, True = Thomas 
TEST_PAS_VARIABLE = True
LANCER_UNE_SIMULATION = False
pasMatriceCst = 0.005

#region Precision
precisionResultat = 1
precisionAAtteindre = 1e-5
#endregion

#region Dimension de la surface
eM = 0.2 # m
eI = 0.12
eS_m = 0.03
eB = 0.05
hM = 2
hB_m = 0.1
k_m = 0.015
#endregion

#region Pas des sources de chaleurs
pasSources_m = 0.2
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
TempE = 283.15
TempI = 295.15
#endregion

#region Coefficent de convection et Phi
hE = 25
hI = 7
phi = 100
#endregion

temperatureTempon = 10

if TEST_PAS_VARIABLE :
    #region Pas variable
    # Paramètres du raffinement
    nb_fin  = 3    # nœuds dans la zone raffinée
    nb_gros = 8    # nœuds dans la zone loin (entre deux singularités)

    # ===================== AXE Y =====================
    singularites_y = set()

    # Bords du mur
    singularites_y.add(0.0)
    singularites_y.add(hM)

    # Sources (tous les pasSources_m)
    for k in range(1, int(hM / pasSources_m)):
        singularites_y.add(float(k * pasSources_m))

    # Interfaces alvéoles : bord bas et haut de chaque cavité d'air
    for k in range(int(hM / hB_m)):
        y_alv = k * hB_m
        singularites_y.add(float(y_alv + k_m))
        singularites_y.add(float(y_alv + hB_m - k_m))

    singularites_y = sorted(singularites_y)

    y_parts = []
    for idx, y_sing in enumerate(singularites_y):
        y_parts.append([y_sing])
        
        if idx < len(singularites_y) - 1:
            y_next = singularites_y[idx + 1]
            dist = y_next - y_sing
            delta_y = min(0.05, dist / 4)
            
            mid = (y_sing + y_next) / 2
            y_parts.append(np.linspace(y_sing + delta_y/4, y_sing + delta_y, nb_fin))
            y_parts.append(np.linspace(y_sing + delta_y,   y_next - delta_y, nb_gros))
            y_parts.append(np.linspace(y_next - delta_y,   y_next,           nb_fin))

    y_asc = np.unique(np.round(np.concatenate(y_parts), 10))

    def find_idx_y_asc(val):
        idx = np.searchsorted(y_asc, val)
        if idx < len(y_asc) and abs(y_asc[idx] - val) < 1e-9:
            return idx
        # fallback : plus proche voisin
        return int(np.argmin(np.abs(y_asc - val)))

    _alv_bas_asc  = [find_idx_y_asc(float(k * hB_m + k_m))       for k in range(int(hM / hB_m))]
    _alv_haut_asc = [find_idx_y_asc(float(k * hB_m + hB_m - k_m)) for k in range(int(hM / hB_m))]

    y = y_asc[::-1]
    n = len(y)

    indices_alv_bas  = [n - 1 - idx for idx in _alv_haut_asc]  
    indices_alv_haut = [n - 1 - idx for idx in _alv_bas_asc]  

    indices_sources_y = [
        n - 1 - find_idx_y_asc(float(k * pasSources_m))
        for k in range(1, int(hM / pasSources_m))
    ]


    # Vérification
    for s in singularites_y:
        idx = np.searchsorted(y_asc, s)
        if idx >= len(y_asc) or abs(y_asc[idx] - s) > 1e-9:
            print(f"⚠️ Singularité y={s:.6f} absente ! Plus proche : y_asc[{idx}]={y_asc[idx]:.6f}")
        else:
            print(f"✅ y={s:.6f} → idx_asc={idx}, idx_retourné={n-1-idx}")

    # ===================== AXE X =====================
    singularites_x = set()
    singularites_x.add(0.0)
    singularites_x.add(float(eM))
    singularites_x.add(float(eM + eI))
    singularites_x.add(float(eM + eI + eS_m / 2))
    singularites_x.add(float(eM + eI + eS_m))
    singularites_x.add(float(eM + eI + eS_m + k_m))
    singularites_x.add(float(eM + eI + eS_m + eB - k_m))
    singularites_x.add(float(eM + eI + eS_m + eB))

    singularites_x = sorted(singularites_x)

    x_parts = []
    for idx, x_sing in enumerate(singularites_x):
        x_parts.append([x_sing])

        if idx < len(singularites_x) - 1:
            x_next = singularites_x[idx + 1]
            dist   = x_next - x_sing
            delta_x = min(0.05, dist / 4)

            x_parts.append(np.linspace(x_sing + delta_x/4, x_sing + delta_x, nb_fin))   # ← raffiné départ
            x_parts.append(np.linspace(x_sing + delta_x,   x_next - delta_x, nb_gros))  # ← gros milieu
            x_parts.append(np.linspace(x_next - delta_x,   x_next,           nb_fin))   # ← raffiné arrivée

    x = np.unique(np.round(np.concatenate(x_parts), 10))   # ← round ajouté
    m = len(x)

    # Recalcul des indices j sur le nouveau x non-uniforme
    def find_idx_x(val):
        idx = np.searchsorted(x, val)
        if idx < len(x) and abs(x[idx] - val) < 1e-9:
            return idx
        return int(np.argmin(np.abs(x - val)))

    j_bord_ext   = find_idx_x(0.0)
    j_mur_ext    = find_idx_x(float(eM))
    j_isolant    = find_idx_x(float(eM + eI))
    j_source     = find_idx_x(float(eM + eI + eS_m / 2))
    j_enduit     = find_idx_x(float(eM + eI + eS_m))
    j_air_gauche = find_idx_x(float(eM + eI + eS_m + k_m))
    j_air_droite = find_idx_x(float(eM + eI + eS_m + eB - k_m))
    j_mur_int    = find_idx_x(float(eM + eI + eS_m + eB))

    # Vérification
    if not (j_isolant < j_source < j_enduit):
        print(f"⚠️ j_source ({j_source}) mal positionné ! Isolant:{j_isolant}, Enduit:{j_enduit}")

    for s in singularites_x:
        idx = np.searchsorted(x, s)
        if idx >= len(x) or abs(x[idx] - s) > 1e-9:
            print(f"⚠️ Singularité x={s:.6f} absente ! Plus proche : x[{idx}]={x[idx]:.6f}")
        else:
            print(f"✅ x={s:.6f} → j={idx}")

    dx = pasMatriceCst
    dy = pasMatriceCst
    #endregion
else :
    #region Test pas uniforme
    dx = pasMatriceCst
    dy = pasMatriceCst

    x = np.round(np.arange(0, eM + eI + eS_m + eB + dx, dx), 10)
    y = np.round(np.arange(0, hM + dy, dy)[::-1], 10)
    m = len(x)
    n = len(y)

    j_bord_ext   = np.searchsorted(x, 0.0)
    j_mur_ext    = np.searchsorted(x, eM)
    j_isolant    = np.searchsorted(x, eM + eI)
    j_source     = np.searchsorted(x, eM + eI + eS_m / 2)
    j_enduit     = np.searchsorted(x, eM + eI + eS_m)
    j_air_gauche = np.searchsorted(x, eM + eI + eS_m + k_m)
    j_air_droite = np.searchsorted(x, eM + eI + eS_m + eB - k_m)
    j_mur_int    = np.searchsorted(x, eM + eI + eS_m + eB)
    
    # Vérification de la cohérence : j_source DOIT être entre j_isolant et j_enduit
    if not (j_isolant < j_source < j_enduit):
        print(f"⚠️ Alerte : j_source ({j_source}) est mal positionné ! Isolant:{j_isolant}, Enduit:{j_enduit}")

    def to_idx_y(val):
        return int(round((hM - val)/ dy))


    indices_alv_bas  = [min(to_idx_y(k * hB_m + hB_m - k_m), n - 1)
                        for k in range(int(hM / hB_m))]
    indices_alv_haut = [min(to_idx_y(k * hB_m + k_m), n - 1)
                        for k in range(int(hM / hB_m))]
    
    indices_sources_y = [min(to_idx_y(k * pasSources_m), n - 1)
                        for k in range(1, int(round(hM / pasSources_m)))]

    #endregion

#region Debug
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

#print(f"T.shape = {T.shape}")  # doit être (n, m) = (nb lignes Y, nb colonnes X)
print(f"n={n}, m={m}")

print(f"j_source      = {j_source}  → x = {x[j_source]:.4f} cm")
print(f"j_enduit      = {j_enduit}  → x = {x[j_enduit]:.4f} cm")
print(f"j_air_gauche  = {j_air_gauche}  → x = {x[j_air_gauche]:.4f} cm")
print(f"eM+eI+eS/2    = {eM + eI + eS_m/2:.4f} cm  ← position attendue source")

print(f"n = {n}")
print(f"indices_sources_y = {indices_sources_y}")
print(f"Hauteurs sources  = {[y[k] for k in indices_sources_y]}")

if TEST_PAS_VARIABLE :
    print(f"find_idx_y_asc(0.2) = {find_idx_y_asc(0.2)}")
    print(f"find_idx_y_asc(1.0) = {find_idx_y_asc(1.0)}")
    print(f"n - 1 - find_idx_y_asc(0.2) = {n - 1 - find_idx_y_asc(0.2)}")

# ===========================
#endregion

# Initialisation de la matrice 
T = np.linspace(TempE, TempI, m)[np.newaxis, :] * np.ones((n, 1))

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
    
    is_source_y = set(indices_sources_y)

is_cavite = np.zeros(n, dtype=bool)
idx_alv_par_ligne = np.full(n, -1, dtype=int)  # -1 = pas de cavité

for k in range(len(indices_alv_bas)):
    for i in range(indices_alv_bas[k], indices_alv_haut[k] + 1):
        is_cavite[i] = True
        idx_alv_par_ligne[i] = k


if TEST_PAS_VARIABLE : 
    dx = dy = 0.05
N_Source = len(indices_sources_y)
q_sources = phi * hM / N_Source / (dx * dy)

print(f"dx = {dx:.6f} m")
print(f"dy = {dy:.6f} m")
print(f"dx*dy = {dx*dy:.2e} m²")
print(f"q_sources = {q_sources:.2e} W/m³")

print(f"Dimensions de la matrice :\n\tNombre de lignes = {n},\n\tNombre de colonnes = {m}\n\t\tDimension totale = {n} * {m} = {n * m}")

if not LANCER_UNE_SIMULATION :
    T = np.load('T_result.npy')
    x = np.load('x_result.npy')
    y = np.load('y_result.npy')

# while precisionResultat >= precisionAAtteindre :
#     precisionResultat = 0
#     print(f"Temps : {time.time()-t0:.1f}s, Itérations : {cptIteration}")
#     cptIteration += 1
       
#     if not USE_THOMAS :
#         #region Test si l'on calcule les températures sur la ligne
#         for i in range(n) :
#             dans_cavite = is_cavite[i]
#             idx_alv = idx_alv_par_ligne[i] if dans_cavite else None
#             for j in range(m):
#                 #region Temperature Tempon
#                 temperatureTempon = T[i][j]
#                 #endregion
#                 if TEST_PAS_VARIABLE :
#                     #region Gestion des pas
#                     dx_avant = x[j] - x[j-1] if j > 0 else x[1] - x[0]
#                     dx_apres = x[j+1] - x[j] if j < m-1 else x[-1] - x[-2]
#                     dy_avant = abs(y[i] - y[i-1]) if i > 0 else abs(y[1] - y[0])
#                     dy_apres = abs(y[i+1] - y[i]) if i < n-1 else abs(y[-1] - y[-2])
#                     #endregion
#                 else :
#                     dx_avant = dx
#                     dx_apres = dx_avant
#                     dy_avant = dx_avant
#                     dy_apres = dx_avant

#                 #region Plaque du haut :
#                 if i == 0 :
#                     # Face BC
#                     wG_bc = dy_apres / (2*dx_avant)
#                     wD_bc = dy_apres / (2*dx_apres)
#                     if j == 0 :                                 # Coin B
#                         wE_B = hE * dy_apres / 2
#                         wD_B = lbdM * dy_apres / (2*dx_apres)
#                         wB_B = lbdM * dx_apres / (2*dy_apres)
#                         T[i][j] = (wE_B * TempE + wD_B * T[i][j+1] + wB_B * T[i+1][j]) / (wE_B + wD_B + wB_B)
#                     elif j < j_mur_ext :                        # Plaque du haut mur extérieur
#                         wG_bc = wG_bc * lbdM
#                         wD_bc = wD_bc * lbdM
#                         wB_bc = lbdM * (dx_apres + dx_avant) / (2*dy_apres)
#                         T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
#                     elif j == j_mur_ext :                       # Coin haut |e| mur extérieur et isolant
#                         wG_bc = wG_bc * lbdM
#                         wD_bc = wD_bc * lbdI
#                         wB_bc = (dx_apres * lbdI + dx_avant * lbdM) / (2*dy_apres)
#                         T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
#                     elif j < j_isolant :                        # Plaque du haut isolant
#                         wG_bc = wG_bc * lbdI
#                         wD_bc = wD_bc * lbdI
#                         wB_bc = lbdI * (dx_apres + dx_avant) / (2*dy_apres)
#                         T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
#                     elif j == j_isolant :                       # Coin haut |e| isolant et enduit
#                         wG_bc = wG_bc * lbdI
#                         wD_bc = wD_bc * lbdE
#                         wB_bc = (dx_apres * lbdE + dx_avant * lbdI) / (2*dy_apres)
#                         T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
#                     elif j < j_enduit :                         # Plaque du haut enduit
#                         wG_bc = wG_bc * lbdE
#                         wD_bc = wD_bc * lbdE
#                         wB_bc = lbdE * (dx_apres + dx_avant) / (2*dy_apres)
#                         T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
#                     elif j == j_enduit :                        # Coin haut |e| enduit et mur inétieur
#                         wG_bc = wG_bc * lbdE
#                         wD_bc = wD_bc * lbdB
#                         wB_bc = (dx_apres * lbdB + dx_avant * lbdE) / (2*dy_apres)
#                         T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
#                     elif j < j_mur_int :                        # Plaque du haut mur intérieur
#                         wG_bc = wG_bc * lbdB
#                         wD_bc = wD_bc * lbdB
#                         wB_bc = lbdB * (dx_apres + dx_avant) / (2*dy_apres)
#                         T[i][j] = (wG_bc * T[i][j-1] + wD_bc * T[i][j+1] + wB_bc * T[i+1][j]) / (wG_bc + wD_bc + wB_bc)
#                     elif j == j_mur_int :                       # Coin C
#                         wC_C = hI * dy_apres / 2
#                         wG_C = lbdB * dy_apres / (2*dx_avant)
#                         wB_C = lbdB * dx_avant / (2*dy_apres)
#                         T[i][j] = (wC_C * TempI + wG_C * T[i][j-1] + wB_C * T[i+1][j]) / (wC_C + wG_C + wB_C)
#                 #endregion

#                 #region Centre
#                 elif i < n - 1 :              # |e| la plaque du haut et du bas et après la plaque de gauche
#                     if j == 0 :
#                         wE_ab = hE * (dy_apres + dy_avant) / 2
#                         wD_ab = lbdM * (dy_apres + dy_avant) / (2 * dx_apres)
#                         wH_ab = lbdM * dx_apres / (2*dy_avant)
#                         wB_ab = lbdM * dx_apres / (2*dy_apres)
#                         T[i][j] = (wE_ab * TempE + wD_ab * T[i][j+1] + wH_ab * T[i-1][j] + wB_ab * T[i+1][j]) / (wE_ab + wD_ab + wB_ab + wH_ab)

#                     elif j < j_mur_ext :
#                         c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                         c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                         c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                         c_h = 2 / ((dy_apres + dy_avant) * dy_avant)
#                         T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)
#                         #print("Emplacement : point mur ext : ", {T[i][j]})

#                     elif j == j_mur_ext : 
#                         # C Mur extérieur et Isolant
#                         cMI_g = lbdM * (dy_apres + dy_avant)/(2*dx_avant)
#                         cMI_d = lbdI * (dy_apres + dy_avant)/(2*dx_apres)
#                         cMI_b = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_apres)
#                         cMI_h = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_avant)
#                         T[i][j] = (cMI_g * T[i][j - 1] + cMI_b * T[i+1][j] + cMI_h * T[i-1][j] + cMI_d * T[i][j+1])/(cMI_d + cMI_g + cMI_b + cMI_h)
#                         #print(f"Emplacement (enter mur extérieur et isolant): i = {i}, j = {j} et température = {T[i][j]}")

#                     elif j < j_isolant :
#                         c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                         c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                         c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                         c_h = 2 / ((dy_apres + dy_avant) * dy_avant)
#                         T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)
#                         #print("Emplacement : point isolant : ", {T[i][j]})

#                     elif j == j_isolant :
#                         # C Isolant et Enduit
#                         cIE_g = lbdI * (dy_apres + dy_avant)/(2*dx_avant)
#                         cIE_d = lbdE * (dy_apres + dy_avant)/(2*dx_apres)
#                         cIE_b = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_apres)
#                         cIE_h = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_avant)
#                         T[i][j] = (cIE_g * T[i][j - 1] + cIE_b * T[i+1][j] + cIE_h * T[i-1][j] + cIE_d * T[i][j+1])/(cIE_d + cIE_g + cIE_b + cIE_h)

#                     elif j < j_enduit :
#                         if i in indices_sources_y and j == j_source:
#                             term_x = (2 / (dx_avant + dx_apres)) * (T[i][j+1]/dx_apres + T[i][j-1]/dx_avant)
#                             term_y = (2 / (dy_avant + dy_apres)) * (T[i-1][j]/dy_avant + T[i+1][j]/dy_apres)
#                             denom  = 2 * (1/(dx_avant * dx_apres) + 1/(dy_avant * dy_apres))
                            
#                             # On ajoute le terme source q_sources (W/m3) divisé par la conductivité
#                             if TEST_PAS_VARIABLE :
#                                 N_Source = len(indices_sources_y)
#                                 q_sources = phi * hM / N_Source / ((dx_apres+dx_avant)/2 * (dy_apres+dy_avant)/2)
#                             T[i][j] = (term_x + term_y + (q_sources / lbdE)) / denom
#                         else : 
#                             # Équation de Laplace : Conduction pure sans source
#                             c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                             c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                             c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                             c_h = 2 / ((dy_apres + dy_avant) * dy_avant)
#                             T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h) #<- MODIFIE

#                     elif j == j_enduit :
#                         # C Enduit et Mur intérieur
#                         cEB_g = lbdE * (dy_apres + dy_avant)/(2*dx_avant)
#                         cEB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
#                         cEB_b = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_apres)
#                         cEB_h = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_avant)
#                         T[i][j] = (cEB_g * T[i][j - 1] + cEB_b * T[i+1][j] + cEB_h * T[i-1][j] + cEB_d * T[i][j+1])/(cEB_d + cEB_g + cEB_b + cEB_h)

#                     elif j < j_mur_int :
#                         if j < j_air_gauche :           # mur intérieur plein gauche
#                             c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                             c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                             c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                             c_h = 2 / ((dy_apres + dy_avant) * dy_avant)
#                             T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)

#                         elif j == j_air_gauche :          # interface mur B / air A
#                             if idx_alv is not None and i == indices_alv_bas[idx_alv] :  # coin inf gauche
#                                 cAlveole_g = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
#                                 cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
#                                 cAlveole_d = (lbdB * dy_avant + lbdA * dy_apres) / (2 * dx_apres)
#                                 cAlveole_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_avant)
#                                 T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← coin BAS de la cavité (interface B/A + bord bas)
#                             elif idx_alv is not None and i == indices_alv_haut[idx_alv] : # coin sup gauche
#                                 cAlveole_g = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
#                                 cAlveole_b = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_apres)
#                                 cAlveole_d = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
#                                 cAlveole_h = lbdB * (dx_apres + dx_avant) / (2 * dy_avant)
#                                 T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← coin HAUT de la cavité (interface B/A + bord haut)
#                             elif dans_cavite :
#                                 # C Mur intérieur et Air selon X
#                                 cBA_g = lbdB * (dy_apres + dy_avant)/(2*dx_avant)
#                                 cBA_d = lbdA * (dy_apres + dy_avant)/(2*dx_apres)
#                                 cBA_b = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_apres)
#                                 cBA_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_avant)
#                                 T[i][j] = (cBA_g * T[i][j-1] + cBA_b * T[i+1][j] + cBA_h * T[i-1][j] + cBA_d * T[i][j+1]) / (cBA_g + cBA_b + cBA_h + cBA_d) # ← interface B/A pure (plein milieu cavité)
#                             else :
#                                 c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                                 c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                                 c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                                 c_h = 2 / ((dy_apres + dy_avant) * dy_avant)
#                                 T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud dans lbdB hors cavité

#                         elif j < j_air_droite :           # plein air
#                             if idx_alv is not None and i == indices_alv_bas[idx_alv] : 
#                                 cAlveole_g = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_avant)
#                                 cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
#                                 cAlveole_d = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
#                                 cAlveole_h = lbdA * (dx_avant + dx_apres) / (2*dy_avant)
#                                 T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← bord bas cavité (air + bord horizontal)
#                             elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
#                                 cAlveole_g = (lbdA * dy_apres + lbdB * dy_avant) / (2 * dx_avant)
#                                 cAlveole_b = lbdA * (dx_apres + dx_avant) / (2 * dy_apres)
#                                 cAlveole_d = (lbdA * dy_apres + lbdB * dy_avant) / (2 * dx_apres)
#                                 cAlveole_h = lbdB * (dx_avant + dx_apres) / (2*dy_avant)
#                                 T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← bord haut cavité (air + bord horizontal)
#                             elif dans_cavite :
#                                 c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                                 c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                                 c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                                 c_h = 2 / ((dy_apres + dy_avant) * dy_avant)
#                                 T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud intérieur lbdA pur
#                             else :
#                                 c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                                 c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                                 c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                                 c_h = 2 / ((dy_apres + dy_avant) * dy_avant)
#                                 T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud dans lbdB (entre deux cavités)

#                         elif j == j_air_droite :          # interface air A / mur B
#                             if idx_alv is not None and i == indices_alv_bas[idx_alv] :  # coin inf droit
#                                 #print("Emplacement : coin alvéole inf droit")
#                                 cAlveole_d = lbdB * (dy_apres + dy_avant) / (2 * dx_apres)
#                                 cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
#                                 cAlveole_g = (lbdB * dy_avant + lbdA * dy_apres) / (2 * dx_avant)
#                                 cAlveole_h = (lbdB * dx_apres + lbdA * dx_avant) / (2 * dy_avant)
#                                 T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← coin BAS (interface A/B + bord bas)
#                             elif idx_alv is not None and i == indices_alv_haut[idx_alv] :   # coin sup droit
#                                 #print("Emplacement : coin alvéole sup droit")
#                                 cAlveole_d = lbdB * (dy_apres + dy_avant) / (2 * dx_apres)
#                                 cAlveole_h = lbdB * (dx_apres + dx_avant) / (2 * dy_avant)
#                                 cAlveole_g = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_avant)
#                                 cAlveole_b = (lbdB * dx_apres + lbdA * dx_avant) / (2 * dy_apres)
#                                 T[i][j] = (cAlveole_g * T[i][j-1] + cAlveole_h * T[i-1][j] + cAlveole_d * T[i][j+1] + cAlveole_b * T[i+1][j]) / (cAlveole_g + cAlveole_h + cAlveole_d + cAlveole_b)   # ← coin HAUT (interface A/B + bord haut)
#                             elif dans_cavite :
#                                 # C Mur intérieur et Air
#                                 cAB_g = lbdA * (dy_apres + dy_avant)/(2*dx_avant)
#                                 cAB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
#                                 cAB_b = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_apres)
#                                 cAB_h = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_avant)

#                                 T[i][j] = (cAB_g * T[i][j-1] + cAB_b * T[i+1][j] + cAB_h * T[i-1][j] + cAB_d * T[i][j+1]) / (cAB_g + cAB_b + cAB_h + cAB_d) # ← interface A/B pure
#                             else :
#                                 #print(f"else générique : i={i}, j={j}")
#                                 c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                                 c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                                 c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                                 c_h = 2 / ((dy_apres + dy_avant) * dy_avant)
#                                 T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)   # ← nœud dans lbdB hors cavité
                        
#                         else :
#                             c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                             c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                             c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                             c_h = 2 / ((dy_apres + dy_avant) * dy_avant)
#                             T[i][j] = (c_d * T[i][j+1] + c_g * T[i][j-1] + c_b * T[i+1][j] + c_h * T[i-1][j]) / (c_g + c_d + c_b + c_h)

#                     elif j == j_mur_int :
#                         wI_cd = hI * (dy_apres + dy_avant) / 2
#                         wG_cd = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
#                         wH_cd = lbdB * dx_avant / (2*dy_avant)
#                         wB_cd = lbdB * dx_avant / (2*dy_apres)
#                         T[i][j] = (wI_cd * TempI + wG_cd * T[i][j-1] + wH_cd * T[i-1][j] + wB_cd * T[i+1][j]) / (wB_cd + wI_cd + wH_cd + wG_cd)
                        
#                 #endregion

#                 #region Plaque du bas :
#                 elif i == n - 1:
#                     # Face AD
#                     wG_ad = dy_avant / (2*dx_avant)
#                     wD_ad = dy_avant / (2*dx_apres)
#                     if j == 0 :                                 # Coin A
#                         wE_A = hE * dy_avant / 2
#                         wD_A = lbdM * dy_avant / (2*dx_apres)
#                         wH_A = lbdM * dx_apres / (2*dy_avant)
#                         T[i][j] = (wE_A * TempE + wD_A * T[i][j+1] + wH_A * T[i-1][j]) / (wE_A + wD_A + wH_A)
#                     elif j < j_mur_ext :                        # Plaque du bas mur extérieur
#                         wG_ad = wG_ad * lbdM
#                         wD_ad = wD_ad * lbdM
#                         wH_ad = lbdM * (dx_apres + dx_avant) / (2*dy_avant)
#                         T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
#                     elif j == j_mur_ext :                       # Coin bas |e| mur extérieur et isolant
#                         wG_ad = wG_ad * lbdM
#                         wD_ad = wD_ad * lbdI
#                         wH_ad = (dx_apres * lbdI + dx_avant * lbdM) / (2*dy_avant)
#                         T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
#                     elif j < j_isolant :                        # Plaque du bas isolant
#                         wG_ad = wG_ad * lbdI
#                         wD_ad = wD_ad * lbdI
#                         wH_ad = lbdI * (dx_apres + dx_avant) / (2*dy_avant)
#                         T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
#                     elif j == j_isolant :                       # Coin bas |e| isolant et enduit
#                         wG_ad = wG_ad * lbdI
#                         wD_ad = wD_ad * lbdE
#                         wH_ad = (dx_apres * lbdE + dx_avant * lbdI) / (2*dy_avant)
#                         T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
#                     elif j < j_enduit :                         # Plaque du bas enduit
#                         wG_ad = wG_ad * lbdE
#                         wD_ad = wD_ad * lbdE
#                         wH_ad = lbdE * (dx_apres + dx_avant) / (2*dy_avant)
#                         T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
#                     elif j == j_enduit :                        # Coin bas |e| enduit et mur inétieur
#                         wG_ad = wG_ad * lbdE
#                         wD_ad = wD_ad * lbdB
#                         wH_ad = (dx_apres * lbdB + dx_avant * lbdE) / (2*dy_avant)
#                         T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
#                     elif j < j_mur_int :                        # Plaque du bas mur intérieur
#                         wG_ad = wG_ad * lbdB
#                         wD_ad = wD_ad * lbdB
#                         wH_ad = lbdB * (dx_apres + dx_avant) / (2*dy_avant)
#                         T[i][j] = (wG_ad * T[i][j-1] + wD_ad * T[i][j+1] + wH_ad * T[i-1][j]) / (wG_ad + wD_ad + wH_ad)
#                     elif j == j_mur_int :                       # Coin D
#                         wC_D = hI * dy_avant / 2
#                         wG_D = lbdB * dy_avant / (2*dx_avant)
#                         wH_D = lbdB * dx_avant / (2*dy_avant)
#                         T[i][j] = (wC_D * TempI + wG_D * T[i][j-1] + wH_D * T[i-1][j]) / (wC_D + wG_D + wH_D)
#                 precisionResultat = max(precisionResultat, abs(T[i][j] - temperatureTempon))
#                 #endregion
#         #endregion

#     else :
#         T_avant = T.copy()
#         #region Test si l'on calcule les températures sur la ligne
#         for i in range(n) :
#             a_vec = np.zeros(m)
#             b_vec = np.zeros(m)
#             c_vec = np.zeros(m)
#             y_vec = np.zeros(m)
#             dans_cavite = any(
#             indices_alv_bas[k] <= i <= indices_alv_haut[k]
#             for k in range(len(indices_alv_bas))
#             )
#             idx_alv = next(
#             (k for k in range(len(indices_alv_bas)) if indices_alv_bas[k] <= i <= indices_alv_haut[k]), None
#             )
#             for j in range(m):

#                 #region Gestion des pas
#                 if TEST_PAS_VARIABLE :
#                     #region Gestion des pas
#                     dx_avant = x[j] - x[j-1] if j > 0 else x[1] - x[0]
#                     dx_apres = x[j+1] - x[j] if j < m-1 else x[-1] - x[-2]
#                     dy_avant = abs(y[i] - y[i-1]) if i > 0 else abs(y[1] - y[0])
#                     dy_apres = abs(y[i+1] - y[i]) if i < n-1 else abs(y[-1] - y[-2])
#                     #endregion
#                 else :
#                     dx_avant = dx
#                     dx_apres = dx_avant
#                     dy_avant = dx_avant
#                     dy_apres = dx_avant

#                 #endregion

#                 #region C
#                 # C Intérieur d'un matériau
#                 c_d = 2 / ((dx_apres + dx_avant) * dx_apres)
#                 c_g = 2 / ((dx_apres + dx_avant) * dx_avant)
#                 c_b = 2 / ((dy_apres + dy_avant) * dy_apres)
#                 c_h = 2 / ((dy_apres + dy_avant) * dy_avant)

#                 # C Mur extérieur et Isolant
#                 cMI_g = lbdM * (dy_apres + dy_avant)/(2*dx_avant)
#                 cMI_d = lbdI * (dy_apres + dy_avant)/(2*dx_apres)
#                 cMI_b = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_apres)
#                 cMI_h = (lbdM * dx_avant + lbdI * dx_apres) / (2 * dy_avant)

#                 # C Isolant et Enduit
#                 cIE_g = lbdI * (dy_apres + dy_avant)/(2*dx_avant)
#                 cIE_d = lbdE * (dy_apres + dy_avant)/(2*dx_apres)
#                 cIE_b = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_apres)
#                 cIE_h = (lbdI * dx_avant + lbdE * dx_apres) / (2 * dy_avant)

#                 # C Enduit et Mur intérieur
#                 cEB_g = lbdE * (dy_apres + dy_avant)/(2*dx_avant)
#                 cEB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
#                 cEB_b = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_apres)
#                 cEB_h = (lbdE * dx_avant + lbdB * dx_apres) / (2 * dy_avant)

#                 # C Mur intérieur et Air selon X
#                 cBA_g = lbdB * (dy_apres + dy_avant)/(2*dx_avant)
#                 cBA_d = lbdA * (dy_apres + dy_avant)/(2*dx_apres)
#                 cBA_b = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_apres)
#                 cBA_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_avant)

#                 # C Mur intérieur et Air
#                 cAB_g = lbdA * (dy_apres + dy_avant)/(2*dx_avant)
#                 cAB_d = lbdB * (dy_apres + dy_avant)/(2*dx_apres)
#                 cAB_b = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_apres)
#                 cAB_h = (lbdA * dx_avant + lbdB * dx_apres) / (2 * dy_avant)

#                 # C Sources
#                 c1 = lbdE * (dy_apres + dy_avant) / 2
#                 c2 = lbdE * (dx_apres + dx_avant) / 2
                
#                 #endregion

#                 #region W
#                 # Face AB   
#                 wE_ab = hE * (dy_apres + dy_avant) / 2
#                 wD_ab = lbdM * (dy_apres + dy_avant) / (2 * dx_apres)
#                 wH_ab = lbdM * dx_apres / (2*dy_avant)
#                 wB_ab = lbdM * dx_apres / (2*dy_apres)

#                 # Face CD   
#                 wI_cd = hI * (dy_apres + dy_avant) / 2
#                 wG_cd = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
#                 wH_cd = lbdB * dx_avant / (2*dy_avant)
#                 wB_cd = lbdB * dx_avant / (2*dy_apres)


#                 #endregion
                
#                 #region Plaque du haut :
#                 if i == 0 :
#                     # Face BC
#                     wG_bc = dy_apres / (2*dx_avant)
#                     wD_bc = dy_apres / (2*dx_apres)
#                     if j == 0 :                                 # Coin B
#                         wE_B = hE * dy_apres / 2
#                         wD_B = lbdM * dy_apres / (2*dx_apres)
#                         wB_B = lbdM * dx_apres / (2*dy_apres)
#                         a_vec[j] = 0 ; c_vec[j] = wD_B ; b_vec[j] = -(wE_B+wD_B+wB_B) ; y_vec[j] = -(wE_B*TempE + wB_B*T[i+1][j])
#                     elif j < j_mur_ext :                        # Plaque du haut mur extérieur
#                         wG_bc = wG_bc * lbdM
#                         wD_bc = wD_bc * lbdM
#                         wB_bc = lbdM * (dx_apres + dx_avant) / (2*dy_apres)
#                         a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
#                     elif j == j_mur_ext :                       # Coin haut |e| mur extérieur et isolant
#                         wG_bc = wG_bc * lbdM
#                         wD_bc = wD_bc * lbdI
#                         wB_bc = (dx_apres * lbdI + dx_avant * lbdM) / (2*dy_apres)
#                         a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
#                     elif j < j_isolant :                        # Plaque du haut isolant
#                         wG_bc = wG_bc * lbdI
#                         wD_bc = wD_bc * lbdI
#                         wB_bc = lbdI * (dx_apres + dx_avant) / (2*dy_apres)
#                         a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
#                     elif j == j_isolant :                       # Coin haut |e| isolant et enduit
#                         wG_bc = wG_bc * lbdI
#                         wD_bc = wD_bc * lbdE
#                         wB_bc = (dx_apres * lbdE + dx_avant * lbdI) / (2*dy_apres)
#                         a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
#                     elif j < j_enduit :                         # Plaque du haut enduit
#                         wG_bc = wG_bc * lbdE
#                         wD_bc = wD_bc * lbdE
#                         wB_bc = lbdE * (dx_apres + dx_avant) / (2*dy_apres)
#                         a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
#                     elif j == j_enduit :                        # Coin haut |e| enduit et mur inétieur
#                         wG_bc = wG_bc * lbdE
#                         wD_bc = wD_bc * lbdB
#                         wB_bc = (dx_apres * lbdB + dx_avant * lbdE) / (2*dy_apres)
#                         a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
#                     elif j < j_mur_int :                        # Plaque du haut mur intérieur
#                         wG_bc = wG_bc * lbdB
#                         wD_bc = wD_bc * lbdB
#                         wB_bc = lbdB * (dx_apres + dx_avant) / (2*dy_apres)
#                         a_vec[j] =  wG_bc; c_vec[j] = wD_bc ; b_vec[j] = -(wG_bc+wD_bc+wB_bc) ; y_vec[j] = -(wB_bc*T[i+1][j])
#                     elif j == j_mur_int :                       # Coin C
#                         wC_C = hI * dy_apres / 2
#                         wG_C = lbdB * dy_apres / (2*dx_avant)
#                         wB_C = lbdB * dx_avant / (2*dy_apres)
#                         a_vec[j] =  wG_C; c_vec[j] = 0 ; b_vec[j] = -(wC_C+wG_C+wB_C) ; y_vec[j] = -(wC_C * TempI + wB_C*T[i+1][j])
#                 #endregion

#                 #region Centre
#                 elif i < n - 1 :              # |e| la plaque du haut et du bas et après la plaque de gauche
#                     if j == 0 :
#                         a_vec[j] = 0
#                         c_vec[j] = wD_ab
#                         b_vec[j] = -(wD_ab + wE_ab + wH_ab + wB_ab)
#                         y_vec[j] = -(wH_ab * T[i-1][j] + wB_ab * T[i+1][j] + wE_ab * TempE)

#                     elif j < j_mur_ext :
#                         a_vec[j] = c_g
#                         c_vec[j] = c_d
#                         b_vec[j] = -(c_g + c_d + c_h + c_b)
#                         y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])
#                         #print("Emplacement : point mur ext : ", {T[i][j]})

#                     elif j == j_mur_ext : 
#                         a_vec[j] = cMI_g
#                         c_vec[j] = cMI_d
#                         b_vec[j] = -(cMI_g + cMI_d + cMI_h + cMI_b)
#                         y_vec[j] = -(cMI_h * T[i-1][j] + cMI_b * T[i+1][j])
#                         #print(f"Emplacement (enter mur extérieur et isolant): i = {i}, j = {j} et température = {T[i][j]}")

#                     elif j < j_isolant :
#                         a_vec[j] = c_g
#                         c_vec[j] = c_d
#                         b_vec[j] = -(c_g + c_d + c_h + c_b)
#                         y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])
#                         #print("Emplacement : point isolant : ", {T[i][j]})

#                     elif j == j_isolant :
#                         a_vec[j] = cIE_g
#                         c_vec[j] = cIE_d
#                         b_vec[j] = -(cIE_g + cIE_d + cIE_h + cIE_b)
#                         y_vec[j] = -(cIE_h * T[i-1][j] + cIE_b * T[i+1][j])

#                     elif j < j_enduit :
#                         if i in is_source_y and j == j_source :             # Position sur les sources de chaleur 
#                             cS_g = c1 / dx_avant
#                             cS_d = c1 / dx_apres
#                             cS_h = c2 / dy_avant
#                             cS_b = c2 / dy_apres

#                             a_vec[j] = cS_g
#                             c_vec[j] = cS_d
#                             b_vec[j] = -(cS_g + cS_d + cS_h + cS_b)
#                             y_vec[j] = -(cS_h * T[i-1][j] + cS_b * T[i+1][j]) - q_sources * dx * dy
#                             #print(f"Emplacement : point enduit : {T[i][j]} et emplacement i={i}, j = {j}")
#                         else : 
#                             #print(f"else générique : i={i}, j={j}")
#                             a_vec[j] = c_g
#                             c_vec[j] = c_d
#                             b_vec[j] = -(c_g + c_d + c_h + c_b)
#                             y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])

#                     elif j == j_enduit :
#                         a_vec[j] = cEB_g
#                         c_vec[j] = cEB_d
#                         b_vec[j] = -(cEB_g + cEB_d + cEB_h + cEB_b)
#                         y_vec[j] = -(cEB_h * T[i-1][j] + cEB_b * T[i+1][j])

#                     elif j < j_mur_int :
#                         if j < j_air_gauche :           # mur intérieur plein gauche
#                             a_vec[j] = c_g
#                             c_vec[j] = c_d
#                             b_vec[j] = -(c_g + c_d + c_h + c_b)
#                             y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])

#                         elif j == j_air_gauche :          # interface mur B / air A
#                             if idx_alv is not None and i == indices_alv_bas[idx_alv] : 
#                                 cAlveole_g = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
#                                 cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
#                                 cAlveole_d = (lbdB * dy_avant + lbdA * dy_apres) / (2 * dx_apres)
#                                 cAlveole_h = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_avant)
#                                 a_vec[j] = cAlveole_g
#                                 c_vec[j] = cAlveole_d
#                                 b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
#                                 y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← coin BAS de la cavité (interface B/A + bord bas)
#                             elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
#                                 cAlveole_g = lbdB * (dy_apres + dy_avant) / (2 * dx_avant)
#                                 cAlveole_b = (lbdB * dx_avant + lbdA * dx_apres) / (2 * dy_apres)
#                                 cAlveole_d = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
#                                 cAlveole_h = lbdB * (dx_apres + dx_avant) / (2 * dy_avant)
#                                 a_vec[j] = cAlveole_g
#                                 c_vec[j] = cAlveole_d
#                                 b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
#                                 y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← coin HAUT de la cavité (interface B/A + bord haut)
#                             elif dans_cavite :
#                                 a_vec[j] = cBA_g 
#                                 c_vec[j] = cBA_d
#                                 b_vec[j] = -(cBA_g + cBA_d + cBA_h + cBA_b)
#                                 y_vec[j] = -(cBA_h * T[i-1][j] + cBA_b * T[i+1][j]) # ← interface B/A pure (plein milieu cavité)
#                             else :
#                                 a_vec[j] = c_g
#                                 c_vec[j] = c_d
#                                 b_vec[j] = -(c_g + c_d + c_h + c_b)
#                                 y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])   # ← nœud dans lbdB hors cavité

#                         elif j < j_air_droite :           # plein air
#                             if idx_alv is not None and i == indices_alv_bas[idx_alv] :
#                                 cAlveole_g = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_avant)
#                                 cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
#                                 cAlveole_d = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_apres)
#                                 cAlveole_h = lbdA * (dx_avant + dx_apres) / (2*dy_avant)
#                                 a_vec[j] = cAlveole_g
#                                 c_vec[j] = cAlveole_d
#                                 b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
#                                 y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← bord bas cavité (air + bord horizontal)
#                             elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
#                                 cAlveole_g = (lbdA * dy_apres + lbdB * dy_avant) / (2 * dx_apres)
#                                 cAlveole_b = lbdA * (dx_apres + dx_avant) / (2 * dy_apres)
#                                 cAlveole_d = (lbdA * dy_apres + lbdB * dy_avant) / (2 * dx_apres)
#                                 cAlveole_h = lbdB * (dx_avant + dx_apres) / (2*dy_avant)
#                                 a_vec[j] = cAlveole_g
#                                 c_vec[j] = cAlveole_d
#                                 b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
#                                 y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← bord haut cavité (air + bord horizontal)
#                             elif dans_cavite :
#                                 a_vec[j] = c_g * lbdA
#                                 c_vec[j] = c_d * lbdA
#                                 b_vec[j] = -(c_g + c_d + c_h + c_b) * lbdA
#                                 y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j]) * lbdA   # ← nœud intérieur lbdA pur
#                             else :
#                                 a_vec[j] = c_g
#                                 c_vec[j] = c_d
#                                 b_vec[j] = -(c_g + c_d + c_h + c_b)
#                                 y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])   # ← nœud dans lbdB (entre deux cavités)

#                         elif j == j_air_droite :          # interface air A / mur B
#                             if idx_alv is not None and i == indices_alv_bas[idx_alv] :
#                                 #print("Emplacement : coin alvéole inf droit")
#                                 cAlveole_d = lbdB * (dy_apres + dy_avant) / (2 * dx_apres)
#                                 cAlveole_b = lbdB * (dx_apres + dx_avant) / (2 * dy_apres)
#                                 cAlveole_g = (lbdB * dy_avant + lbdA * dy_apres) / (2 * dx_avant)
#                                 cAlveole_h = (lbdB * dx_apres + lbdA * dx_avant) / (2 * dy_avant)
#                                 a_vec[j] = cAlveole_g
#                                 c_vec[j] = cAlveole_d
#                                 b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
#                                 y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← coin BAS (interface A/B + bord bas)
#                             elif idx_alv is not None and i == indices_alv_haut[idx_alv] :
#                                 #print("Emplacement : coin alvéole sup droit")
#                                 cAlveole_d = lbdB * (dy_apres + dy_avant) / (2 * dx_apres)
#                                 cAlveole_h = lbdB * (dx_apres + dx_avant) / (2 * dy_avant)
#                                 cAlveole_g = (lbdB * dy_apres + lbdA * dy_avant) / (2 * dx_avant)
#                                 cAlveole_b = (lbdB * dx_apres + lbdA * dx_avant) / (2 * dy_apres)
#                                 a_vec[j] = cAlveole_g
#                                 c_vec[j] = cAlveole_d
#                                 b_vec[j] = -(cAlveole_g + cAlveole_d + cAlveole_h + cAlveole_b)
#                                 y_vec[j] = -(cAlveole_h * T[i-1][j] + cAlveole_b * T[i+1][j])   # ← coin HAUT (interface A/B + bord haut)
#                             elif dans_cavite :
#                                 a_vec[j] = cAB_g
#                                 c_vec[j] = cAB_d
#                                 b_vec[j] = -(cAB_g + cAB_d + cAB_h + cAB_b)
#                                 y_vec[j] = -(cAB_h * T[i-1][j] + cAB_b * T[i+1][j]) # ← interface A/B pure
#                             else :
#                                 #print(f"else générique : i={i}, j={j}")
#                                 a_vec[j] = c_g
#                                 c_vec[j] = c_d
#                                 b_vec[j] = -(c_g + c_d + c_h + c_b)
#                                 y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])   # ← nœud dans lbdB hors cavité
#                         else :
#                             a_vec[j] = c_g
#                             c_vec[j] = c_d
#                             b_vec[j] = -(c_g + c_d + c_h + c_b)
#                             y_vec[j] = -(c_h * T[i-1][j] + c_b * T[i+1][j])

#                     elif j == j_mur_int :
#                         a_vec[j] = wG_cd
#                         c_vec[j] = 0                    # pas de voisin droit
#                         b_vec[j] = -(wG_cd + wI_cd + wH_cd + wB_cd)
#                         y_vec[j] = -(wH_cd * T[i-1][j] + wB_cd * T[i+1][j] + wI_cd * TempI)
                        
#                 #endregion

#                 #region Plaque du bas :
#                 elif i == n - 1:
#                     # Face AD
#                     wG_ad = dy_avant / (2*dx_avant)
#                     wD_ad = dy_avant / (2*dx_apres)
#                     if j == 0 :                                 # Coin A
#                         wE_A = hE * dy_avant / 2
#                         wD_A = lbdM * dy_avant / (2*dx_apres)
#                         wH_A = lbdM * dx_apres / (2*dy_avant)
#                         a_vec[j] =  0; c_vec[j] = wD_A ; b_vec[j] = -(wD_A+wE_A+wH_A) ; y_vec[j] = -(wH_A * T[i-1][j] + wE_A * TempE)
#                     elif j < j_mur_ext :                        # Plaque du bas mur extérieur
#                         wG_ad = wG_ad * lbdM
#                         wD_ad = wD_ad * lbdM
#                         wH_ad = lbdM * (dx_apres + dx_avant) / (2*dy_avant)
#                         a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
#                     elif j == j_mur_ext :                       # Coin bas |e| mur extérieur et isolant
#                         wG_ad = wG_ad * lbdM
#                         wD_ad = wD_ad * lbdI
#                         wH_ad = (dx_apres * lbdI + dx_avant * lbdM) / (2*dy_avant)
#                         a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
#                     elif j < j_isolant :                        # Plaque du bas isolant
#                         wG_ad = wG_ad * lbdI
#                         wD_ad = wD_ad * lbdI
#                         wH_ad = lbdI * (dx_apres + dx_avant) / (2*dy_avant)
#                         a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
#                     elif j == j_isolant :                       # Coin bas |e| isolant et enduit
#                         wG_ad = wG_ad * lbdI
#                         wD_ad = wD_ad * lbdE
#                         wH_ad = (dx_apres * lbdE + dx_avant * lbdI) / (2*dy_avant)
#                         a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
#                     elif j < j_enduit :                         # Plaque du bas enduit
#                         wG_ad = wG_ad * lbdE
#                         wD_ad = wD_ad * lbdE
#                         wH_ad = lbdE * (dx_apres + dx_avant) / (2*dy_avant)
#                         a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
#                     elif j == j_enduit :                        # Coin bas |e| enduit et mur inétieur
#                         wG_ad = wG_ad * lbdE
#                         wD_ad = wD_ad * lbdB
#                         wH_ad = (dx_apres * lbdB + dx_avant * lbdE) / (2*dy_avant)
#                         a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
#                     elif j < j_mur_int :                        # Plaque du bas mur intérieur
#                         wG_ad = wG_ad * lbdB
#                         wD_ad = wD_ad * lbdB
#                         wH_ad = lbdB * (dx_apres + dx_avant) / (2*dy_avant)
#                         a_vec[j] =  wG_ad; c_vec[j] = wD_ad ; b_vec[j] = -(wG_ad+wD_ad+wH_ad) ; y_vec[j] = -(wH_ad*T[i-1][j])
#                     elif j == j_mur_int :                       # Coin D
#                         wC_D = hI * dy_avant / 2
#                         wG_D = lbdB * dy_avant / (2*dx_avant)
#                         wH_D = lbdB * dx_avant / (2*dy_avant)
#                         a_vec[j] =  wG_D; c_vec[j] = 0 ; b_vec[j] = -(wG_D+wC_D+wH_D) ; y_vec[j] = -(wH_D*T[i-1][j] + wC_D * TempI)
#                 #endregion
#             T[i] = thomas(a_vec, b_vec, c_vec, y_vec)
#             precisionResultat = np.max(np.abs(T - T_avant)) / np.max(np.abs(T))
#             print(f"La température vaut : {T[i][j]}")
                
#         #endregion
       
#     print("\tPrecision : ", precisionResultat)



np.save('T_result5.npy', T)
np.save('x_result5.npy', x)
np.save('y_result5.npy', y)
print("✅ T sauvegardé !")

#region Debug
# ===== DEBUG =====
# print("\t===== DEBUG =====")
# print(f"j_mur_int = {j_mur_int}, m-1 = {m-1}")
# print(f"x[j_mur_int-2] = {x[j_mur_int-2]:.6f}")
# print(f"x[j_mur_int-1] = {x[j_mur_int-1]:.6f}")
# print(f"x[j_mur_int]   = {x[j_mur_int]:.6f}")
# print(f"j_mur_int == m-1 ? {j_mur_int == m-1}")

# i_mid = n // 2 + 3
# # print(f"\nProfil T au milieu (i={i_mid}, y={y[i_mid]:.2f} m) :")
# # for j in range(0, m, m//10):
# #     print(f"  x={x[j]:.2f} m → T={T[i_mid][j]:.2f}°C")

# print("Colonne bord droit (j=j_mur_int) :")
# for i in range(0, n, n//10):
#     print(f"  i={i}, y={y[i]:.2f} m → T={T[i][j_mur_int]:.2f}°C")

# print(f"j_enduit     = {j_enduit}  → x = {x[j_enduit]:.2f} m")
# print(f"j_air_gauche = {j_air_gauche} → x = {x[j_air_gauche]:.2f} m")
# print(f"j_air_droite = {j_air_droite} → x = {x[j_air_droite]:.2f} m")
# print(f"j_mur_int    = {j_mur_int} → x = {x[j_mur_int]:.2f} m")

# i_mid = n // 2 + 3
# print("Profil T complet :")
# for j in range(m):
#     print(f"  x={x[j]:.3f} m → T={T[i_mid][j]:.4f}°C")

# i_source = indices_alv_bas[0] + (indices_alv_haut[0] - indices_alv_bas[0]) // 2
# print(f"\nProfil complet à i={i_source} (milieu source 1, y={y[i_source]:.2f} m) :")
# for j in range(m):
#     print(f"  x={x[j]:.3f} m → T={T[i_source][j]:.4f}°C")
# if TEST_PAS_VARIABLE :
#     print(f"y[120] = {y[120]:.6f} m   (hauteur physique)")
#     print(f"Sources y : {[y_asc[n-1-idx] for idx in [n-1-s for s in indices_sources_y]]}")
#     # Plus simple :
#     print(f"indices_sources_y = {indices_sources_y}")
#     print(f"Hauteurs sources  = {[y[k] for k in indices_sources_y]}")
#     print(f"j_source = {j_source}, x[j_source] = {x[j_source]:.6f} m")
# Doit être ≈ eM + eI + eS_m/2 = 0.335 m


GRAPHIQUE_DE_TEMPERATURE = True
if GRAPHIQUE_DE_TEMPERATURE :
    avrg = np.mean(T, axis=0)  # moyenne par colonne
    temperatureRightWall = T[:, -1]
    i_source = indices_sources_y[len(indices_sources_y)//2]  # source du milieu
    print(f"Tracé à i={i_source}, y={y[i_source]:.4f} m")
    plt.figure(figsize=(6,4))
    plt.plot(x, T[i_source, :], '-b')
    plt.xlabel('x [m]')
    plt.ylabel('T [K]')
    plt.title(f'Profil de température à i = {i_source}')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(6, 4))
    plt.plot(x, avrg, '-b')
    plt.xlabel('x [m]')
    plt.ylabel('T [K]')
    plt.title('Profil de température moyenne')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(6, 4))
    plt.plot(y, temperatureRightWall, '-b')
    plt.xlabel('y [m]')
    plt.ylabel('T [K]')
    plt.title('Profil de température au mur extérieur (x = L)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
# =================
#endregion

import matplotlib.patches as patches

def overlay_geometrie(ax):
    x_debut = x[j_mur_ext]    # début de la zone visible (mur ext)
    x_fin   = x[j_mur_int]    # fin de la zone visible (mur int)

    # Couches avec transparence
    ax.add_patch(patches.Rectangle((x[j_mur_ext],    0), eI,   hM, facecolor='lightgray', alpha=0.15, edgecolor='none'))
    ax.add_patch(patches.Rectangle((x[j_isolant],    0), eS_m, hM, facecolor='beige',     alpha=0.20, edgecolor='none'))
    ax.add_patch(patches.Rectangle((x[j_enduit],     0), eB,   hM, facecolor='whitesmoke',alpha=0.15, edgecolor='none'))

    # Cavités d'air
    for k in range(int(hM / hB_m)):
        y_bas = k * hB_m + k_m
        h_air = hB_m - 2 * k_m
        if y_bas + h_air <= hM:
            ax.add_patch(patches.Rectangle(
                (x[j_enduit] + k_m, y_bas),
                eB - 2 * k_m, h_air,
                facecolor='skyblue', alpha=0.25, edgecolor='none'
            ))

    # Sources de chaleur
    x_source = x[j_source]
    for k in range(1, int(round(hM / pasSources_m))):
        y_src = k * pasSources_m
        if y_src < hM:
            ax.plot(x_source, y_src, 'ro', markersize=4, alpha=0.6)

    # Interfaces verticales
    for xpos in [x[j_mur_ext], x[j_isolant], x[j_enduit], x[j_mur_int]]:
        ax.axvline(x=xpos, color='white', linewidth=0.8, linestyle='--', alpha=0.5)


# ============================================================
# Calcul du gradient et des flux
# ============================================================
n, m = T.shape       
j_bord_ext   = find_idx_x(0.0)
j_mur_ext    = find_idx_x(float(eM))
j_isolant    = find_idx_x(float(eM + eI))
j_source     = find_idx_x(float(eM + eI + eS_m / 2))
j_enduit     = find_idx_x(float(eM + eI + eS_m))
j_air_gauche = find_idx_x(float(eM + eI + eS_m + k_m))
j_air_droite = find_idx_x(float(eM + eI + eS_m + eB - k_m))
j_mur_int    = find_idx_x(float(eM + eI + eS_m + eB))

T_flipped = np.flipud(T)
y_croissant = y[::-1]

dT_dy_flipped, dT_dx_flipped = np.gradient(T_flipped, y_croissant, x)

dT_dx = np.zeros_like(T)

# Points internes
for i in range(n):
    for j in range(1, m-1):
        dxm = x[j]   - x[j-1]
        dxp = x[j+1] - x[j]
        dT_dx[i, j] = (
            -dxp / (dxm*(dxm+dxp)) * T[i, j-1]
            + (dxp-dxm) / (dxm*dxp) * T[i, j]
            + dxm / (dxp*(dxm+dxp)) * T[i, j+1]
        )

# Bords (dérivée unilatérale premier ordre)
dT_dx[:, 0]    = (T[:, 1]  - T[:, 0])    / (x[1]  - x[0])
dT_dx[:, m-1]  = (T[:, m-1] - T[:, m-2]) / (x[m-1] - x[m-2])

dT_dy = np.zeros_like(T)

for i in range(1, n-1):
    for j in range(m):
        dym = y[i]   - y[i-1]
        dyp = y[i+1] - y[i]
        dT_dy[i, j] = (
            -dyp / (dym*(dym+dyp)) * T[i-1, j]
            + (dyp-dym) / (dym*dyp) * T[i, j]
            + dym / (dyp*(dym+dyp)) * T[i+1, j]
        )

dT_dy[0, :]    = (T[1, :]    - T[0, :])    / (y[1]  - y[0])
dT_dy[n-1, :]  = (T[n-1, :]  - T[n-2, :])  / (y[n-1] - y[n-2])

flux_x = -dT_dx
flux_y = -dT_dy
intensite = np.sqrt(flux_x**2 + flux_y**2)

# Recalcul flux réel
K = np.full((n, m), lbdM)                     
K[:, j_mur_ext:j_isolant]    = lbdI           
K[:, j_isolant:j_enduit]     = lbdE                
K[:, j_enduit:j_mur_int]     = lbdB                 
for idx_b, idx_h in zip(indices_alv_bas, indices_alv_haut):
    K[idx_b:idx_h, j_air_gauche:j_air_droite] = lbdA  # alvéoles d'air
print("K.shape    =", K.shape)
print("dT_dx.shape =", dT_dx.shape)

flux_x_reel = -K * dT_dx
flux_y_reel = -K * dT_dy
intensite_reel = np.sqrt(flux_x_reel**2 + flux_y_reel**2)

# ============================================================
# Figure 1 : Champ de température + flux normalisé
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# --- ax1 : Champ de température ---
XX, YY = np.meshgrid(x, y)
im = ax1.pcolormesh(XX, YY, T, cmap='hot', shading='auto')
plt.colorbar(im, ax=ax1, label='Température (K)')
ax1.set_title('Champs des températures', fontsize=13, fontweight='bold')
ax1.set_xlabel('Épaisseur (m)')
ax1.set_ylabel('Hauteur (m)')
ax1.set_xlim(x[0], x[-1])
ax1.set_ylim(y[0], y[-1])

for xpos in [x[j_mur_ext], x[j_isolant], x[j_enduit], x[j_air_gauche], x[j_air_droite], x[j_mur_int]]:
    ax1.axvline(x=xpos, color='white', linewidth=0.8, linestyle='--', alpha=0.6)

def format_coord_T(xc, yc):
    j = np.argmin(np.abs(x - xc))
    i = np.argmin(np.abs(y - yc))
    if 0 <= i < n and 0 <= j < m:
        return f'x={xc:.3f} m  y={yc:.3f} m  →  T = {T[i,j]:.2f} K  ({T[i,j]-273.15:.2f} °C)'
    return f'x={xc:.3f} m  y={yc:.3f} m'
ax1.format_coord = format_coord_T

# --- ax2 : Flux normalisé (direction) ---
pas_fleche_i = max(1, n // 18)
I_idx = np.arange(0, n, pas_fleche_i)
J_idx = np.arange(j_mur_ext, j_mur_int, max(1, (j_mur_int - j_mur_ext) // 18))
II, JJ = np.meshgrid(I_idx, J_idx, indexing='ij')

X_pos   = x[JJ]
Y_pos   = y[II]
FX_arr  = flux_x[II, JJ]
FY_arr  = flux_y[II, JJ]
INT_arr = intensite[II, JJ]

norme = np.sqrt(FX_arr**2 + FY_arr**2)
norme[norme == 0] = 1
FX_norm = FX_arr / norme
FY_norm = FY_arr / norme

sc = ax2.quiver(
    X_pos, Y_pos, FX_norm, FY_norm, INT_arr,
    cmap='plasma', angles='xy', scale=40, width=0.003, headwidth=4, headlength=5
)
plt.colorbar(sc, ax=ax2, label='|∇T| (K/m)')
ax2.set_xlim(0, x[j_mur_int])
ax2.set_ylim(y[0], y[-1])
ax2.set_title('Flux thermique (direction normalisée)', fontsize=13, fontweight='bold')
ax2.set_xlabel('Épaisseur (m)')
ax2.set_ylabel('Hauteur (m)')
ax2.set_aspect('auto')

def format_coord_flux(xc, yc):
    j = np.argmin(np.abs(x - xc))
    i = np.argmin(np.abs(y - yc))
    if 0 <= i < n and 0 <= j < m:
        return f'x={xc:.3f} m  y={yc:.3f} m  →  |∇T| = {intensite[i,j]:.1f} K/m  |  q = {intensite_reel[i,j]:.1f} W/m²'
    return f'x={xc:.3f} m  y={yc:.3f} m'
ax2.format_coord = format_coord_flux

overlay_geometrie(ax1)
overlay_geometrie(ax2)
plt.tight_layout()
plt.show()

# ============================================================
# Figure 2 : Flux réel proportionnel (W/m²)
# ============================================================
fig2, ax3 = plt.subplots(figsize=(9, 7))

FX_reel_arr  = flux_x_reel[II, JJ]
FY_reel_arr  = flux_y_reel[II, JJ]
INT_reel_arr = intensite_reel[II, JJ]

norme_reel = np.sqrt(FX_reel_arr**2 + FY_reel_arr**2)
norme_reel[norme_reel == 0] = 1

INT_reel_norm = INT_reel_arr / np.percentile(INT_reel_arr[INT_reel_arr > 0], 95)
INT_reel_norm = np.clip(INT_reel_norm, 0.0, 1.0)

FX_plot = (FX_reel_arr / norme_reel) * INT_reel_norm
FY_plot = (FY_reel_arr / norme_reel) * INT_reel_norm

sc2 = ax3.quiver(
    X_pos, Y_pos, FX_plot, FY_plot, INT_reel_arr,
    cmap='plasma', angles='xy', scale=25, width=0.003, headwidth=4, headlength=5
)
plt.colorbar(sc2, ax=ax3, label='Flux thermique (W/m²)')
ax3.set_xlim(0, x[j_mur_int])
ax3.set_ylim(y[0], y[-1])
ax3.set_title('Flux thermique réel (longueur proportionnelle)', fontsize=13, fontweight='bold')
ax3.set_xlabel('Épaisseur (m)')
ax3.set_ylabel('Hauteur (m)')
ax3.set_aspect('auto')

def format_coord_flux2(xc, yc):
    j = np.argmin(np.abs(x - xc))
    i = np.argmin(np.abs(y - yc))
    if 0 <= i < n and 0 <= j < m:
        return f'x={xc:.3f} m  y={yc:.3f} m  →  q = {intensite_reel[i,j]:.2f} W/m²  qx={flux_x_reel[i,j]:.2f}  qy={flux_y_reel[i,j]:.2f}'
    return f'x={xc:.3f} m  y={yc:.3f} m'
ax3.format_coord = format_coord_flux2

overlay_geometrie(ax3)
plt.tight_layout()
plt.show()

print(f"Maillage = {n*m}")

#Plot de vérif géométrique
SHOW_GRAPH_GEOMETRY = False
if SHOW_GRAPH_GEOMETRY :

    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(8, 10))

    # Dimensions totales
    x_tot = eM + eI + eS_m + eB
    y_tot = hM

    # Couches principales
    ax.add_patch(patches.Rectangle((0, 0), eM, hM, facecolor='lightgray', edgecolor='black', label='Mur extérieur'))
    ax.add_patch(patches.Rectangle((eM, 0), eI, hM, facecolor='beige', edgecolor='black', label='Isolant'))
    ax.add_patch(patches.Rectangle((eM + eI, 0), eS_m, hM, facecolor='mistyrose', edgecolor='black', label='Enduit'))
    ax.add_patch(patches.Rectangle((eM + eI + eS_m, 0), eB, hM, facecolor='whitesmoke', edgecolor='black', label='Mur intérieur'))

    # Cavités d'air
    for k in range(int(hM / hB_m)):
        y_bas = k * hB_m + k_m
        hauteur_air = hB_m - 2 * k_m
        if y_bas + hauteur_air <= hM:
            ax.add_patch(
                patches.Rectangle(
                    (eM + eI + eS_m + k_m, y_bas),
                    eB - 2 * k_m,
                    hauteur_air,
                    facecolor='skyblue',
                    edgecolor='black'
                )
            )

    # Sources de chaleur dans l’enduit
    x_source = eM + eI + eS_m / 2
    for k in range(1, int(round(hM / pasSources_m))):
        y_source = k * pasSources_m
        if y_source < hM:
            ax.plot(x_source, y_source, 'ro', markersize=6)

    # Conditions limites
    ax.text(-0.03, hM/2, f"Te = {TempE-273.15:.0f}°C\nhe = {hE}", ha='right', va='center', fontsize=10)
    ax.text(x_tot + 0.02, hM/2, f"Ti = {TempI-273.15:.0f}°C\nhi = {hI}", ha='left', va='center', fontsize=10)

    # Interfaces verticales
    for xpos in [0, eM, eM + eI, eM + eI + eS_m, x_tot]:
        ax.axvline(x=xpos, color='k', linewidth=0.8)

    # Mise en forme
    ax.set_xlim(-0.05, x_tot + 0.08)
    ax.set_ylim(0, hM)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Vérification visuelle de la géométrie et des conditions du projet")
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.show()


    from matplotlib.colors import ListedColormap

    zone = np.zeros((n, m), dtype=int)

    jsource_debut = np.searchsorted(x, float(eM + eI))
    jsource_fin   = np.searchsorted(x, float(eM + eI + eS_m))

    for i in range(n):
        dans_cavite = is_cavite[i]
        idx_alv = idx_alv_par_ligne[i] if dans_cavite else None

        for j in range(m):

            # Sources
            if i in indices_sources_y and jsource_debut <= j < jsource_fin:
                zone[i, j] = 5

            # Cavité d'air
            elif dans_cavite and j_air_gauche <= j <= j_air_droite:
                zone[i, j] = 7

            # Mur extérieur
            elif j < j_mur_ext:
                zone[i, j] = 0

            # Interface mur ext / isolant
            elif j == j_mur_ext:
                zone[i, j] = 1

            # Isolant
            elif j < j_isolant:
                zone[i, j] = 2

            # Interface isolant / enduit
            elif j == j_isolant:
                zone[i, j] = 3

            # Enduit
            elif j < j_enduit:
                zone[i, j] = 4

            # Interface enduit / mur intérieur
            elif j == j_enduit:
                zone[i, j] = 8

            # Mur intérieur plein
            elif j < j_mur_int:
                zone[i, j] = 6

            # Bord intérieur
            elif j == j_mur_int:
                zone[i, j] = 11

    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch

    # Reprend tes paramètres déjà définis :
    # eM, eI, eS_m, eB, hM, hB_m, k_m, pasSources_m, dx, dy

    x = np.round(np.arange(0, eM + eI + eS_m + eB + dx, dx), 10)
    y = np.round(np.arange(0, hM + dy, dy), 10)
    m = len(x)
    n = len(y)

    j_mur_ext    = np.searchsorted(x, eM)
    j_isolant    = np.searchsorted(x, eM + eI)
    j_source     = np.searchsorted(x, eM + eI + eS_m / 2)
    j_enduit     = np.searchsorted(x, eM + eI + eS_m)
    j_air_gauche = np.searchsorted(x, eM + eI + eS_m + k_m)
    j_air_droite = np.searchsorted(x, eM + eI + eS_m + eB - k_m)
    j_mur_int    = np.searchsorted(x, eM + eI + eS_m + eB)

    def to_idx_y(val):
        return int(round(val / dy))

    indices_sources_y = [
        min(to_idx_y(k * pasSources_m), n - 1)
        for k in range(1, int(round(hM / pasSources_m)))
    ]

    indices_alv_bas = [
        min(to_idx_y(k * hB_m + k_m), n - 1)
        for k in range(int(hM / hB_m))
    ]

    indices_alv_haut = [
        min(to_idx_y(k * hB_m + hB_m - k_m), n - 1)
        for k in range(int(hM / hB_m))
    ]

    is_cavite = np.zeros(n, dtype=bool)
    for b, h in zip(indices_alv_bas, indices_alv_haut):
        is_cavite[b:h+1] = True

    # Codes :
    # 0 mur ext
    # 1 interface M/I
    # 2 isolant
    # 3 interface I/E
    # 4 enduit
    # 5 source
    # 6 mur intérieur
    # 7 air
    # 8 interface E/B
    # 9 bord haut
    # 10 bord bas
    # 11 bord gauche
    # 12 bord droit

    zone = np.zeros((n, m), dtype=int)

    for i in range(n):
        dans_cavite = is_cavite[i]

        for j in range(m):
            if j < j_mur_ext:
                z = 0
            elif j == j_mur_ext:
                z = 1
            elif j < j_isolant:
                z = 2
            elif j == j_isolant:
                z = 3
            elif j < j_enduit:
                z = 4
            elif j == j_enduit:
                z = 8
            elif j < j_mur_int:
                if dans_cavite and j_air_gauche <= j <= j_air_droite:
                    z = 7
                else:
                    z = 6
            else:
                z = 12

            # Source : priorité visuelle
            if (i in indices_sources_y) and (j == j_source):
                z = 5

            zone[i, j] = z

    # Bords
    zone[0, :-1] = 9
    zone[-1, :-1] = 10
    zone[:, 0] = 11
    zone[:, -1] = 12

    cmap = ListedColormap([
        '#bfbfbf',  # 0 mur ext
        '#555555',  # 1 int M/I
        '#ecea99',  # 2 isolant
        '#dba61c',  # 3 int I/E
        '#efd8d2',  # 4 enduit
        '#ff2d2d',  # 5 source
        '#efefef',  # 6 mur int
        '#8ecae6',  # 7 air
        '#8a0f8f',  # 8 int E/B
        '#2ca02c',  # 9 bord haut
        '#1b8f1b',  # 10 bord bas
        '#2b6cff',  # 11 bord gauche
        '#2b6cff',  # 12 bord droit
    ])

    plt.figure(figsize=(8, 10))
    plt.imshow(zone, origin='lower', aspect='auto', cmap=cmap, vmin=0, vmax=12, interpolation='nearest')
    plt.xlabel("j")
    plt.ylabel("i")
    plt.title("Carte logique reconstruite depuis les conditions Python")

    legend_elements = [
        Patch(facecolor='#bfbfbf', label='Mur extérieur'),
        Patch(facecolor='#555555', label='Interface M/I'),
        Patch(facecolor='#ecea99', label='Isolant'),
        Patch(facecolor='#dba61c', label='Interface I/E'),
        Patch(facecolor='#efd8d2', label='Enduit'),
        Patch(facecolor='#ff2d2d', label='Source'),
        Patch(facecolor='#efefef', label='Mur intérieur'),
        Patch(facecolor='#8ecae6', label='Air'),
        Patch(facecolor='#8a0f8f', label='Interface E/B'),
    ]
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0.)
    plt.tight_layout()
    plt.show()

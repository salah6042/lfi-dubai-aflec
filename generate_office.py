#!/usr/bin/env python3
"""
Génère un fichier office.tmj agrandi pour WorkAdventure.
Carte étendue à 50x40 avec :
  - 5 salles de classe
  - 1 salle des profs
  - 1 belle cour de récréation centrale
  - Couloirs connectant toutes les zones
  - Zones Jitsi pour chaque salle
"""

import json
import copy

# ── Dimensions ──────────────────────────────────────────────────────────────
W = 50  # largeur en tuiles
H = 40  # hauteur en tuiles

# ── Tile IDs issus des vrais tilesets WorkAdventure ─────────────────────────
# WA_Room_Builder (firstgid=375, 25 colonnes)
FLOOR_WOOD   = 725   # parquet intérieur
FLOOR_CARPET = 735   # moquette / tapis
FLOOR_DARK   = 2461  # sol extérieur sombre

# Murs (WA_Room_Builder)
WALL_TOP_L   = 403   # coin haut-gauche
WALL_TOP     = 479   # mur haut
WALL_TOP_R   = 404   # coin haut-droite
WALL_LEFT    = 477   # mur gauche
WALL_RIGHT   = 477   # mur droite (même tile)
WALL_BOT_L   = 433   # coin bas-gauche
WALL_BOT     = 685   # mur bas / ombre
WALL_BOT_R   = 429   # coin bas-droite

# Murs intérieurs / portes
WALL_VERT    = 477   # cloison verticale
WALL_HORIZ   = 479   # cloison horizontale
DOOR_TOP     = 431   # porte haut
DOOR_MID     = 655   # porte milieu
DOOR_BOT     = 680   # porte bas
WALL_T_DOWN  = 535   # T vers le bas
WALL_T_RIGHT = 406   # T vers la droite
WALL_T_LEFT  = 438   # T vers la gauche
WALL_CROSS   = 485   # croisement
WALL_TOP_R2  = 440   # coin spécial

# Sol extérieur / cour (WA_Exterior, firstgid=1833)
GRASS        = 0     # herbe = tile vide (transparent)
PAVE_1       = 2461  # pavé extérieur
PAVE_2       = 2461

# Meubles / Tables (WA_Tables, firstgid=1557)
TABLE_TL     = 1567  # table coin haut-gauche
TABLE_TR     = 1568  # coin haut-droite
TABLE_T      = 1570  # table haut milieu
TABLE_BL     = 1577  # coin bas-gauche
TABLE_BR     = 1578  # coin bas-droite
TABLE_B      = 1580  # table bas milieu
DESK_L       = 1569  # bureau gauche
DESK_R       = 1569  # bureau droite

# Meubles / Chaises (WA_Seats, firstgid=1375)
CHAIR_UP     = 1494  # chaise face haut
CHAIR_DOWN   = 1495  # chaise face bas
CHAIR_SIDE   = 1509  # chaise côté

# Plantes (WA_Decoration, firstgid=13)
PLANT_SM     = 90    # petite plante
PLANT_SM2    = 102   # petite plante 2
PLANT_BIG    = 187   # grande plante

# Panneaux (WA_Miscellaneous)
BOARD_TL     = 142   # tableau haut-gauche
BOARD_TM     = 143   # tableau haut-milieu
BOARD_TR     = 144   # tableau haut-droite
BOARD_ML     = 152   # tableau milieu-gauche
BOARD_MM     = 153   # tableau milieu-milieu
BOARD_MR     = 154   # tableau milieu-droite
BOARD_BL     = 162   # tableau bas-gauche
BOARD_BM     = 163   # tableau bas-milieu
BOARD_BR     = 164   # tableau bas-droite

# Collisions
COLLIDE      = 3     # tile de collision (WA_Special_Zones tile id=2 → gid=3)

# ── Fonctions utilitaires ───────────────────────────────────────────────────

def make_layer(w, h, fill=0):
    """Crée une grille 2D w×h remplie de fill."""
    return [[fill] * w for _ in range(h)]


def flatten(grid):
    """Aplatit une grille 2D en liste 1D."""
    return [t for row in grid for t in row]


def fill_rect(grid, x1, y1, x2, y2, tile):
    """Remplit un rectangle (inclus) avec un tile ID."""
    for y in range(y1, min(y2 + 1, len(grid))):
        for x in range(x1, min(x2 + 1, len(grid[0]))):
            grid[y][x] = tile


def draw_room_walls(walls, x1, y1, x2, y2, door_side="bottom", door_pos=None):
    """
    Dessine les murs d'une pièce sur le layer walls.
    door_side: 'bottom', 'top', 'left', 'right'
    door_pos: position x ou y de la porte (auto-centré si None)
    """
    # Coins
    walls[y1][x1] = WALL_TOP_L
    walls[y1][x2] = WALL_TOP_R
    walls[y2][x1] = WALL_BOT_L
    walls[y2][x2] = WALL_BOT_R

    # Haut
    for x in range(x1 + 1, x2):
        walls[y1][x] = WALL_HORIZ

    # Bas
    for x in range(x1 + 1, x2):
        walls[y2][x] = WALL_HORIZ

    # Gauche / Droite
    for y in range(y1 + 1, y2):
        walls[y][x1] = WALL_LEFT
        walls[y][x2] = WALL_RIGHT

    # Porte
    if door_side == "bottom":
        dp = door_pos if door_pos else (x1 + x2) // 2
        walls[y2][dp] = 0  # ouverture
    elif door_side == "top":
        dp = door_pos if door_pos else (x1 + x2) // 2
        walls[y1][dp] = 0
    elif door_side == "left":
        dp = door_pos if door_pos else (y1 + y2) // 2
        walls[dp][x1] = 0
    elif door_side == "right":
        dp = door_pos if door_pos else (y1 + y2) // 2
        walls[dp][x2] = 0


def add_classroom_furniture(furn, x1, y1, x2, y2, board_wall="top"):
    """
    Ajoute du mobilier de classe : tableau + rangées de bureaux + chaises.
    """
    # Tableau au mur du haut
    bx = (x1 + x2) // 2 - 1
    if board_wall == "top":
        by = y1 + 1
        if bx >= x1 + 1 and bx + 2 <= x2:
            furn[by][bx]     = BOARD_TL
            furn[by][bx + 1] = BOARD_TM
            furn[by][bx + 2] = BOARD_TR
            if by + 1 < y2:
                furn[by + 1][bx]     = BOARD_BL
                furn[by + 1][bx + 1] = BOARD_BM
                furn[by + 1][bx + 2] = BOARD_BR

    # Rangées de bureaux (2 rangées)
    room_w = x2 - x1 - 1
    room_h = y2 - y1 - 1
    desk_start_y = y1 + 4  # laisser de l'espace après le tableau

    for row_offset in range(0, min(4, room_h - 4), 2):
        dy = desk_start_y + row_offset
        if dy >= y2:
            break
        # Bureaux par paires
        for dx in range(x1 + 2, x2 - 1, 3):
            if dx + 1 < x2:
                furn[dy][dx] = DESK_L
                furn[dy][dx + 1] = DESK_R


def add_teacher_room_furniture(furn, x1, y1, x2, y2):
    """Ajoute du mobilier pour la salle des profs."""
    # Grande table de réunion au centre
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    # Table 4x2
    for dx in range(-2, 2):
        furn[cy - 1][cx + dx] = TABLE_T
        furn[cy][cx + dx] = TABLE_B

    # Chaises autour
    for dx in range(-2, 2):
        if cy - 2 >= y1 + 1:
            furn[cy - 2][cx + dx] = CHAIR_UP
        if cy + 1 <= y2 - 1:
            furn[cy + 1][cx + dx] = CHAIR_DOWN

    # Plantes dans les coins
    furn[y1 + 1][x1 + 1] = PLANT_BIG
    furn[y1 + 1][x2 - 1] = PLANT_BIG
    furn[y2 - 1][x1 + 1] = PLANT_SM
    furn[y2 - 1][x2 - 1] = PLANT_SM


def add_courtyard_decorations(furn, x1, y1, x2, y2):
    """Ajoute des décorations dans la cour de récréation."""
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    # Grand arbre central
    furn[cy - 1][cx - 1] = PLANT_BIG
    furn[cy - 1][cx]     = PLANT_BIG
    furn[cy - 1][cx + 1] = PLANT_BIG
    furn[cy][cx - 1]     = PLANT_BIG
    furn[cy][cx]         = PLANT_BIG
    furn[cy][cx + 1]     = PLANT_BIG

    # Petites plantes autour
    for x in range(x1 + 1, x2, 4):
        furn[y1 + 1][x] = PLANT_SM
        furn[y2 - 1][x] = PLANT_SM
    for y in range(y1 + 1, y2, 4):
        furn[y][x1 + 1] = PLANT_SM2
        furn[y][x2 - 1] = PLANT_SM2

    # Bancs (tables simples)
    furn[cy - 3][cx - 3] = TABLE_TL
    furn[cy - 3][cx - 2] = TABLE_TR
    furn[cy - 3][cx + 2] = TABLE_TL
    furn[cy - 3][cx + 3] = TABLE_TR

    furn[cy + 3][cx - 3] = TABLE_BL
    furn[cy + 3][cx - 2] = TABLE_BR
    furn[cy + 3][cx + 2] = TABLE_BL
    furn[cy + 3][cx + 3] = TABLE_BR


# ── Construction de la carte ────────────────────────────────────────────────

def build_map():
    # Layers
    start_layer     = make_layer(W, H, 0)
    collision_layer = make_layer(W, H, 0)
    floor1          = make_layer(W, H, 0)
    floor2          = make_layer(W, H, 0)
    walls1          = make_layer(W, H, 0)
    walls2          = make_layer(W, H, 0)
    furniture1      = make_layer(W, H, 0)
    furniture2      = make_layer(W, H, 0)
    furniture3      = make_layer(W, H, 0)
    above1          = make_layer(W, H, 0)
    above2          = make_layer(W, H, 0)

    # ── Point de départ (spawn) ─────────────────────────────────────────
    start_layer[2][25] = 2  # start tile au milieu en haut

    # ══════════════════════════════════════════════════════════════════════
    # FLOOR : Sol intérieur partout sauf la cour
    # ══════════════════════════════════════════════════════════════════════

    # Sol global intérieur (bâtiment)
    fill_rect(floor1, 0, 0, W - 1, H - 1, FLOOR_WOOD)

    # ══════════════════════════════════════════════════════════════════════
    # COUR DE RÉCRÉATION (centre de la carte)
    # ══════════════════════════════════════════════════════════════════════
    COUR_X1, COUR_Y1 = 15, 12
    COUR_X2, COUR_Y2 = 34, 27

    # Sol extérieur pour la cour
    fill_rect(floor1, COUR_X1, COUR_Y1, COUR_X2, COUR_Y2, PAVE_1)

    # Moquette spéciale au pourtour de la cour
    fill_rect(floor2, COUR_X1 + 1, COUR_Y1 + 1, COUR_X2 - 1, COUR_Y2 - 1, 0)

    # Décorations de la cour
    add_courtyard_decorations(furniture1, COUR_X1, COUR_Y1, COUR_X2, COUR_Y2)

    # ══════════════════════════════════════════════════════════════════════
    # MURS EXTÉRIEURS du bâtiment complet
    # ══════════════════════════════════════════════════════════════════════

    # Mur extérieur du bâtiment principal (le contour complet)
    # Haut
    for x in range(W):
        walls1[0][x] = WALL_HORIZ
        collision_layer[0][x] = COLLIDE
    # Bas
    for x in range(W):
        walls1[H - 1][x] = WALL_HORIZ
        collision_layer[H - 1][x] = COLLIDE
    # Gauche
    for y in range(H):
        walls1[y][0] = WALL_LEFT
        collision_layer[y][0] = COLLIDE
    # Droite
    for y in range(H):
        walls1[y][W - 1] = WALL_RIGHT
        collision_layer[y][W - 1] = COLLIDE

    # Coins
    walls1[0][0] = WALL_TOP_L
    walls1[0][W - 1] = WALL_TOP_R
    walls1[H - 1][0] = WALL_BOT_L
    walls1[H - 1][W - 1] = WALL_BOT_R

    # Entrée principale (bas, centre)
    entrance_x = W // 2
    walls1[H - 1][entrance_x - 1] = 0
    walls1[H - 1][entrance_x] = 0
    walls1[H - 1][entrance_x + 1] = 0
    collision_layer[H - 1][entrance_x - 1] = 0
    collision_layer[H - 1][entrance_x] = 0
    collision_layer[H - 1][entrance_x + 1] = 0

    # ══════════════════════════════════════════════════════════════════════
    # 5 SALLES DE CLASSE
    # ══════════════════════════════════════════════════════════════════════

    classrooms = [
        # (x1, y1, x2, y2, door_side, door_pos, name)
        (1,  1,  13, 10, "bottom", 7,   "Salle 101"),   # Classe 1 - Haut gauche
        (1,  12, 13, 21, "right",  17,  "Salle 102"),   # Classe 2 - Milieu gauche
        (1,  23, 13, 32, "right",  28,  "Salle 103"),   # Classe 3 - Bas gauche
        (36, 1,  48, 10, "bottom", 42,  "Salle 201"),   # Classe 4 - Haut droite
        (36, 12, 48, 21, "left",   17,  "Salle 202"),   # Classe 5 - Milieu droite
    ]

    for (x1, y1, x2, y2, ds, dp, name) in classrooms:
        # Sol moquette dans la salle
        fill_rect(floor1, x1, y1, x2, y2, FLOOR_WOOD)
        fill_rect(floor2, x1 + 1, y1 + 1, x2 - 1, y2 - 1, FLOOR_CARPET)

        # Murs
        draw_room_walls(walls1, x1, y1, x2, y2, door_side=ds, door_pos=dp)

        # Collisions sur les murs
        for x in range(x1, x2 + 1):
            collision_layer[y1][x] = COLLIDE
            collision_layer[y2][x] = COLLIDE
        for y in range(y1, y2 + 1):
            collision_layer[y][x1] = COLLIDE
            collision_layer[y][x2] = COLLIDE

        # Retirer la collision à la porte
        if ds == "bottom":
            collision_layer[y2][dp] = 0
        elif ds == "top":
            collision_layer[y1][dp] = 0
        elif ds == "left":
            collision_layer[dp][x1] = 0
        elif ds == "right":
            collision_layer[dp][x2] = 0

        # Mobilier de classe
        add_classroom_furniture(furniture2, x1, y1, x2, y2)

    # ══════════════════════════════════════════════════════════════════════
    # SALLE DES PROFS (bas droite)
    # ══════════════════════════════════════════════════════════════════════
    TP_X1, TP_Y1 = 36, 23
    TP_X2, TP_Y2 = 48, 32

    fill_rect(floor1, TP_X1, TP_Y1, TP_X2, TP_Y2, FLOOR_WOOD)
    fill_rect(floor2, TP_X1 + 1, TP_Y1 + 1, TP_X2 - 1, TP_Y2 - 1, FLOOR_CARPET)

    draw_room_walls(walls1, TP_X1, TP_Y1, TP_X2, TP_Y2, door_side="left", door_pos=28)

    for x in range(TP_X1, TP_X2 + 1):
        collision_layer[TP_Y1][x] = COLLIDE
        collision_layer[TP_Y2][x] = COLLIDE
    for y in range(TP_Y1, TP_Y2 + 1):
        collision_layer[y][TP_X1] = COLLIDE
        collision_layer[y][TP_X2] = COLLIDE
    collision_layer[28][TP_X1] = 0  # porte

    add_teacher_room_furniture(furniture2, TP_X1, TP_Y1, TP_X2, TP_Y2)

    # ══════════════════════════════════════════════════════════════════════
    # COULOIRS (sol à nu / parquet)
    # ══════════════════════════════════════════════════════════════════════

    # Couloir horizontal haut (entre classes gauche et droite)
    fill_rect(floor1, 14, 1, 35, 10, FLOOR_WOOD)

    # Couloir vertical gauche (entre les 3 classes gauche)
    fill_rect(floor1, 14, 1, 14, 38, FLOOR_WOOD)

    # Couloir vertical droite (entre les classes droite et salle profs)
    fill_rect(floor1, 35, 1, 35, 38, FLOOR_WOOD)

    # Couloir horizontal bas
    fill_rect(floor1, 1, 33, 48, 38, FLOOR_WOOD)

    # ══════════════════════════════════════════════════════════════════════
    # MURS DE LA COUR (contour intérieur)
    # ══════════════════════════════════════════════════════════════════════
    # Les murs de la cour
    draw_room_walls(walls2, COUR_X1, COUR_Y1, COUR_X2, COUR_Y2,
                    door_side="bottom", door_pos=25)

    # Porte d'accès haut de la cour
    walls2[COUR_Y1][25] = 0

    # Collision autour de la cour
    for x in range(COUR_X1, COUR_X2 + 1):
        collision_layer[COUR_Y1][x] = COLLIDE
        collision_layer[COUR_Y2][x] = COLLIDE
    for y in range(COUR_Y1, COUR_Y2 + 1):
        collision_layer[y][COUR_X1] = COLLIDE
        collision_layer[y][COUR_X2] = COLLIDE

    # Portes de la cour (pas de collision)
    collision_layer[COUR_Y2][25] = 0  # porte bas
    collision_layer[COUR_Y1][25] = 0  # porte haut

    # ══════════════════════════════════════════════════════════════════════
    # PLANTES DÉCORATIVES (couloirs)
    # ══════════════════════════════════════════════════════════════════════
    # Plantes le long du couloir horizontal haut
    for x in range(16, 34, 4):
        above1[2][x] = PLANT_SM

    # Plantes dans le couloir bas
    for x in range(3, 48, 5):
        above1[34][x] = PLANT_SM

    # Plantes dans le couloir vertical gauche
    for y in range(3, 32, 5):
        above1[y][14] = PLANT_SM2

    # Plantes dans le couloir vertical droite
    for y in range(3, 32, 5):
        above1[y][35] = PLANT_SM2

    # ══════════════════════════════════════════════════════════════════════
    # ZONES JITSI (WorkAdventure object layer)
    # ══════════════════════════════════════════════════════════════════════

    objects = []
    obj_id = 10

    # Zone de départ
    obj_id += 1
    objects.append({
        "height": 32,
        "id": obj_id,
        "name": "start",
        "properties": [{"name": "start", "type": "bool", "value": True}],
        "rotation": 0,
        "type": "area",
        "visible": True,
        "width": 64,
        "x": 24 * 32,
        "y": 2 * 32
    })

    # Jitsi pour chaque salle de classe
    for i, (x1, y1, x2, y2, _, _, name) in enumerate(classrooms):
        obj_id += 1
        objects.append({
            "height": (y2 - y1 - 1) * 32,
            "id": obj_id,
            "name": f"jitsi{name.replace(' ', '')}",
            "properties": [
                {"name": "focusable", "type": "bool", "value": True},
                {"name": "jitsiRoom", "type": "string", "value": name.replace(" ", "")},
                {"name": "jitsiTrigger", "type": "string", "value": "onaction"},
                {"name": "zoom_margin", "type": "float", "value": 1}
            ],
            "rotation": 0,
            "type": "area",
            "visible": True,
            "width": (x2 - x1 - 1) * 32,
            "x": (x1 + 1) * 32,
            "y": (y1 + 1) * 32
        })

    # Jitsi pour la salle des profs
    obj_id += 1
    objects.append({
        "height": (TP_Y2 - TP_Y1 - 1) * 32,
        "id": obj_id,
        "name": "jitsiSalleDesProfs",
        "properties": [
            {"name": "focusable", "type": "bool", "value": True},
            {"name": "jitsiRoom", "type": "string", "value": "SalleDesProfs"},
            {"name": "jitsiTrigger", "type": "string", "value": "onaction"},
            {"name": "zoom_margin", "type": "float", "value": 1}
        ],
        "rotation": 0,
        "type": "area",
        "visible": True,
        "width": (TP_X2 - TP_X1 - 1) * 32,
        "x": (TP_X1 + 1) * 32,
        "y": (TP_Y1 + 1) * 32
    })

    # Sortie vers conference
    obj_id += 1
    objects.append({
        "height": 64,
        "id": obj_id,
        "name": "to-conference",
        "properties": [
            {"name": "exitUrl", "type": "string", "value": "conference.tmj#from-office"}
        ],
        "rotation": 0,
        "type": "area",
        "visible": True,
        "width": 96,
        "x": (entrance_x - 1) * 32,
        "y": (H - 1) * 32
    })

    # Entrée depuis conference
    obj_id += 1
    objects.append({
        "height": 32,
        "id": obj_id,
        "name": "from-conference",
        "properties": [
            {"name": "start", "type": "bool", "value": True}
        ],
        "rotation": 0,
        "type": "area",
        "visible": True,
        "width": 32,
        "x": entrance_x * 32,
        "y": (H - 2) * 32
    })

    # ══════════════════════════════════════════════════════════════════════
    # ASSEMBLAGE du fichier Tiled
    # ══════════════════════════════════════════════════════════════════════

    def tile_layer(name, lid, data):
        return {
            "data": flatten(data),
            "height": H,
            "id": lid,
            "name": name,
            "opacity": 1,
            "type": "tilelayer",
            "visible": True,
            "width": W,
            "x": 0,
            "y": 0
        }

    tiled_map = {
        "compressionlevel": -1,
        "height": H,
        "infinite": False,
        "layers": [
            tile_layer("start", 6, start_layer),
            tile_layer("collisions", 7, collision_layer),
            {
                "id": 55,
                "layers": [
                    tile_layer("floor1", 4, floor1),
                    tile_layer("floor2", 57, floor2),
                ],
                "name": "floor",
                "opacity": 1,
                "type": "group",
                "visible": True,
                "x": 0,
                "y": 0
            },
            {
                "id": 54,
                "layers": [
                    tile_layer("walls1", 9, walls1),
                    tile_layer("walls2", 56, walls2),
                ],
                "name": "walls",
                "opacity": 1,
                "type": "group",
                "visible": True,
                "x": 0,
                "y": 0
            },
            {
                "id": 52,
                "layers": [
                    tile_layer("furniture1", 44, furniture1),
                    tile_layer("furniture2", 1, furniture2),
                    tile_layer("furniture3", 33, furniture3),
                ],
                "name": "furniture",
                "opacity": 1,
                "type": "group",
                "visible": True,
                "x": 0,
                "y": 0
            },
            {
                "draworder": "topdown",
                "id": 2,
                "name": "floorLayer",
                "objects": objects,
                "opacity": 1,
                "type": "objectgroup",
                "visible": True,
                "x": 0,
                "y": 0
            },
            {
                "id": 51,
                "layers": [
                    tile_layer("above1", 3, above1),
                    tile_layer("above2", 27, above2),
                ],
                "name": "above",
                "opacity": 1,
                "type": "group",
                "visible": True,
                "x": 0,
                "y": 0
            }
        ],
        "nextlayerid": 63,
        "nextobjectid": obj_id + 1,
        "orientation": "orthogonal",
        "properties": [
            {
                "name": "mapCopyright",
                "type": "string",
                "value": "Credits: WorkAdventure (https://WorkAdventu.re) \nLicense: CC-BY-SA 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)"
            },
            {
                "name": "mapDescription",
                "type": "string",
                "value": "Campus virtuel du Lycée Français - 5 salles de classe, salle des profs, cour de récréation"
            },
            {
                "name": "mapImage",
                "type": "string",
                "value": "office.png"
            },
            {
                "name": "mapName",
                "type": "string",
                "value": "Campus Virtuel"
            },
            {
                "name": "script",
                "type": "string",
                "value": "src/main.ts"
            }
        ],
        "renderorder": "right-down",
        "tiledversion": "1.11.2",
        "tileheight": 32,
        "tilesets": [
            {
                "columns": 6,
                "firstgid": 1,
                "image": "tilesets/WA_Special_Zones.png",
                "imageheight": 64,
                "imagewidth": 192,
                "margin": 0,
                "name": "WA_Special_Zones",
                "spacing": 0,
                "tilecount": 12,
                "tileheight": 32,
                "tiles": [
                    {
                        "id": 2,
                        "properties": [
                            {"name": "collides", "type": "bool", "value": True}
                        ]
                    }
                ],
                "tilewidth": 32
            },
            {
                "columns": 12,
                "firstgid": 13,
                "image": "tilesets/WA_Decoration.png",
                "imageheight": 256,
                "imagewidth": 384,
                "margin": 0,
                "name": "WA_Decoration",
                "spacing": 0,
                "tilecount": 96,
                "tileheight": 32,
                "tilewidth": 32
            },
            {
                "columns": 10,
                "firstgid": 109,
                "image": "tilesets/WA_Miscellaneous.png",
                "imageheight": 352,
                "imagewidth": 320,
                "margin": 0,
                "name": "WA_Miscellaneous",
                "spacing": 0,
                "tilecount": 110,
                "tileheight": 32,
                "tilewidth": 32
            },
            {
                "columns": 12,
                "firstgid": 219,
                "image": "tilesets/WA_Other_Furniture.png",
                "imageheight": 416,
                "imagewidth": 384,
                "margin": 0,
                "name": "WA_Other_Furniture",
                "spacing": 0,
                "tilecount": 156,
                "tileheight": 32,
                "tilewidth": 32
            },
            {
                "columns": 25,
                "firstgid": 375,
                "image": "tilesets/WA_Room_Builder.png",
                "imageheight": 1280,
                "imagewidth": 800,
                "margin": 0,
                "name": "WA_Room_Builder",
                "spacing": 0,
                "tilecount": 1000,
                "tileheight": 32,
                "tilewidth": 32
            },
            {
                "columns": 13,
                "firstgid": 1375,
                "image": "tilesets/WA_Seats.png",
                "imageheight": 448,
                "imagewidth": 416,
                "margin": 0,
                "name": "WA_Seats",
                "spacing": 0,
                "tilecount": 182,
                "tileheight": 32,
                "tilewidth": 32
            },
            {
                "columns": 10,
                "firstgid": 1557,
                "image": "tilesets/WA_Tables.png",
                "imageheight": 864,
                "imagewidth": 320,
                "margin": 0,
                "name": "WA_Tables",
                "spacing": 0,
                "tilecount": 270,
                "tileheight": 32,
                "tilewidth": 32
            },
            {
                "columns": 6,
                "firstgid": 1827,
                "image": "tilesets/WA_Logo_Long.png",
                "imageheight": 32,
                "imagewidth": 192,
                "margin": 0,
                "name": "WA_Logo_Long",
                "spacing": 0,
                "tilecount": 6,
                "tileheight": 32,
                "tilewidth": 32
            },
            {
                "columns": 25,
                "firstgid": 1833,
                "image": "tilesets/WA_Exterior.png",
                "imageheight": 1088,
                "imagewidth": 800,
                "margin": 0,
                "name": "WA_Exterior",
                "spacing": 0,
                "tilecount": 850,
                "tileheight": 32,
                "tilewidth": 32
            },
            {
                "columns": 13,
                "firstgid": 2683,
                "image": "tilesets/WA_User_Interface.png",
                "imageheight": 672,
                "imagewidth": 416,
                "margin": 0,
                "name": "WA_User_Interface",
                "spacing": 0,
                "tilecount": 273,
                "tileheight": 32,
                "tilewidth": 32
            }
        ],
        "tilewidth": 32,
        "type": "map",
        "version": "1.10",
        "width": W
    }

    return tiled_map


def main():
    print("🏫 Génération de la carte campus étendue...")
    tiled_map = build_map()

    output = "office.tmj"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(tiled_map, f, ensure_ascii=False)

    total_tiles = W * H
    print(f"✅ Carte exportée dans « {output} »")
    print(f"   → {W}×{H} tuiles ({W * 32}×{H * 32} px)")
    print(f"   → {total_tiles} tuiles par calque")
    print(f"   → 5 salles de classe + 1 salle des profs + 1 cour de récréation")
    print(f"   → Zones Jitsi configurées pour chaque salle")
    print()
    print("📌 Ouvre ce fichier dans Tiled ou lance WorkAdventure pour voir le résultat !")


if __name__ == "__main__":
    main()

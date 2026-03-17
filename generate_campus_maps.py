#!/usr/bin/env python3
"""
🏫 Générateur de Campus Virtuel — Lycée Français International de Dubaï (AFLEC)
===============================================================================
Génère 9 cartes .tmj interconnectées pour WorkAdventure :
  • cour1.tmj        — Hub principal avec fontaine, palmiers, lettres AFLEC
  • cour2.tmj        — Cour de détente avec zones ombragées et tapis
  • salle-info.tmj   — Salle informatique (disposition en îlots)
  • salle-techno1.tmj — Salle technologie (rangées d'ordinateurs)
  • maths.tmj        — Salle de mathématiques
  • svt.tmj          — Salle de SVT (Sciences de la Vie et de la Terre)
  • francais.tmj     — Salle de français
  • anglais.tmj      — Salle d'anglais
  • arabic.tmj       — Salle d'arabe

Utilise les tilesets WorkAdventure existants dans le dossier tilesets/.
"""

import json
import os

# ══════════════════════════════════════════════════════════════════════════════
# TILE IDs — issus des vrais tilesets WorkAdventure du projet
# ══════════════════════════════════════════════════════════════════════════════

# --- WA_Room_Builder (firstgid=375, 25 colonnes) ---
FLOOR_WOOD     = 725    # parquet intérieur
FLOOR_CARPET   = 735    # moquette
FLOOR_TILE     = 750    # carrelage
FLOOR_DARK     = 700    # sol sombre

# Murs
WALL_TL  = 403   # coin haut-gauche
WALL_T   = 479   # mur horizontal haut
WALL_TR  = 404   # coin haut-droite
WALL_L   = 477   # mur vertical gauche
WALL_R   = 477   # mur vertical droite
WALL_BL  = 433   # coin bas-gauche
WALL_B   = 685   # mur bas / ombre
WALL_BR  = 429   # coin bas-droite

# Murs spéciaux / portes
WALL_T_DOWN  = 535  # T vers le bas
DOOR_TOP     = 431  # porte haut
DOOR_MID     = 655  # porte milieu
DOOR_BOT     = 680  # porte bas

# --- WA_Exterior (firstgid=1833, 25 colonnes) ---
GRASS_1     = 1858   # herbe
GRASS_2     = 1859   # herbe variante
PAVE_1      = 2461   # pavé extérieur
PAVE_2      = 2461
SAND_1      = 1883   # sable (Dubaï!)
PALM_TOP    = 1836   # palmier haut
PALM_BOT    = 1837   # palmier bas
TREE_1      = 1911   # arbre 1
TREE_2      = 1912   # arbre 2
TREE_3      = 1913   # arbre 3
WATER_TL    = 1908   # eau coin haut-gauche
WATER_T     = 1909   # eau haut
WATER_TR    = 1910   # eau coin haut-droite
WATER_ML    = 1933   # eau milieu-gauche
WATER_M     = 1934   # eau milieu
WATER_MR    = 1935   # eau milieu-droite
WATER_BL    = 1958   # eau bas-gauche
WATER_B     = 1959   # eau bas
WATER_BR    = 1960   # eau bas-droite
FLOWER_1    = 1961   # fleur 1
FLOWER_2    = 1962   # fleur 2
FLOWER_3    = 1963   # fleur 3

# --- WA_Decoration (firstgid=13, 12 colonnes) ---
PLANT_SM     = 90    # petite plante
PLANT_SM2    = 102   # petite plante 2
PLANT_BIG    = 187   # grande plante

# --- WA_Miscellaneous (firstgid=109, 10 colonnes) ---
BOARD_TL = 142;  BOARD_TM = 143;  BOARD_TR = 144
BOARD_ML = 152;  BOARD_MM = 153;  BOARD_MR = 154
BOARD_BL = 162;  BOARD_BM = 163;  BOARD_BR = 164

# --- WA_Tables (firstgid=1557, 10 colonnes) ---
TABLE_TL = 1567;  TABLE_T = 1570;  TABLE_TR = 1568
TABLE_BL = 1577;  TABLE_B = 1580;  TABLE_BR = 1578
DESK     = 1569   # bureau simple
DESK2    = 1579   # bureau variante

# PC / écran (tables spéciales)
PC_TL = 1572;  PC_TR = 1574
PC_BL = 1582;  PC_BR = 1584
SCREEN_T = 1562;  SCREEN_B = 1563

# --- WA_Seats (firstgid=1375, 13 colonnes) ---
CHAIR_U  = 1494   # chaise face haut
CHAIR_D  = 1495   # chaise face bas
CHAIR_L  = 1496   # chaise face gauche
CHAIR_R  = 1497   # chaise face droite
SOFA_TL  = 1518;  SOFA_TR = 1519  # canapé haut
SOFA_BL  = 1535;  SOFA_BR = 1522  # canapé bas
BOOKSH_T = 1375;  BOOKSH_M = 1388;  BOOKSH_B = 1401  # étagère

# --- WA_Other_Furniture (firstgid=219, 12 colonnes) ---
LAMP     = 238
LAMP2    = 239
CARPET_TL = 250;  CARPET_TR = 251

# --- WA_User_Interface (firstgid=2683, 13 colonnes) ---
ARROW_D  = 2704   # flèche bas (indication porte)
SIGN     = 2743   # panneau

# Collisions
COLLIDE  = 3   # WA_Special_Zones tile id=2 → gid=3

# ══════════════════════════════════════════════════════════════════════════════
# LETTRES AFLEC en pixel art (5 lignes × variable colonnes chaque)
# ══════════════════════════════════════════════════════════════════════════════

LETTER_PATTERNS = {
    'A': [
        " ## ",
        "#  #",
        "####",
        "#  #",
        "#  #",
    ],
    'F': [
        "####",
        "#   ",
        "### ",
        "#   ",
        "#   ",
    ],
    'L': [
        "#   ",
        "#   ",
        "#   ",
        "#   ",
        "####",
    ],
    'E': [
        "####",
        "#   ",
        "### ",
        "#   ",
        "####",
    ],
    'C': [
        " ###",
        "#   ",
        "#   ",
        "#   ",
        " ###",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def make_grid(w, h, fill=0):
    """Crée une grille 2D w×h."""
    return [[fill] * w for _ in range(h)]


def flatten(grid):
    """Aplatit 2D → 1D."""
    return [t for row in grid for t in row]


def fill_rect(grid, x1, y1, x2, y2, tile):
    """Remplit un rectangle (bornes incluses)."""
    for y in range(max(0, y1), min(len(grid), y2 + 1)):
        for x in range(max(0, x1), min(len(grid[0]), x2 + 1)):
            grid[y][x] = tile


def set_tile(grid, x, y, tile):
    """Place un tile en vérifiant les bornes."""
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        grid[y][x] = tile


def draw_walls(walls, coll, x1, y1, x2, y2, openings=None):
    """
    Dessine les murs d'une pièce + collisions.
    openings: liste de tuples (side, pos) pour les portes.
    """
    if openings is None:
        openings = []

    open_set = set()
    for side, pos in openings:
        open_set.add((side, pos))

    # Coins
    set_tile(walls, x1, y1, WALL_TL)
    set_tile(walls, x2, y1, WALL_TR)
    set_tile(walls, x1, y2, WALL_BL)
    set_tile(walls, x2, y2, WALL_BR)
    set_tile(coll, x1, y1, COLLIDE)
    set_tile(coll, x2, y1, COLLIDE)
    set_tile(coll, x1, y2, COLLIDE)
    set_tile(coll, x2, y2, COLLIDE)

    # Haut
    for x in range(x1 + 1, x2):
        if ('top', x) not in open_set:
            set_tile(walls, x, y1, WALL_T)
            set_tile(coll, x, y1, COLLIDE)
        else:
            set_tile(walls, x, y1, 0)

    # Bas
    for x in range(x1 + 1, x2):
        if ('bottom', x) not in open_set:
            set_tile(walls, x, y2, WALL_T)
            set_tile(coll, x, y2, COLLIDE)
        else:
            set_tile(walls, x, y2, 0)

    # Gauche
    for y in range(y1 + 1, y2):
        if ('left', y) not in open_set:
            set_tile(walls, x1, y, WALL_L)
            set_tile(coll, x1, y, COLLIDE)
        else:
            set_tile(walls, x1, y, 0)

    # Droite
    for y in range(y1 + 1, y2):
        if ('right', y) not in open_set:
            set_tile(walls, x2, y, WALL_R)
            set_tile(coll, x2, y, COLLIDE)
        else:
            set_tile(walls, x2, y, 0)


def draw_text_on_grid(grid, text, start_x, start_y, tile_id):
    """Dessine du texte pixel-art sur la grille avec l'ID donné."""
    cursor_x = start_x
    for ch in text:
        if ch == ' ':
            cursor_x += 2
            continue
        pattern = LETTER_PATTERNS.get(ch.upper())
        if not pattern:
            cursor_x += 3
            continue
        for dy, row in enumerate(pattern):
            for dx, pixel in enumerate(row):
                if pixel == '#':
                    set_tile(grid, cursor_x + dx, start_y + dy, tile_id)
        cursor_x += len(pattern[0]) + 1  # +1 espacement entre lettres


def draw_fountain(floor, furn, coll, cx, cy):
    """Dessine une fontaine 3×3 avec bordure de palmiers."""
    # Eau 3×3
    set_tile(furn, cx - 1, cy - 1, WATER_TL)
    set_tile(furn, cx,     cy - 1, WATER_T)
    set_tile(furn, cx + 1, cy - 1, WATER_TR)
    set_tile(furn, cx - 1, cy,     WATER_ML)
    set_tile(furn, cx,     cy,     WATER_M)
    set_tile(furn, cx + 1, cy,     WATER_MR)
    set_tile(furn, cx - 1, cy + 1, WATER_BL)
    set_tile(furn, cx,     cy + 1, WATER_B)
    set_tile(furn, cx + 1, cy + 1, WATER_BR)

    # Collisions sur la fontaine
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            set_tile(coll, cx + dx, cy + dy, COLLIDE)

    # Palmiers autour (4 coins)
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3)]:
        set_tile(furn, cx + dx, cy + dy - 1, PALM_TOP)
        set_tile(furn, cx + dx, cy + dy,     PALM_BOT)
        set_tile(coll, cx + dx, cy + dy, COLLIDE)

    # Palmiers latéraux
    for dx, dy in [(-3, 0), (3, 0)]:
        set_tile(furn, cx + dx, cy + dy - 1, PALM_TOP)
        set_tile(furn, cx + dx, cy + dy,     PALM_BOT)
        set_tile(coll, cx + dx, cy + dy, COLLIDE)


def draw_palm_row(furn, coll, x1, x2, y, spacing=3):
    """Dessine une rangée de palmiers."""
    for x in range(x1, x2 + 1, spacing):
        set_tile(furn, x, y - 1, PALM_TOP)
        set_tile(furn, x, y,     PALM_BOT)
        set_tile(coll, x, y, COLLIDE)


# ══════════════════════════════════════════════════════════════════════════════
# TILESETS — structure identique à celle du projet existant
# ══════════════════════════════════════════════════════════════════════════════

TILESETS = [
    {
        "columns": 6, "firstgid": 1,
        "image": "tilesets/WA_Special_Zones.png",
        "imageheight": 64, "imagewidth": 192,
        "margin": 0, "name": "WA_Special_Zones", "spacing": 0,
        "tilecount": 12, "tileheight": 32,
        "tiles": [{"id": 2, "properties": [{"name": "collides", "type": "bool", "value": True}]}],
        "tilewidth": 32
    },
    {
        "columns": 12, "firstgid": 13,
        "image": "tilesets/WA_Decoration.png",
        "imageheight": 256, "imagewidth": 384,
        "margin": 0, "name": "WA_Decoration", "spacing": 0,
        "tilecount": 96, "tileheight": 32, "tilewidth": 32
    },
    {
        "columns": 10, "firstgid": 109,
        "image": "tilesets/WA_Miscellaneous.png",
        "imageheight": 352, "imagewidth": 320,
        "margin": 0, "name": "WA_Miscellaneous", "spacing": 0,
        "tilecount": 110, "tileheight": 32, "tilewidth": 32
    },
    {
        "columns": 12, "firstgid": 219,
        "image": "tilesets/WA_Other_Furniture.png",
        "imageheight": 416, "imagewidth": 384,
        "margin": 0, "name": "WA_Other_Furniture", "spacing": 0,
        "tilecount": 156, "tileheight": 32, "tilewidth": 32
    },
    {
        "columns": 25, "firstgid": 375,
        "image": "tilesets/WA_Room_Builder.png",
        "imageheight": 1280, "imagewidth": 800,
        "margin": 0, "name": "WA_Room_Builder", "spacing": 0,
        "tilecount": 1000, "tileheight": 32, "tilewidth": 32
    },
    {
        "columns": 13, "firstgid": 1375,
        "image": "tilesets/WA_Seats.png",
        "imageheight": 448, "imagewidth": 416,
        "margin": 0, "name": "WA_Seats", "spacing": 0,
        "tilecount": 182, "tileheight": 32, "tilewidth": 32
    },
    {
        "columns": 10, "firstgid": 1557,
        "image": "tilesets/WA_Tables.png",
        "imageheight": 864, "imagewidth": 320,
        "margin": 0, "name": "WA_Tables", "spacing": 0,
        "tilecount": 270, "tileheight": 32, "tilewidth": 32
    },
    {
        "columns": 6, "firstgid": 1827,
        "image": "tilesets/WA_Logo_Long.png",
        "imageheight": 32, "imagewidth": 192,
        "margin": 0, "name": "WA_Logo_Long", "spacing": 0,
        "tilecount": 6, "tileheight": 32, "tilewidth": 32
    },
    {
        "columns": 25, "firstgid": 1833,
        "image": "tilesets/WA_Exterior.png",
        "imageheight": 1088, "imagewidth": 800,
        "margin": 0, "name": "WA_Exterior", "spacing": 0,
        "tilecount": 850, "tileheight": 32, "tilewidth": 32
    },
    {
        "columns": 13, "firstgid": 2683,
        "image": "tilesets/WA_User_Interface.png",
        "imageheight": 672, "imagewidth": 416,
        "margin": 0, "name": "WA_User_Interface", "spacing": 0,
        "tilecount": 273, "tileheight": 32, "tilewidth": 32
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# ASSEMBLEUR DE CARTE TILED
# ══════════════════════════════════════════════════════════════════════════════

def build_tile_layer(name, lid, grid, w, h):
    return {
        "data": flatten(grid),
        "height": h, "id": lid, "name": name,
        "opacity": 1, "type": "tilelayer",
        "visible": True, "width": w, "x": 0, "y": 0
    }


def build_object_layer(name, lid, objects=None):
    return {
        "draworder": "topdown",
        "id": lid, "name": name,
        "objects": objects or [],
        "opacity": 1, "type": "objectgroup",
        "visible": True, "x": 0, "y": 0
    }


def make_exit_zone(obj_id, name, x, y, w, h, target_file):
    """Crée une zone de sortie WorkAdventure."""
    return {
        "height": h * 32,
        "id": obj_id,
        "name": name,
        "properties": [
            {"name": "exitUrl", "type": "string", "value": target_file}
        ],
        "rotation": 0,
        "type": "area",
        "visible": True,
        "width": w * 32,
        "x": x * 32,
        "y": y * 32
    }


def make_jitsi_zone(obj_id, name, room_name, x, y, w, h):
    """Crée une zone Jitsi pour la visio."""
    return {
        "height": h * 32,
        "id": obj_id,
        "name": name,
        "properties": [
            {"name": "focusable", "type": "bool", "value": True},
            {"name": "jitsiRoom", "type": "string", "value": room_name},
            {"name": "jitsiTrigger", "type": "string", "value": "onaction"},
            {"name": "zoom_margin", "type": "float", "value": 1}
        ],
        "rotation": 0,
        "type": "area",
        "visible": True,
        "width": w * 32,
        "x": x * 32,
        "y": y * 32
    }


def make_start_zone(obj_id, x, y):
    return {
        "height": 32, "id": obj_id, "name": "start",
        "properties": [{"name": "start", "type": "bool", "value": True}],
        "rotation": 0, "type": "area", "visible": True,
        "width": 32, "x": x * 32, "y": y * 32
    }


def assemble_map(w, h, layers, objects, map_name, map_desc, next_layer_id=20, next_obj_id=50):
    """Assemble la structure finale du fichier .tmj."""
    return {
        "compressionlevel": -1,
        "height": h,
        "infinite": False,
        "layers": layers + [
            build_object_layer("zones-interactives", next_layer_id - 1, objects)
        ],
        "nextlayerid": next_layer_id,
        "nextobjectid": next_obj_id,
        "orientation": "orthogonal",
        "properties": [
            {
                "name": "mapCopyright",
                "type": "string",
                "value": "LFI Dubaï - Réseau AFLEC — Campus Virtuel WorkAdventure"
            },
            {
                "name": "mapDescription",
                "type": "string",
                "value": map_desc
            },
            {
                "name": "mapName",
                "type": "string",
                "value": map_name
            },
        ],
        "renderorder": "right-down",
        "tiledversion": "1.11.2",
        "tileheight": 32,
        "tilesets": TILESETS,
        "tilewidth": 32,
        "type": "map",
        "version": "1.10",
        "width": w
    }


# ══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATEURS DE CARTES
# ══════════════════════════════════════════════════════════════════════════════

def generate_cour1():
    """
    Hub principal du campus (40×40).
    Fontaine centrale, palmiers, lettres AFLEC sur le sol,
    portes vers toutes les salles de classe.
    """
    W, H = 40, 40

    floor   = make_grid(W, H, PAVE_1)       # sol pavé partout
    walls   = make_grid(W, H, 0)
    furn    = make_grid(W, H, 0)
    above   = make_grid(W, H, 0)
    coll    = make_grid(W, H, 0)
    start   = make_grid(W, H, 0)

    # ── Sol : bordure herbe ─────────────────────────────────────────────
    fill_rect(floor, 0, 0, W - 1, 1, GRASS_1)
    fill_rect(floor, 0, H - 2, W - 1, H - 1, GRASS_1)
    fill_rect(floor, 0, 0, 1, H - 1, GRASS_1)
    fill_rect(floor, W - 2, 0, W - 1, H - 1, GRASS_1)

    # Variantes d'herbe pour du naturel
    for x in range(0, W, 3):
        set_tile(floor, x, 0, GRASS_2)
        set_tile(floor, x, H - 1, GRASS_2)

    # ── Murs extérieurs avec ouvertures ─────────────────────────────────
    # Ouvertures: 4 à gauche (salles), 3 à droite (salles), 1 bas (cour2)
    left_doors = [
        ('left', 7), ('left', 8),      # salle-info
        ('left', 14), ('left', 15),     # maths
        ('left', 21), ('left', 22),     # francais
        ('left', 28), ('left', 29),     # arabic
    ]
    right_doors = [
        ('right', 7), ('right', 8),     # salle-techno1
        ('right', 14), ('right', 15),   # svt
        ('right', 21), ('right', 22),   # anglais
    ]
    bottom_doors = [
        ('bottom', 19), ('bottom', 20),  # vers cour2
    ]
    all_openings = left_doors + right_doors + bottom_doors

    draw_walls(walls, coll, 0, 0, W - 1, H - 1, openings=all_openings)

    # ── Fontaine centrale ───────────────────────────────────────────────
    cx, cy = W // 2, H // 2 - 2
    draw_fountain(floor, furn, coll, cx, cy)

    # ── Palmiers décoratifs ─────────────────────────────────────────────
    # Rangées Nord et Sud
    draw_palm_row(furn, coll, 4, W - 5, 3, spacing=4)
    draw_palm_row(furn, coll, 4, W - 5, H - 5, spacing=4)

    # Allées latérales
    for y in range(5, H - 5, 5):
        set_tile(furn, 3, y - 1, PALM_TOP)
        set_tile(furn, 3, y, PALM_BOT)
        set_tile(coll, 3, y, COLLIDE)
        set_tile(furn, W - 4, y - 1, PALM_TOP)
        set_tile(furn, W - 4, y, PALM_BOT)
        set_tile(coll, W - 4, y, COLLIDE)

    # ── Lettres "AFLEC" sur le sol ──────────────────────────────────────
    # Dessiner sur le layer floor avec un tile décoratif
    draw_text_on_grid(floor, "AFLEC", 8, H - 10, FLOOR_CARPET)

    # ── Fleurs décoratives ──────────────────────────────────────────────
    for x in range(6, W - 6, 4):
        set_tile(above, x, cy - 6, FLOWER_1)
        set_tile(above, x + 1, cy - 6, FLOWER_2)
        set_tile(above, x, cy + 6, FLOWER_2)
        set_tile(above, x + 1, cy + 6, FLOWER_3)

    # ── Panneaux indicateurs près des portes ────────────────────────────
    set_tile(above, 2, 6, SIGN)     # Info
    set_tile(above, 2, 13, SIGN)    # Maths
    set_tile(above, 2, 20, SIGN)    # Français
    set_tile(above, 2, 27, SIGN)    # Arabe
    set_tile(above, W - 3, 6, SIGN) # Techno
    set_tile(above, W - 3, 13, SIGN)# SVT
    set_tile(above, W - 3, 20, SIGN)# Anglais

    # ── Flèches d'indication aux portes ─────────────────────────────────
    set_tile(above, 1, 6, ARROW_D)
    set_tile(above, 1, 13, ARROW_D)
    set_tile(above, 1, 20, ARROW_D)
    set_tile(above, 1, 27, ARROW_D)
    set_tile(above, W - 2, 6, ARROW_D)
    set_tile(above, W - 2, 13, ARROW_D)
    set_tile(above, W - 2, 20, ARROW_D)

    # ── Point de départ ─────────────────────────────────────────────────
    start[H - 4][W // 2] = 2  # spawn tile

    # ── Objets WorkAdventure ────────────────────────────────────────────
    objects = []
    oid = 1

    # Start zone
    objects.append(make_start_zone(oid, W // 2, H - 4)); oid += 1

    # Portes vers les salles (exitUrl)
    door_defs = [
        ("exit-info",    0, 7, 1, 2, "salle-info.tmj"),
        ("exit-maths",   0, 14, 1, 2, "maths.tmj"),
        ("exit-francais",0, 21, 1, 2, "francais.tmj"),
        ("exit-arabic",  0, 28, 1, 2, "arabic.tmj"),
        ("exit-techno",  W - 1, 7, 1, 2, "salle-techno1.tmj"),
        ("exit-svt",     W - 1, 14, 1, 2, "svt.tmj"),
        ("exit-anglais", W - 1, 21, 1, 2, "anglais.tmj"),
        ("exit-cour2",   19, H - 1, 2, 1, "cour2.tmj"),
    ]
    for name, x, y, w, h, target in door_defs:
        objects.append(make_exit_zone(oid, name, x, y, w, h, target))
        oid += 1

    # Layers
    layers = [
        build_tile_layer("start", 1, start, W, H),
        build_tile_layer("collisions", 2, coll, W, H),
        build_tile_layer("floor", 3, floor, W, H),
        build_tile_layer("walls", 4, walls, W, H),
        build_tile_layer("furniture", 5, furn, W, H),
        build_tile_layer("above", 6, above, W, H),
    ]

    return assemble_map(W, H, layers, objects,
                        "Cour Principale — LFI Dubaï",
                        "Hub principal du campus avec fontaine, palmiers et lettres AFLEC",
                        next_layer_id=10, next_obj_id=oid)


def generate_cour2():
    """
    Cour de détente (40×40).
    Zones d'ombre, tapis/coussins, design asymétrique, retour vers cour1.
    """
    W, H = 40, 40

    floor = make_grid(W, H, PAVE_1)
    walls = make_grid(W, H, 0)
    furn  = make_grid(W, H, 0)
    above = make_grid(W, H, 0)
    coll  = make_grid(W, H, 0)
    start = make_grid(W, H, 0)

    # Bordure sable (Dubaï!)
    fill_rect(floor, 0, 0, W - 1, 2, SAND_1)
    fill_rect(floor, 0, H - 3, W - 1, H - 1, SAND_1)
    fill_rect(floor, 0, 0, 2, H - 1, SAND_1)
    fill_rect(floor, W - 3, 0, W - 1, H - 1, SAND_1)

    # Murs avec ouverture vers cour1 (haut)
    draw_walls(walls, coll, 0, 0, W - 1, H - 1,
               openings=[('top', 19), ('top', 20)])

    # ── Zone détente 1 : Canapés (coin haut-gauche) ─────────────────────
    fill_rect(floor, 4, 4, 14, 12, FLOOR_CARPET)
    # Canapés en L
    set_tile(furn, 5, 5, SOFA_TL); set_tile(furn, 6, 5, SOFA_TR)
    set_tile(furn, 5, 6, SOFA_BL); set_tile(furn, 6, 6, SOFA_BR)
    set_tile(furn, 8, 5, SOFA_TL); set_tile(furn, 9, 5, SOFA_TR)
    set_tile(furn, 8, 6, SOFA_BL); set_tile(furn, 9, 6, SOFA_BR)
    # Table basse
    set_tile(furn, 6, 8, TABLE_TL); set_tile(furn, 7, 8, TABLE_T); set_tile(furn, 8, 8, TABLE_TR)
    set_tile(furn, 6, 9, TABLE_BL); set_tile(furn, 7, 9, TABLE_B); set_tile(furn, 8, 9, TABLE_BR)
    # Canapés face
    set_tile(furn, 5, 11, SOFA_TL); set_tile(furn, 6, 11, SOFA_TR)
    set_tile(furn, 8, 11, SOFA_TL); set_tile(furn, 9, 11, SOFA_TR)
    # Plantes
    set_tile(above, 4, 4, PLANT_BIG)
    set_tile(above, 14, 4, PLANT_BIG)

    # ── Zone détente 2 : "Cool Zone" tapis (centre-droite) ──────────────
    fill_rect(floor, 22, 14, 36, 26, FLOOR_CARPET)
    # Grands tapis
    for y in range(15, 25, 3):
        set_tile(furn, 24, y, CARPET_TL); set_tile(furn, 25, y, CARPET_TR)
        set_tile(furn, 28, y, CARPET_TL); set_tile(furn, 29, y, CARPET_TR)
        set_tile(furn, 32, y, CARPET_TL); set_tile(furn, 33, y, CARPET_TR)
    # Lampes
    set_tile(above, 22, 14, LAMP); set_tile(above, 36, 14, LAMP2)
    set_tile(above, 22, 26, LAMP); set_tile(above, 36, 26, LAMP2)

    # ── Zone ombre : allée de palmiers ──────────────────────────────────
    for x in range(5, 35, 3):
        set_tile(furn, x, 20 - 1, PALM_TOP)
        set_tile(furn, x, 20, PALM_BOT)
        set_tile(coll, x, 20, COLLIDE)

    # ── Fontaine décorative (coin bas-droite) ───────────────────────────
    draw_fountain(floor, furn, coll, 32, 32)

    # ── Fleurs partout ──────────────────────────────────────────────────
    for x in range(4, W - 4, 5):
        set_tile(above, x, 3, FLOWER_1)
        set_tile(above, x, H - 4, FLOWER_3)
    for y in range(4, H - 4, 5):
        set_tile(above, 3, y, FLOWER_2)
        set_tile(above, W - 4, y, FLOWER_1)

    # ── Étagères / bibliothèque (coin bas-gauche) ───────────────────────
    for x in range(5, 14, 2):
        set_tile(furn, x, 30, BOOKSH_T)
        set_tile(furn, x, 31, BOOKSH_M)
        set_tile(furn, x, 32, BOOKSH_B)
        set_tile(coll, x, 30, COLLIDE)
        set_tile(coll, x, 31, COLLIDE)
        set_tile(coll, x, 32, COLLIDE)

    # Point de départ
    start[3][W // 2] = 2

    # Objets
    objects = []
    oid = 1
    objects.append(make_start_zone(oid, W // 2, 3)); oid += 1
    # Retour cour1
    objects.append(make_exit_zone(oid, "exit-cour1", 19, 0, 2, 1, "cour1.tmj")); oid += 1
    # Jitsi "Cool Zone"
    objects.append(make_jitsi_zone(oid, "jitsiCoolZone", "CoolZone-Detente", 22, 14, 14, 12)); oid += 1

    layers = [
        build_tile_layer("start", 1, start, W, H),
        build_tile_layer("collisions", 2, coll, W, H),
        build_tile_layer("floor", 3, floor, W, H),
        build_tile_layer("walls", 4, walls, W, H),
        build_tile_layer("furniture", 5, furn, W, H),
        build_tile_layer("above", 6, above, W, H),
    ]

    return assemble_map(W, H, layers, objects,
                        "Cour de Détente",
                        "Espace détente avec zones ombragées, tapis et fontaine",
                        next_layer_id=10, next_obj_id=oid)


def generate_classroom(name, display_name, exit_target="cour1.tmj",
                       style="standard", subject_letter=None):
    """
    Génère une salle de classe 20×20.
    Styles: 'standard', 'computer_islands', 'computer_rows', 'science'
    """
    W, H = 20, 20

    floor = make_grid(W, H, FLOOR_WOOD)
    walls = make_grid(W, H, 0)
    furn  = make_grid(W, H, 0)
    above = make_grid(W, H, 0)
    coll  = make_grid(W, H, 0)
    start = make_grid(W, H, 0)

    # Sol : moquette intérieure
    fill_rect(floor, 1, 1, W - 2, H - 2, FLOOR_CARPET)

    # Murs avec porte en bas (2 tuiles)
    draw_walls(walls, coll, 0, 0, W - 1, H - 1,
               openings=[('bottom', W // 2 - 1), ('bottom', W // 2)])

    # ── Tableau au mur du haut ──────────────────────────────────────────
    bx = W // 2 - 1
    set_tile(furn, bx - 1, 1, BOARD_TL)
    set_tile(furn, bx,     1, BOARD_TM)
    set_tile(furn, bx + 1, 1, BOARD_TR)
    set_tile(furn, bx - 1, 2, BOARD_BL)
    set_tile(furn, bx,     2, BOARD_BM)
    set_tile(furn, bx + 1, 2, BOARD_BR)
    # Collision sur le tableau
    for dx in range(-1, 2):
        set_tile(coll, bx + dx, 1, COLLIDE)
        set_tile(coll, bx + dx, 2, COLLIDE)

    # ── Bureau du prof ──────────────────────────────────────────────────
    set_tile(furn, W // 2 - 1, 4, DESK)
    set_tile(furn, W // 2,     4, DESK)
    set_tile(furn, W // 2 - 1, 3, CHAIR_U)
    set_tile(coll, W // 2 - 1, 4, COLLIDE)
    set_tile(coll, W // 2,     4, COLLIDE)

    # ── Mobilier selon le style ─────────────────────────────────────────
    if style == "computer_islands":
        # 4 îlots de 2×2 avec chaises autour
        islands = [(4, 7), (12, 7), (4, 13), (12, 13)]
        for ix, iy in islands:
            # Ilot 2×2
            set_tile(furn, ix, iy, PC_TL); set_tile(furn, ix + 1, iy, PC_TR)
            set_tile(furn, ix, iy + 1, PC_BL); set_tile(furn, ix + 1, iy + 1, PC_BR)
            set_tile(coll, ix, iy, COLLIDE); set_tile(coll, ix + 1, iy, COLLIDE)
            set_tile(coll, ix, iy + 1, COLLIDE); set_tile(coll, ix + 1, iy + 1, COLLIDE)
            # Chaises
            set_tile(furn, ix - 1, iy, CHAIR_R); set_tile(furn, ix + 2, iy, CHAIR_L)
            set_tile(furn, ix - 1, iy + 1, CHAIR_R); set_tile(furn, ix + 2, iy + 1, CHAIR_L)
            set_tile(furn, ix, iy - 1, CHAIR_D); set_tile(furn, ix + 1, iy - 1, CHAIR_D)
            set_tile(furn, ix, iy + 2, CHAIR_U); set_tile(furn, ix + 1, iy + 2, CHAIR_U)

    elif style == "computer_rows":
        # 3 rangées de 6 postes
        for row_y in [7, 11, 15]:
            for x in range(3, 17, 2):
                set_tile(furn, x, row_y, DESK)
                set_tile(furn, x, row_y - 1, SCREEN_T)
                set_tile(coll, x, row_y, COLLIDE)
                set_tile(coll, x, row_y - 1, COLLIDE)
                set_tile(furn, x, row_y + 1, CHAIR_U)

    elif style == "science":
        # Paillasses et rangées de tables labo
        for row_y in [7, 11, 15]:
            for x in range(3, 16, 4):
                set_tile(furn, x, row_y, TABLE_TL); set_tile(furn, x + 1, row_y, TABLE_T)
                set_tile(furn, x + 2, row_y, TABLE_TR)
                set_tile(furn, x, row_y + 1, TABLE_BL); set_tile(furn, x + 1, row_y + 1, TABLE_B)
                set_tile(furn, x + 2, row_y + 1, TABLE_BR)
                set_tile(coll, x, row_y, COLLIDE)
                set_tile(coll, x + 1, row_y, COLLIDE)
                set_tile(coll, x + 2, row_y, COLLIDE)
                # Chaises
                set_tile(furn, x, row_y + 2, CHAIR_U)
                set_tile(furn, x + 2, row_y + 2, CHAIR_U)
        # Plantes déco (SVT!)
        set_tile(above, 1, 1, PLANT_BIG)
        set_tile(above, W - 2, 1, PLANT_BIG)
        set_tile(above, 1, H - 3, PLANT_BIG)
        set_tile(above, W - 2, H - 3, PLANT_BIG)

    else:  # standard
        # Rangées de bureaux classiques (3 rangées × 4 bureaux)
        for row_y in [7, 11, 15]:
            for x in range(3, 16, 3):
                set_tile(furn, x, row_y, DESK); set_tile(furn, x + 1, row_y, DESK)
                set_tile(coll, x, row_y, COLLIDE)
                set_tile(coll, x + 1, row_y, COLLIDE)
                set_tile(furn, x, row_y + 1, CHAIR_U)
                set_tile(furn, x + 1, row_y + 1, CHAIR_U)

    # ── Plantes dans les coins ──────────────────────────────────────────
    if style != "science":
        set_tile(above, 1, 1, PLANT_SM)
        set_tile(above, W - 2, 1, PLANT_SM)

    # ── Étagère sur le mur de droite ────────────────────────────────────
    set_tile(furn, W - 2, 4, BOOKSH_T)
    set_tile(furn, W - 2, 5, BOOKSH_M)
    set_tile(furn, W - 2, 6, BOOKSH_B)
    set_tile(coll, W - 2, 4, COLLIDE)
    set_tile(coll, W - 2, 5, COLLIDE)
    set_tile(coll, W - 2, 6, COLLIDE)

    # ── Lettre de la matière sur le sol (optionnel) ─────────────────────
    if subject_letter and subject_letter in LETTER_PATTERNS:
        draw_text_on_grid(floor, subject_letter, 2, H - 7, FLOOR_DARK)

    # Point de départ (juste après la porte)
    start[H - 3][W // 2] = 2

    # Objets
    objects = []
    oid = 1
    objects.append(make_start_zone(oid, W // 2, H - 3)); oid += 1
    # Retour à la cour
    objects.append(make_exit_zone(oid, f"exit-{name}", W // 2 - 1, H - 1, 2, 1, exit_target)); oid += 1
    # Zone Jitsi couvrant toute la salle (la classe est une salle de visio)
    objects.append(make_jitsi_zone(oid, f"jitsi-{name}", display_name.replace(" ", ""), 2, 2, W - 4, H - 4)); oid += 1

    layers = [
        build_tile_layer("start", 1, start, W, H),
        build_tile_layer("collisions", 2, coll, W, H),
        build_tile_layer("floor", 3, floor, W, H),
        build_tile_layer("walls", 4, walls, W, H),
        build_tile_layer("furniture", 5, furn, W, H),
        build_tile_layer("above", 6, above, W, H),
    ]

    return assemble_map(W, H, layers, objects,
                        display_name,
                        f"Salle de classe : {display_name}",
                        next_layer_id=10, next_obj_id=oid)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN : exécution
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("🏫 Lycée Français International de Dubaï — Réseau AFLEC")
    print("   Génération de 9 cartes WorkAdventure (.tmj)")
    print("=" * 60)
    print()

    maps_to_generate = [
        # (filename, generator_function)
        ("cour1.tmj",         lambda: generate_cour1()),
        ("cour2.tmj",         lambda: generate_cour2()),
        ("salle-info.tmj",    lambda: generate_classroom(
            "salle-info", "Salle Informatique",
            style="computer_islands", subject_letter="A"
        )),
        ("salle-techno1.tmj", lambda: generate_classroom(
            "salle-techno1", "Salle Technologie",
            style="computer_rows", subject_letter="F"
        )),
        ("maths.tmj",         lambda: generate_classroom(
            "maths", "Mathématiques",
            style="standard", subject_letter=None
        )),
        ("svt.tmj",           lambda: generate_classroom(
            "svt", "Sciences de la Vie et de la Terre",
            style="science", subject_letter=None
        )),
        ("francais.tmj",      lambda: generate_classroom(
            "francais", "Français",
            style="standard", subject_letter="F"
        )),
        ("anglais.tmj",       lambda: generate_classroom(
            "anglais", "English",
            style="standard", subject_letter="E"
        )),
        ("arabic.tmj",        lambda: generate_classroom(
            "arabic", "اللغة العربية",
            style="standard", subject_letter="A"
        )),
    ]

    for filename, generator in maps_to_generate:
        data = generator()
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        w, h = data["width"], data["height"]
        n_layers = len(data["layers"])
        n_objects = sum(
            len(l.get("objects", []))
            for l in data["layers"]
            if l["type"] == "objectgroup"
        )
        print(f"  ✅ {filename:25s} → {w}×{h} ({n_layers} calques, {n_objects} objets)")

    print()
    print("=" * 60)
    print("🎉 CAMPUS COMPLET GÉNÉRÉ ! 9 fichiers .tmj créés.")
    print()
    print("📋 Interconnexions configurées :")
    print("   cour1 ←→ salle-info     (gauche)")
    print("   cour1 ←→ maths          (gauche)")
    print("   cour1 ←→ francais       (gauche)")
    print("   cour1 ←→ arabic         (gauche)")
    print("   cour1 ←→ salle-techno1  (droite)")
    print("   cour1 ←→ svt            (droite)")
    print("   cour1 ←→ anglais        (droite)")
    print("   cour1 ←→ cour2          (bas)")
    print()
    print("📌 Pour tester : ouvre cour1.tmj dans Tiled")
    print("   ou déploie sur WorkAdventure pour naviguer entre les cartes !")
    print()
    print("🎨 Personnalisation des avatars :")
    print("   WorkAdventure permet de choisir son WOKA (avatar)")
    print("   lors de la première connexion (nom + apparence).")
    print("   Pour des avatars personnalisés, ajoute des fichiers")
    print("   .png dans un dossier 'woka/' et configure le serveur.")
    print("=" * 60)


if __name__ == "__main__":
    main()

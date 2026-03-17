#!/usr/bin/env python3
"""
Générateur de carte Tiled (.json) pour le Lycée Français International de Dubaï.
Génère un fichier campus_lfi.json compatible avec l'éditeur Tiled et WorkAdventure.

Grille : 60×60 tuiles de 32×32 pixels.

Légende des Tile IDs :
  0 = Vide / Herbe (extérieur)
  1 = Mur extérieur des bâtiments
  2 = Sol intérieur (salles de classe / couloirs)
  3 = Chemin pavé / Cour de récréation
  4 = Arbre / Végétation
  5 = Terrain de sport (bleu/rouge)
  6 = Terrain de football (gazon synthétique)
"""

import json

# ── Dimensions de la carte ──────────────────────────────────────────────────
MAP_WIDTH = 60
MAP_HEIGHT = 60
TILE_SIZE = 32

# ── Dictionnaire des tuiles ─────────────────────────────────────────────────
TILES = {
    "herbe": 0,
    "mur": 1,
    "sol_interieur": 2,
    "pave": 3,
    "arbre": 4,
    "sport": 5,
    "football": 6,
}


def create_empty_grid(width: int, height: int, fill: int = 0) -> list[list[int]]:
    """Crée une grille 2D initialisée avec la valeur `fill`."""
    return [[fill] * width for _ in range(height)]


def fill_rect(grid: list[list[int]], x1: int, y1: int, x2: int, y2: int, tile_id: int):
    """Remplit un rectangle (bornes incluses) avec un tile_id donné."""
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            grid[y][x] = tile_id


def draw_building(grid: list[list[int]], x1: int, y1: int, x2: int, y2: int,
                  wall_id: int = 1, floor_id: int = 2):
    """
    Dessine un bâtiment : contours en `wall_id`, intérieur en `floor_id`.
    Les coordonnées sont inclusives.
    """
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if x == x1 or x == x2 or y == y1 or y == y2:
                grid[y][x] = wall_id
            else:
                grid[y][x] = floor_id


def flatten(grid: list[list[int]]) -> list[int]:
    """Aplatit une grille 2D en une liste 1D (ligne par ligne, de haut en bas)."""
    return [tile for row in grid for tile in row]


def apply_zoning(grid: list[list[int]]):
    """
    Applique les règles de zonage du campus sur la grille.
    Chaque zone est décrite par ses coordonnées et son type de remplissage.
    """

    # ── 1. Terrains de sport (Nord-Ouest) ────────────────────────────────────
    # De x=2 à x=15, y=2 à y=20 → ID 5
    fill_rect(grid, x1=2, y1=2, x2=15, y2=20, tile_id=TILES["sport"])

    # ── 2. Auditorium / Bâtiment Nord-Est ────────────────────────────────────
    # De x=30 à x=45, y=5 à y=25 → contours = 1, intérieur = 2
    draw_building(grid, x1=30, y1=5, x2=45, y2=25)

    # ── 3. Terrain de Football (Bordure Est) ─────────────────────────────────
    # De x=48 à x=59, y=0 à y=59 → ID 6
    fill_rect(grid, x1=48, y1=0, x2=59, y2=59, tile_id=TILES["football"])

    # ── 4. Cour Centrale ─────────────────────────────────────────────────────
    # De x=20 à x=45, y=26 à y=45 → ID 3 (pavés)
    fill_rect(grid, x1=20, y1=26, x2=45, y2=45, tile_id=TILES["pave"])

    # Grand arbre central (bloc 4×4 centré vers x=32, y=35)
    fill_rect(grid, x1=31, y1=34, x2=34, y2=37, tile_id=TILES["arbre"])

    # ── 5. Bâtiment Principal et Entrée (Sud) ────────────────────────────────
    # De x=15 à x=45, y=46 à y=55 → contours = 1, intérieur = 2
    draw_building(grid, x1=15, y1=46, x2=45, y2=55)

    # ── 6. Bordures d'arbres décoratifs autour du campus ─────────────────────
    # Rangée d'arbres en haut (y=0)
    for x in range(0, 48):
        grid[0][x] = TILES["arbre"]
    # Rangée d'arbres en bas (y=59)
    for x in range(0, 48):
        grid[59][x] = TILES["arbre"]
    # Rangée d'arbres à gauche (x=0)
    for y in range(0, 60):
        grid[y][0] = TILES["arbre"]
    # Petite allée d'arbres entre les terrains de sport et la cour
    for y in range(2, 21):
        grid[y][17] = TILES["arbre"]

    # ── 7. Chemins piétons reliant les zones ─────────────────────────────────
    # Chemin vertical reliant la cour au bâtiment sud
    fill_rect(grid, x1=30, y1=26, x2=32, y2=55, tile_id=TILES["pave"])
    # Chemin horizontal reliant les terrains de sport à l'auditorium
    fill_rect(grid, x1=16, y1=22, x2=29, y2=24, tile_id=TILES["pave"])
    # Chemin vertical reliant le chemin horizontal à la cour
    fill_rect(grid, x1=24, y1=24, x2=26, y2=26, tile_id=TILES["pave"])


def build_tiled_map(grid: list[list[int]]) -> dict:
    """
    Construit le dictionnaire Python qui imite la structure d'un fichier Tiled (.tmj / .json).
    Compatible WorkAdventure.
    """
    data = flatten(grid)

    tiled_map = {
        "compressionlevel": -1,
        "height": MAP_HEIGHT,
        "width": MAP_WIDTH,
        "infinite": False,
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "tilewidth": TILE_SIZE,
        "tileheight": TILE_SIZE,
        "tiledversion": "1.10.2",
        "type": "map",
        "version": "1.10",
        "nextlayerid": 2,
        "nextobjectid": 1,
        "layers": [
            {
                "id": 1,
                "name": "campus",
                "type": "tilelayer",
                "visible": True,
                "opacity": 1,
                "x": 0,
                "y": 0,
                "width": MAP_WIDTH,
                "height": MAP_HEIGHT,
                "data": data,
            }
        ],
        "tilesets": [
            {
                "firstgid": 1,
                "name": "campus_tiles",
                "tilewidth": TILE_SIZE,
                "tileheight": TILE_SIZE,
                "tilecount": 7,
                "columns": 7,
                "image": "campus_tiles.png",
                "imagewidth": 7 * TILE_SIZE,
                "imageheight": TILE_SIZE,
                "margin": 0,
                "spacing": 0,
                "tiles": [
                    {"id": 0, "type": "herbe"},
                    {"id": 1, "type": "mur"},
                    {"id": 2, "type": "sol_interieur"},
                    {"id": 3, "type": "pave"},
                    {"id": 4, "type": "arbre"},
                    {"id": 5, "type": "sport"},
                    {"id": 6, "type": "football"},
                ],
            }
        ],
    }
    return tiled_map


def main():
    """Point d'entrée : génère la grille, applique le zonage et exporte le JSON."""
    print("🏫 Génération de la carte du campus LFI Dubaï...")

    # 1. Initialiser la grille (tout en herbe par défaut)
    grid = create_empty_grid(MAP_WIDTH, MAP_HEIGHT, fill=TILES["herbe"])

    # 2. Appliquer les règles de zonage
    apply_zoning(grid)

    # 3. Construire la structure Tiled
    tiled_map = build_tiled_map(grid)

    # 4. Exporter en JSON
    output_file = "campus_lfi.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(tiled_map, f, indent=2, ensure_ascii=False)

    print(f"✅ Carte exportée avec succès dans « {output_file} »")
    print(f"   → {MAP_WIDTH}×{MAP_HEIGHT} tuiles ({MAP_WIDTH * TILE_SIZE}×{MAP_HEIGHT * TILE_SIZE} px)")
    print(f"   → {len(tiled_map['layers'][0]['data'])} tuiles dans le calque « campus »")
    print()
    print("📌 Prochaine étape : ouvrir ce fichier dans Tiled et associer un tileset !")


if __name__ == "__main__":
    main()

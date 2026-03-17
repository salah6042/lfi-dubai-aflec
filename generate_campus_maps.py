#!/usr/bin/env python3
"""
🏫 Générateur Campus Virtuel — LFI Dubaï (AFLEC) — v3.0
=========================================================
NOUVEAUTÉS v3 :
  • Points d'entrée nommés : les utilisateurs choisissent où atterrir
    via l'URL (ex: cour1.tmj#accueil, cour1.tmj#near-info, etc.)
  • Zones silencieuses dans les salles de classe (micro coupé auto)
  • Zones focusables (zoom caméra) dans les salles
  • Accueil central dans cour1 avec instructions
  • Meilleure navigation : flèches directionnelles aux intersections
  • Labels améliorés aux passages
"""

import json
import os

# ══════════════════════════════════════════════════════════════════════════════
# TILE IDs
# ══════════════════════════════════════════════════════════════════════════════

FLOOR_WOOD=725; FLOOR_CARPET=735; FLOOR_TILE=750; FLOOR_DARK=700
WALL_TL=403; WALL_T=479; WALL_TR=404
WALL_L=477; WALL_R=477
WALL_BL=433; WALL_B=685; WALL_BR=429
WALL_T_DOWN=535; DOOR_TOP=431; DOOR_MID=655; DOOR_BOT=680
GRASS_1=1858; GRASS_2=1859; PAVE_1=2461; SAND_1=1883
PALM_TOP=1836; PALM_BOT=1837
TREE_1=1911; TREE_2=1912; TREE_3=1913
WATER_TL=1908; WATER_T=1909; WATER_TR=1910
WATER_ML=1933; WATER_M=1934; WATER_MR=1935
WATER_BL=1958; WATER_B=1959; WATER_BR=1960
FLOWER_1=1961; FLOWER_2=1962; FLOWER_3=1963
PLANT_SM=90; PLANT_SM2=102; PLANT_BIG=187
BOARD_TL=142; BOARD_TM=143; BOARD_TR=144
BOARD_BL=162; BOARD_BM=163; BOARD_BR=164
TABLE_TL=1567; TABLE_T=1570; TABLE_TR=1568
TABLE_BL=1577; TABLE_B=1580; TABLE_BR=1578
DESK=1569; DESK2=1579
PC_TL=1572; PC_TR=1574; PC_BL=1582; PC_BR=1584
SCREEN_T=1562; SCREEN_B=1563
CHAIR_U=1494; CHAIR_D=1495; CHAIR_L=1496; CHAIR_R=1497
SOFA_TL=1518; SOFA_TR=1519; SOFA_BL=1535; SOFA_BR=1522
BOOKSH_T=1375; BOOKSH_M=1388; BOOKSH_B=1401
LAMP=238; LAMP2=239; CARPET_TL=250; CARPET_TR=251
ARROW_D=2704; SIGN=2743
COLLIDE=3

# ══════════════════════════════════════════════════════════════════════════════
# LETTRES PIXEL-ART (3×5)
# ══════════════════════════════════════════════════════════════════════════════

L3 = {
    'A':["###","# #","###","# #","# #"], 'B':["## ","# #","## ","# #","## "],
    'C':[" ##","#  ","#  ","#  "," ##"], 'D':["## ","# #","# #","# #","## "],
    'E':["###","#  ","## ","#  ","###"], 'F':["###","#  ","## ","#  ","#  "],
    'G':[" ##","#  ","# #","# #"," ##"], 'H':["# #","# #","###","# #","# #"],
    'I':["###"," # "," # "," # ","###"], 'J':["###","  #","  #","# #"," # "],
    'K':["# #","## ","#  ","## ","# #"], 'L':["#  ","#  ","#  ","#  ","###"],
    'M':["# #","###","###","# #","# #"], 'N':["# #","## ","###"," ##","# #"],
    'O':[" # ","# #","# #","# #"," # "], 'P':["## ","# #","## ","#  ","#  "],
    'Q':[" # ","# #","# #"," # ","  #"], 'R':["## ","# #","## ","# #","# #"],
    'S':[" ##","#  "," # ","  #","## "], 'T':["###"," # "," # "," # "," # "],
    'U':["# #","# #","# #","# #"," # "], 'V':["# #","# #","# #"," # "," # "],
    'W':["# #","# #","###","###","# #"], 'X':["# #"," # "," # "," # ","# #"],
    'Y':["# #"," # "," # "," # "," # "], 'Z':["###","  #"," # ","#  ","###"],
    '1':[" # ","## "," # "," # ","###"], '2':[" # ","# #","  #"," # ","###"],
    ' ':["   ","   ","   ","   ","   "],
}

# ══════════════════════════════════════════════════════════════════════════════
# UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def G(w, h, fill=0): return [[fill]*w for _ in range(h)]
def F(g): return [t for r in g for t in r]
def S(g,x,y,t):
    if 0<=y<len(g) and 0<=x<len(g[0]): g[y][x]=t
def R(g,x1,y1,x2,y2,t):
    for y in range(max(0,y1),min(len(g),y2+1)):
        for x in range(max(0,x1),min(len(g[0]),x2+1)): g[y][x]=t

def W(w,c,x1,y1,x2,y2,opens=None):
    ops=set(opens or [])
    S(w,x1,y1,WALL_TL); S(w,x2,y1,WALL_TR); S(w,x1,y2,WALL_BL); S(w,x2,y2,WALL_BR)
    S(c,x1,y1,COLLIDE); S(c,x2,y1,COLLIDE); S(c,x1,y2,COLLIDE); S(c,x2,y2,COLLIDE)
    for x in range(x1+1,x2):
        if ('t',x) not in ops: S(w,x,y1,WALL_T); S(c,x,y1,COLLIDE)
        if ('b',x) not in ops: S(w,x,y2,WALL_T); S(c,x,y2,COLLIDE)
    for y in range(y1+1,y2):
        if ('l',y) not in ops: S(w,x1,y,WALL_L); S(c,x1,y,COLLIDE)
        if ('r',y) not in ops: S(w,x2,y,WALL_R); S(c,x2,y,COLLIDE)
    for side,pos in ops:
        if side=='t': S(w,pos,y1,0); S(c,pos,y1,0)
        elif side=='b': S(w,pos,y2,0); S(c,pos,y2,0)
        elif side=='l': S(w,x1,pos,0); S(c,x1,pos,0)
        elif side=='r': S(w,x2,pos,0); S(c,x2,pos,0)

def label(g,text,sx,sy,tile):
    cx=sx
    for ch in text.upper():
        p=L3.get(ch)
        if not p: cx+=2; continue
        for dy,row in enumerate(p):
            for dx,px in enumerate(row):
                if px=='#': S(g,cx+dx,sy+dy,tile)
        cx+=len(p[0])+1

def fountain(fl,fn,co,cx,cy):
    tiles=[[WATER_TL,WATER_T,WATER_TR],[WATER_ML,WATER_M,WATER_MR],[WATER_BL,WATER_B,WATER_BR]]
    for dy in range(-1,2):
        for dx in range(-1,2):
            S(fn,cx+dx,cy+dy,tiles[dy+1][dx+1]); S(co,cx+dx,cy+dy,COLLIDE)
    for dx,dy in [(-3,-3),(3,-3),(-3,3),(3,3),(-3,0),(3,0),(0,-3),(0,3)]:
        S(fn,cx+dx,cy+dy-1,PALM_TOP); S(fn,cx+dx,cy+dy,PALM_BOT); S(co,cx+dx,cy+dy,COLLIDE)

def palm_row(fn,co,x1,x2,y,sp=3):
    for x in range(x1,x2+1,sp):
        S(fn,x,y-1,PALM_TOP); S(fn,x,y,PALM_BOT); S(co,x,y,COLLIDE)

# ══════════════════════════════════════════════════════════════════════════════
# TILESETS
# ══════════════════════════════════════════════════════════════════════════════

TS = [
    {"columns":6,"firstgid":1,"image":"tilesets/WA_Special_Zones.png","imageheight":64,"imagewidth":192,"margin":0,"name":"WA_Special_Zones","spacing":0,"tilecount":12,"tileheight":32,"tiles":[{"id":2,"properties":[{"name":"collides","type":"bool","value":True}]}],"tilewidth":32},
    {"columns":12,"firstgid":13,"image":"tilesets/WA_Decoration.png","imageheight":256,"imagewidth":384,"margin":0,"name":"WA_Decoration","spacing":0,"tilecount":96,"tileheight":32,"tilewidth":32},
    {"columns":10,"firstgid":109,"image":"tilesets/WA_Miscellaneous.png","imageheight":352,"imagewidth":320,"margin":0,"name":"WA_Miscellaneous","spacing":0,"tilecount":110,"tileheight":32,"tilewidth":32},
    {"columns":12,"firstgid":219,"image":"tilesets/WA_Other_Furniture.png","imageheight":416,"imagewidth":384,"margin":0,"name":"WA_Other_Furniture","spacing":0,"tilecount":156,"tileheight":32,"tilewidth":32},
    {"columns":25,"firstgid":375,"image":"tilesets/WA_Room_Builder.png","imageheight":1280,"imagewidth":800,"margin":0,"name":"WA_Room_Builder","spacing":0,"tilecount":1000,"tileheight":32,"tilewidth":32},
    {"columns":13,"firstgid":1375,"image":"tilesets/WA_Seats.png","imageheight":448,"imagewidth":416,"margin":0,"name":"WA_Seats","spacing":0,"tilecount":182,"tileheight":32,"tilewidth":32},
    {"columns":10,"firstgid":1557,"image":"tilesets/WA_Tables.png","imageheight":864,"imagewidth":320,"margin":0,"name":"WA_Tables","spacing":0,"tilecount":270,"tileheight":32,"tilewidth":32},
    {"columns":6,"firstgid":1827,"image":"tilesets/WA_Logo_Long.png","imageheight":32,"imagewidth":192,"margin":0,"name":"WA_Logo_Long","spacing":0,"tilecount":6,"tileheight":32,"tilewidth":32},
    {"columns":25,"firstgid":1833,"image":"tilesets/WA_Exterior.png","imageheight":1088,"imagewidth":800,"margin":0,"name":"WA_Exterior","spacing":0,"tilecount":850,"tileheight":32,"tilewidth":32},
    {"columns":13,"firstgid":2683,"image":"tilesets/WA_User_Interface.png","imageheight":672,"imagewidth":416,"margin":0,"name":"WA_User_Interface","spacing":0,"tilecount":273,"tileheight":32,"tilewidth":32},
]

# ══════════════════════════════════════════════════════════════════════════════
# ASSEMBLEUR
# ══════════════════════════════════════════════════════════════════════════════

def tl(name,lid,data,w,h):
    return {"data":F(data),"height":h,"id":lid,"name":name,"opacity":1,"type":"tilelayer","visible":True,"width":w,"x":0,"y":0}

def ol(name,lid,objs):
    return {"draworder":"topdown","id":lid,"name":name,"objects":objs,"opacity":1,"type":"objectgroup","visible":True,"x":0,"y":0}

def exit_z(oid,name,x,y,w,h,target):
    return {"height":h*32,"id":oid,"name":name,"properties":[{"name":"exitUrl","type":"string","value":target}],"rotation":0,"type":"area","visible":True,"width":w*32,"x":x*32,"y":y*32}

def jitsi_z(oid,name,room,x,y,w,h):
    return {"height":h*32,"id":oid,"name":name,"properties":[{"name":"focusable","type":"bool","value":True},{"name":"jitsiRoom","type":"string","value":room},{"name":"jitsiTrigger","type":"string","value":"onaction"},{"name":"zoom_margin","type":"float","value":1}],"rotation":0,"type":"area","visible":True,"width":w*32,"x":x*32,"y":y*32}

def start_z(oid,name,x,y,w=1,h=1):
    """Zone de départ nommée. Le nom permet d'y atterrir via URL#nom."""
    return {"height":h*32,"id":oid,"name":name,"properties":[{"name":"start","type":"bool","value":True}],"rotation":0,"type":"area","visible":True,"width":w*32,"x":x*32,"y":y*32}

def silent_z(oid,name,desc,x,y,w,h):
    """Zone silencieuse: micro coupé automatiquement."""
    return {"height":h*32,"id":oid,"name":name,"properties":[{"name":"silent","type":"bool","value":True}],"rotation":0,"type":"area","visible":True,"width":w*32,"x":x*32,"y":y*32}

def focus_z(oid,name,x,y,w,h,zoom=1.5):
    """Zone focusable: zoom caméra automatique."""
    return {"height":h*32,"id":oid,"name":name,"properties":[{"name":"focusable","type":"bool","value":True},{"name":"zoom_margin","type":"float","value":zoom}],"rotation":0,"type":"area","visible":True,"width":w*32,"x":x*32,"y":y*32}

def bmap(w,h,layers,objs,name,desc,nlid=20,noid=50):
    return {"compressionlevel":-1,"height":h,"infinite":False,"layers":layers+[ol("zones-interactives",nlid-1,objs)],"nextlayerid":nlid,"nextobjectid":noid,"orientation":"orthogonal","properties":[{"name":"mapCopyright","type":"string","value":"LFI Dubaï - AFLEC"},{"name":"mapDescription","type":"string","value":desc},{"name":"mapName","type":"string","value":name}],"renderorder":"right-down","tiledversion":"1.11.2","tileheight":32,"tilesets":TS,"tilewidth":32,"type":"map","version":"1.10","width":w}


# ══════════════════════════════════════════════════════════════════════════════
# COUR 1 (50×50) — avec points d'entrée nommés
# ══════════════════════════════════════════════════════════════════════════════

def gen_cour1():
    WW, HH = 50, 50
    fl=G(WW,HH,PAVE_1); wl=G(WW,HH,0); fn=G(WW,HH,0)
    ab=G(WW,HH,0); co=G(WW,HH,0); st=G(WW,HH,0); lb=G(WW,HH,0)

    R(fl,0,0,WW-1,2,GRASS_1); R(fl,0,HH-3,WW-1,HH-1,GRASS_1)
    R(fl,0,0,2,HH-1,GRASS_1); R(fl,WW-3,0,WW-1,HH-1,GRASS_1)

    opens=[]
    for y in [9,10,11,17,18,19,25,26,27,33,34,35]: opens.append(('l',y))
    for y in [9,10,11,17,18,19,25,26,27]: opens.append(('r',y))
    for x in [23,24,25,26]: opens.append(('b',x))
    for x in [10,11,12,37,38,39]: opens.append(('t',x))
    W(wl,co,0,0,WW-1,HH-1,opens)

    fountain(fl,fn,co,WW//2,HH//2-2)
    palm_row(fn,co,5,WW-6,4,4); palm_row(fn,co,5,WW-6,HH-6,4)
    for y in range(6,HH-6,5):
        S(fn,4,y-1,PALM_TOP); S(fn,4,y,PALM_BOT); S(co,4,y,COLLIDE)
        S(fn,WW-5,y-1,PALM_TOP); S(fn,WW-5,y,PALM_BOT); S(co,WW-5,y,COLLIDE)

    label(fl,"AFLEC",15,HH-11,FLOOR_CARPET)
    for x in range(7,WW-7,4):
        S(ab,x,HH//2-8,FLOWER_1); S(ab,x+1,HH//2-8,FLOWER_2)
        S(ab,x,HH//2+6,FLOWER_2); S(ab,x+1,HH//2+6,FLOWER_3)

    # Labels à chaque passage
    label(lb,"INFO",3,7,FLOOR_DARK); label(lb,"MATHS",3,15,FLOOR_DARK)
    label(lb,"FRANCAIS",3,23,FLOOR_DARK); label(lb,"ARABE",3,31,FLOOR_DARK)
    label(lb,"TECHNO",WW-21,7,FLOOR_DARK); label(lb,"SVT",WW-13,15,FLOOR_DARK)
    label(lb,"ANGLAIS",WW-25,23,FLOOR_DARK)
    label(lb,"COUR 2",19,HH-8,FLOOR_DARK)
    label(lb,"OFFICE",5,4,FLOOR_DARK); label(lb,"CONFERENCE",30,4,FLOOR_DARK)

    # Label "ACCUEIL" au centre de la cour (zone d'atterrissage par défaut)
    label(lb,"ACCUEIL",18,HH//2+4,FLOOR_DARK)

    for y in [8,16,24,32]:
        S(ab,2,y,SIGN); S(ab,1,y+1,ARROW_D)
    for y in [8,16,24]:
        S(ab,WW-3,y,SIGN); S(ab,WW-2,y+1,ARROW_D)

    st[HH//2+3][WW//2]=2  # tile de spawn par défaut

    objs=[]; oid=1

    # ════════════════════════════════════════════════════════════
    # POINTS D'ENTRÉE NOMMÉS (le cœur de la fonctionnalité)
    # L'utilisateur peut atterrir où il veut via l'URL :
    #   cour1.tmj#accueil      → centre de la cour
    #   cour1.tmj#near-info    → à côté de la salle info
    #   cour1.tmj#near-maths   → à côté de la salle maths
    #   etc.
    # ════════════════════════════════════════════════════════════
    named_starts = [
        ("accueil",       WW//2, HH//2+3, 3, 1),   # défaut: centre cour
        ("from-office",   11,    2,       1, 1),    # arrivée depuis office
        ("from-conference",38,   2,       1, 1),    # arrivée depuis conference
        ("from-cour2",    24,    HH-3,   1, 1),    # arrivée depuis cour2
        ("near-info",     3,     10,      1, 1),    # à côté de salle info
        ("near-maths",    3,     18,      1, 1),    # à côté de maths
        ("near-francais", 3,     26,      1, 1),    # à côté de français
        ("near-arabe",    3,     34,      1, 1),    # à côté d'arabe
        ("near-techno",   WW-4,  10,      1, 1),    # à côté de techno
        ("near-svt",      WW-4,  18,      1, 1),    # à côté de SVT
        ("near-anglais",  WW-4,  26,      1, 1),    # à côté d'anglais
    ]
    for name,x,y,w,h in named_starts:
        objs.append(start_z(oid,name,x,y,w,h)); oid+=1

    # Exits vers les salles
    doors=[
        ("exit-info",0,9,1,3,"salle-info.tmj"),
        ("exit-maths",0,17,1,3,"maths.tmj"),
        ("exit-francais",0,25,1,3,"francais.tmj"),
        ("exit-arabic",0,33,1,3,"arabic.tmj"),
        ("exit-techno",WW-1,9,1,3,"salle-techno1.tmj"),
        ("exit-svt",WW-1,17,1,3,"svt.tmj"),
        ("exit-anglais",WW-1,25,1,3,"anglais.tmj"),
        ("exit-cour2",23,HH-1,4,1,"cour2.tmj#accueil"),
        ("exit-office",10,0,3,1,"office.tmj#from-cour1"),
        ("exit-conference",37,0,3,1,"conference.tmj#from-cour1"),
    ]
    for n,x,y,w,h,t in doors:
        objs.append(exit_z(oid,n,x,y,w,h,t)); oid+=1

    layers=[tl("start",1,st,WW,HH),tl("collisions",2,co,WW,HH),
            tl("floor",3,fl,WW,HH),tl("walls",4,wl,WW,HH),
            tl("furniture",5,fn,WW,HH),tl("labels",6,lb,WW,HH),
            tl("above",7,ab,WW,HH)]
    return bmap(WW,HH,layers,objs,"Cour Principale — LFI Dubaï",
        "Hub avec points d'entrée nommés, fontaine, palmiers, labels",12,oid)


# ══════════════════════════════════════════════════════════════════════════════
# COUR 2 (50×50)
# ══════════════════════════════════════════════════════════════════════════════

def gen_cour2():
    WW, HH = 50, 50
    fl=G(WW,HH,PAVE_1); wl=G(WW,HH,0); fn=G(WW,HH,0)
    ab=G(WW,HH,0); co=G(WW,HH,0); st=G(WW,HH,0); lb=G(WW,HH,0)

    R(fl,0,0,WW-1,2,SAND_1); R(fl,0,HH-3,WW-1,HH-1,SAND_1)
    R(fl,0,0,2,HH-1,SAND_1); R(fl,WW-3,0,WW-1,HH-1,SAND_1)

    W(wl,co,0,0,WW-1,HH-1,[('t',23),('t',24),('t',25),('t',26)])

    # Zone détente 1: canapés
    R(fl,5,5,18,16,FLOOR_CARPET)
    for dy in [0,2]:
        for dx in [0,3,6,9]:
            S(fn,6+dx,6+dy,SOFA_TL); S(fn,7+dx,6+dy,SOFA_TR)
    for dx in [0,5,10]:
        S(fn,6+dx,9,TABLE_TL); S(fn,7+dx,9,TABLE_TR)
        S(fn,6+dx,10,TABLE_BL); S(fn,7+dx,10,TABLE_BR)
    for dx in [0,3,6,9]:
        S(fn,6+dx,12,SOFA_TL); S(fn,7+dx,12,SOFA_TR)
    S(ab,5,5,PLANT_BIG); S(ab,18,5,PLANT_BIG)

    # Cool Zone
    R(fl,25,18,44,32,FLOOR_CARPET)
    for y in range(19,31,3):
        for x in range(27,43,4):
            S(fn,x,y,CARPET_TL); S(fn,x+1,y,CARPET_TR)
    S(ab,25,18,LAMP); S(ab,44,18,LAMP2)

    # Palmiers
    for x in range(6,44,3):
        S(fn,x,23,PALM_TOP); S(fn,x,24,PALM_BOT); S(co,x,24,COLLIDE)

    fountain(fl,fn,co,38,40)

    # Bibliothèques
    for x in range(6,20,2):
        S(fn,x,36,BOOKSH_T); S(fn,x,37,BOOKSH_M); S(fn,x,38,BOOKSH_B)
        S(co,x,36,COLLIDE); S(co,x,37,COLLIDE); S(co,x,38,COLLIDE)

    for x in range(5,WW-5,5): S(ab,x,3,FLOWER_1); S(ab,x,HH-4,FLOWER_3)

    label(lb,"COUR 1",19,3,FLOOR_DARK)
    label(lb,"DETENTE",6,4,FLOOR_DARK)
    label(lb,"COOL ZONE",26,16,FLOOR_DARK)

    objs=[]; oid=1
    objs.append(start_z(oid,"accueil",WW//2,4)); oid+=1
    objs.append(start_z(oid,"from-cour1",24,3)); oid+=1
    objs.append(exit_z(oid,"exit-cour1",23,0,4,1,"cour1.tmj#from-cour2")); oid+=1
    objs.append(jitsi_z(oid,"jitsiCoolZone","CoolZone",25,18,19,14)); oid+=1
    objs.append(silent_z(oid,"silentBiblio","Bibliothèque silencieuse",5,34,16,8)); oid+=1
    objs.append(focus_z(oid,"focusFontaine",32,34,12,12,2.0)); oid+=1

    layers=[tl("start",1,st,WW,HH),tl("collisions",2,co,WW,HH),
            tl("floor",3,fl,WW,HH),tl("walls",4,wl,WW,HH),
            tl("furniture",5,fn,WW,HH),tl("labels",6,lb,WW,HH),
            tl("above",7,ab,WW,HH)]
    return bmap(WW,HH,layers,objs,"Cour de Détente",
        "Détente, bibliothèque silencieuse, cool zone Jitsi",12,oid)


# ══════════════════════════════════════════════════════════════════════════════
# SALLES DE CLASSE 30×30 — avec zones silencieuses + focusables
# ══════════════════════════════════════════════════════════════════════════════

def gen_class(name,dname,lbl,exit_target="cour1.tmj",style="standard"):
    WW, HH = 30, 30
    fl=G(WW,HH,FLOOR_WOOD); wl=G(WW,HH,0); fn=G(WW,HH,0)
    ab=G(WW,HH,0); co=G(WW,HH,0); st=G(WW,HH,0); lb=G(WW,HH,0)

    R(fl,1,1,WW-2,HH-2,FLOOR_CARPET)
    opens=[('b',WW//2-1),('b',WW//2),('b',WW//2+1)]
    W(wl,co,0,0,WW-1,HH-1,opens)

    # Tableau (5 tiles large)
    bx=WW//2-2
    for dx in range(5):
        S(fn,bx+dx,1,BOARD_TL if dx==0 else BOARD_TR if dx==4 else BOARD_TM)
        S(fn,bx+dx,2,BOARD_BL if dx==0 else BOARD_BR if dx==4 else BOARD_BM)
        S(co,bx+dx,1,COLLIDE); S(co,bx+dx,2,COLLIDE)

    # Bureau prof
    for dx in range(-1,2):
        S(fn,WW//2+dx,4,DESK); S(co,WW//2+dx,4,COLLIDE)
    S(fn,WW//2,3,CHAIR_U)

    # Mobilier élèves
    if style=="computer_islands":
        for ix,iy in [(5,8),(14,8),(23,8),(5,17),(14,17),(23,17)]:
            S(fn,ix,iy,PC_TL); S(fn,ix+1,iy,PC_TR)
            S(fn,ix,iy+1,PC_BL); S(fn,ix+1,iy+1,PC_BR)
            S(co,ix,iy,COLLIDE); S(co,ix+1,iy,COLLIDE)
            S(co,ix,iy+1,COLLIDE); S(co,ix+1,iy+1,COLLIDE)
            S(fn,ix-1,iy,CHAIR_R); S(fn,ix+2,iy,CHAIR_L)
            S(fn,ix-1,iy+1,CHAIR_R); S(fn,ix+2,iy+1,CHAIR_L)

    elif style=="computer_rows":
        for row_y in [8,13,18,23]:
            for x in range(3,26,3):
                S(fn,x,row_y,DESK); S(fn,x+1,row_y,DESK)
                S(fn,x,row_y-1,SCREEN_T); S(fn,x+1,row_y-1,SCREEN_T)
                S(co,x,row_y,COLLIDE); S(co,x+1,row_y,COLLIDE)
                S(co,x,row_y-1,COLLIDE); S(co,x+1,row_y-1,COLLIDE)
                S(fn,x,row_y+1,CHAIR_U); S(fn,x+1,row_y+1,CHAIR_U)

    elif style=="science":
        for row_y in [8,13,18,23]:
            for x in range(3,24,5):
                for dx in range(4):
                    t={0:TABLE_TL,3:TABLE_TR}.get(dx,TABLE_T)
                    b={0:TABLE_BL,3:TABLE_BR}.get(dx,TABLE_B)
                    S(fn,x+dx,row_y,t); S(fn,x+dx,row_y+1,b); S(co,x+dx,row_y,COLLIDE)
                for dx in range(4):
                    S(fn,x+dx,row_y+2,CHAIR_U)
        for cx,cy in [(1,1),(WW-2,1),(1,HH-3),(WW-2,HH-3)]:
            S(ab,cx,cy,PLANT_BIG)

    else:
        for row_y in [7,11,15,19,23]:
            for x in range(3,25,4):
                for dx in range(3):
                    S(fn,x+dx,row_y,DESK); S(co,x+dx,row_y,COLLIDE)
                    S(fn,x+dx,row_y+1,CHAIR_U)

    if style!="science":
        S(ab,1,1,PLANT_SM); S(ab,WW-2,1,PLANT_SM)

    for y in [5,8,11]:
        S(fn,WW-2,y,BOOKSH_T); S(fn,WW-2,y+1,BOOKSH_M); S(fn,WW-2,y+2,BOOKSH_B)
        S(co,WW-2,y,COLLIDE); S(co,WW-2,y+1,COLLIDE); S(co,WW-2,y+2,COLLIDE)

    # Labels
    label(lb,lbl,2,HH-7,FLOOR_DARK)
    label(lb,"COUR 1",WW//2+3,HH-3,FLOOR_DARK)

    objs=[]; oid=1
    # Points d'entrée nommés pour la salle
    objs.append(start_z(oid,"accueil",WW//2,HH-3)); oid+=1
    objs.append(start_z(oid,f"from-cour1",WW//2,HH-3)); oid+=1

    # Exit
    objs.append(exit_z(oid,f"exit-{name}",WW//2-1,HH-1,3,1,exit_target)); oid+=1

    # Jitsi couvrant la salle (visio de classe)
    objs.append(jitsi_z(oid,f"jitsi-{name}",dname.replace(" ",""),2,3,WW-4,HH-6)); oid+=1

    # Zone silencieuse (zone tableau/prof = concentration)
    objs.append(silent_z(oid,f"silent-{name}","Zone tableau silencieuse",2,1,WW-4,4)); oid+=1

    # Zone focusable (zoom sur le tableau quand on s'approche)
    objs.append(focus_z(oid,f"focus-tableau-{name}",WW//2-4,1,8,3,2.0)); oid+=1

    layers=[tl("start",1,st,WW,HH),tl("collisions",2,co,WW,HH),
            tl("floor",3,fl,WW,HH),tl("walls",4,wl,WW,HH),
            tl("furniture",5,fn,WW,HH),tl("labels",6,lb,WW,HH),
            tl("above",7,ab,WW,HH)]
    return bmap(WW,HH,layers,objs,dname,
        f"{dname} — 30×30, 20+ places, Jitsi, zone silencieuse, zoom tableau",12,oid)


# ══════════════════════════════════════════════════════════════════════════════
# PATCH office.tmj + conference.tmj
# ══════════════════════════════════════════════════════════════════════════════

def patch_map(filename, exits_to_add, starts_to_add):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for layer in data["layers"]:
        if layer.get("type") == "objectgroup" and layer.get("name") == "floorLayer":
            existing = {o["name"] for o in layer["objects"]}
            mid = max((o["id"] for o in layer["objects"]), default=20)

            for ename, props in exits_to_add:
                if ename not in existing:
                    mid += 1
                    layer["objects"].append({"height":props["h"],"id":mid,"name":ename,"properties":[{"name":"exitUrl","type":"string","value":props["target"]}],"rotation":0,"type":"area","visible":True,"width":props["w"],"x":props["x"],"y":props["y"]})

            for sname, props in starts_to_add:
                if sname not in existing:
                    mid += 1
                    layer["objects"].append({"height":32,"id":mid,"name":sname,"properties":[{"name":"start","type":"bool","value":True}],"rotation":0,"type":"area","visible":True,"width":32,"x":props["x"],"y":props["y"]})

            data["nextobjectid"] = mid + 1
            break

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def patch_office():
    w_map = 50  # largeur de office.tmj
    patch_map("office.tmj",
        exits_to_add=[
            ("to-cour1", {"x": (w_map//2-1)*32, "y": 0, "w": 96, "h": 32, "target": "cour1.tmj#from-office"}),
        ],
        starts_to_add=[
            ("from-cour1", {"x": (w_map//2)*32, "y": 64}),
        ]
    )

def patch_conference():
    # conference.tmj = 24×14
    patch_map("conference.tmj",
        exits_to_add=[
            ("to-cour1", {"x": 11*32, "y": 13*32, "w": 96, "h": 32, "target": "cour1.tmj#from-conference"}),
        ],
        starts_to_add=[
            ("from-cour1", {"x": 12*32, "y": 12*32}),
        ]
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    BASE = os.path.dirname(os.path.abspath(__file__))
    print("="*65)
    print("🏫 LFI Dubaï — Campus v3.0 (Multi-Entry, Silent, Focus)")
    print("="*65); print()

    maps = [
        ("cour1.tmj", gen_cour1),
        ("cour2.tmj", gen_cour2),
        ("salle-info.tmj",    lambda: gen_class("salle-info","Salle Informatique","INFO",style="computer_islands")),
        ("salle-techno1.tmj", lambda: gen_class("salle-techno1","Salle Technologie","TECHNO",style="computer_rows")),
        ("maths.tmj",         lambda: gen_class("maths","Mathematiques","MATHS")),
        ("svt.tmj",           lambda: gen_class("svt","SVT","SVT",style="science")),
        ("francais.tmj",      lambda: gen_class("francais","Francais","FRANCAIS")),
        ("anglais.tmj",       lambda: gen_class("anglais","English","ANGLAIS")),
        ("arabic.tmj",        lambda: gen_class("arabic","Arabe","ARABE")),
    ]

    for fname, gen in maps:
        data = gen()
        with open(os.path.join(BASE,fname),"w",encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        w,h = data["width"],data["height"]
        nobj = sum(len(l.get("objects",[])) for l in data["layers"] if l["type"]=="objectgroup")
        print(f"  ✅ {fname:25s} {w}×{h}  ({nobj} objets)")

    print(); print("  📝 Patch office.tmj...")
    patch_office(); print("  ✅ office.tmj patché")
    print("  📝 Patch conference.tmj...")
    patch_conference(); print("  ✅ conference.tmj patché")

    print()
    print("="*65)
    print("🎉 CAMPUS v3.0 COMPLET !")
    print()
    print("🚪 POINTS D'ENTRÉE NOMMÉS (URL → destination) :")
    print()
    print("  cour1.tmj#accueil       → Centre de la cour (défaut)")
    print("  cour1.tmj#near-info     → À côté de la salle Info")
    print("  cour1.tmj#near-maths    → À côté de la salle Maths")
    print("  cour1.tmj#near-francais → À côté de Français")
    print("  cour1.tmj#near-arabe    → À côté d'Arabe")
    print("  cour1.tmj#near-techno   → À côté de Techno")
    print("  cour1.tmj#near-svt      → À côté de SVT")
    print("  cour1.tmj#near-anglais  → À côté d'Anglais")
    print("  cour2.tmj#accueil       → Centre de la cour détente")
    print("  salle-info.tmj#accueil  → Direct en salle info")
    print("  maths.tmj#accueil       → Direct en maths")
    print("  ... (toutes les salles)")
    print()
    print("🔇 ZONES SILENCIEUSES :")
    print("  • Zone tableau/prof dans chaque salle (micro coupé)")
    print("  • Bibliothèque dans cour2")
    print()
    print("🔍 ZONES FOCUSABLES :")
    print("  • Zoom auto sur le tableau en s'approchant")
    print("  • Zoom sur la fontaine dans cour2")
    print("="*65)


if __name__ == "__main__":
    main()

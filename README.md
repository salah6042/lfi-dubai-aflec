<p align="center">
  <img src="https://workadventu.re/images/logo-WA-min.png" alt="WorkAdventure" width="280"/>
</p>

<h1 align="center">🏫 LFI Dubai – Campus Virtuel Interactif</h1>

<p align="center">
  <em>Un espace immersif pour apprendre, collaborer et interagir à distance.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Plateforme-WorkAdventure-6C5CE7?style=for-the-badge&logo=data:image/svg+xml;base64,..." alt="WorkAdventure"/>
  <img src="https://img.shields.io/badge/Statut-En%20Production-00B894?style=for-the-badge" alt="Statut"/>
  <img src="https://img.shields.io/badge/Licence-MIT-0984E3?style=for-the-badge" alt="Licence"/>
</p>

---

## 🌐 Qu'est-ce que WorkAdventure ?

[**WorkAdventure**](https://workadventu.re) est une plateforme open source qui permet de créer des **espaces virtuels interactifs** sous forme de cartes 2D pixelisées. Les utilisateurs s'y déplacent avec un avatar et peuvent :

- 💬 Discuter en **visioconférence** en se rapprochant les uns des autres
- 🗺️ Explorer des **environnements personnalisés** (salles de classe, couloirs, espaces communs…)
- 🤝 Collaborer grâce à des **zones interactives** et des liens intégrés

---

## 🎯 Le Projet

Ce projet met en place un **campus virtuel** pour les élèves du **Lycée Français International de Dubaï (AFLEC)**, destiné à enrichir l'expérience d'apprentissage lors des **cours en distanciel**.

L'espace permet de :

- 📺 **Suivre des visios** dans des salles de classe virtuelles
- 🎮 **Participer à des activités de groupe** de manière interactive
- 🚶 **Se déplacer librement** entre les différents espaces du campus
- 🧑‍🤝‍🧑 **Favoriser le lien social** entre élèves, même à distance

---

## 🏗️ Architecture du Projet

```
lfi-dubai-aflec/
├── my-map/            # Cartes et scripts WorkAdventure
│   ├── map.json       # Carte principale du campus
│   ├── cdn/           # Ressources statiques
│   ├── src/           # Scripts TypeScript
│   └── index.html     # Point d'entrée
├── lfidubai-aflec/    # Pages web du projet
└── README.md
```

---

## 🚀 Installation & Lancement

```bash
# Cloner le dépôt
git clone https://github.com/salah6042/lfi-dubai-aflec.git
cd lfi-dubai-aflec/my-map

# Installer les dépendances
npm install

# Lancer en local
npm run start
```

> Le serveur de développement sera accessible sur **http://localhost:8080/**

---

## 👨‍🏫 Crédits

Projet mis en place et optimisé par **M. Salah** — Professeur de Technologie, SNT, NSI et animateur du club de programmation au LFI Dubai (AFLEC).

---

## 📄 Licences

Ce projet utilise plusieurs licences :

| Composant | Licence |
|-----------|---------|
| Code source | [MIT](./my-map/LICENSE.code) |
| Cartes | [CC BY-SA 4.0](./my-map/LICENSE.map) |
| Assets graphiques | [Voir détails](./my-map/LICENSE.assets) |

---

<p align="center">
  <strong>LFI Dubai · AFLEC · WorkAdventure</strong><br/>
  <sub>🌍 Apprendre sans frontières</sub>
</p>

<div align="center">

# 📸 Comparateur Pro — Before / After Image Compare

<p>
  <img src="https://img.shields.io/badge/Langue-Français-007acc?style=for-the-badge" alt="Langue Français">
  <img src="https://img.shields.io/badge/Language-English-007acc?style=for-the-badge" alt="Language English">
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/PyQt5-GUI-41CD52?style=flat-square&logo=qt&logoColor=white" alt="PyQt5">
  <img src="https://img.shields.io/badge/OpenCV-Vision-5C3EE8?style=flat-square&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Version-2.0.0-success?style=flat-square" alt="Version 2.0.0">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square" alt="License MIT">
  <img src="https://img.shields.io/badge/Open_Source-%E2%9C%94-success?style=flat-square" alt="Open Source">
</p>

<p><b>Un outil de comparaison et de compilation d'images professionnel, léger et rapide, pour Windows.</b></p>
<p><i>A professional, lightweight and fast image comparison &amp; compilation tool for Windows.</i></p>

<!-- ════════════════════════════════════════════════════════════════════ -->
<!--  EMPLACEMENT CAPTURE PRINCIPALE — collez ici le lien de l'image       -->
<!--  Exemple : <img src="LIEN_IMAGE_INTERFACE" width="820">               -->
<!-- ════════════════════════════════════════════════════════════════════ -->
<img src="" alt="Interface principale de Comparateur Pro" width="820">

</div>

---

> 🇫🇷 **Français** &nbsp;·&nbsp; 🇬🇧 [Jump to English version](#-english-version)

---

# 🇫🇷 Version française

**Comparateur Pro** simplifie la comparaison de plusieurs images en même temps,
avec une synchronisation parfaite du zoom et du déplacement, un auto-alignement
intelligent et une analyse par carte thermique. Depuis la version 2.0, il intègre
aussi un **créateur de compilations d'images** : montez des grilles et des
planches (couvertures de galeries, présentations avant/après…) sans passer par
un logiciel de retouche externe.

C'est l'outil idéal pour les photographes, les graphistes et toute personne qui
a besoin de comparaisons visuelles précises ou de planches d'images soignées.

## ✨ Fonctionnalités

### 🔍 Comparateur d'images
- **Comparaison multi-images** — curseurs mobiles fluides pour révéler chaque image.
- **Synchronisation totale** — zoom (Ctrl + Molette) et déplacement (Clic droit) appliqués simultanément à toutes les images.
- **Mode Blink** — maintenez **Espace** pour alterner instantanément avec l'image de référence.
- **Auto-alignement intelligent** — cale automatiquement des images légèrement décalées (algorithme affine 2D).
- **Analyse Heatmap** — carte thermique cumulative pour visualiser les différences.
- **Export professionnel** — images propres au format 1:1 (JPEG, PNG, GIF animé), avec étiquettes et filigrane personnalisables.
- **Menu clic droit Windows** — lancez une comparaison ou un export rapide directement depuis l'explorateur.

### 🧩 Compilation d'images *(nouveau en v2.0)*
- **Gabarits de grille** — 7 dispositions intégrées (2, 3, 4, 6, 9 cases) + éditeur pour créer et sauver vos propres gabarits.
- **Glisser-déposer par case** — déposez chaque image directement dans la case voulue.
- **Formats de sortie** — presets prêts à l'emploi (couvertures, 16:9, carré, portrait…) ou dimensions libres en pixels, avec verrou de ratio et inversion largeur/hauteur.
- **Ajustement des images** — repositionnez l'image dans sa case par glisser, zoomez à la molette.
- **Interversion** — échangez deux cases d'un Ctrl + glisser.
- **Séparateur facultatif** — barres entre les cases, couleur et épaisseur réglables.
- **Étiquettes par case** — un clic sur l'étiquette ouvre le choix du texte : automatique (nom du fichier), nom favori ou saisie manuelle.
- **Export automatique** — sauvegarde 1:1 propre dans le dossier de vos images.

### ⚙️ Confort et personnalisation
- **Interface à onglets** — bascule fluide entre Comparateur et Compilation.
- **Réglages centralisés** — bouton ⚙ toujours accessible.
- **Multilingue** — français et anglais natifs, détection automatique de la langue système.
- **Traduction communautaire** — exportez un fichier de langue, traduisez-le, réimportez-le.

## 🖼️ Captures d'écran

<!-- ════════════════════════════════════════════════════════════════════ -->
<!--  EMPLACEMENTS CAPTURES — collez vos liens d'images entre les balises   -->
<!-- ════════════════════════════════════════════════════════════════════ -->

<div align="center">

<!-- Capture 1 : le comparateur en action -->
<img src="" alt="Le comparateur d'images" width="780">

<br><br>

<!-- Capture 2 : l'outil de compilation -->
<img src="" alt="L'outil de compilation" width="780">

<br><br>

<!-- Capture 3 : un export de compilation -->
<img src="" alt="Exemple d'export de compilation" width="780">

<br><br>

<!-- Capture 4 : l'intégration au menu clic droit -->
<img src="" alt="Intégration au menu clic droit Windows" width="620">

</div>

## 🚀 Installation

### 1. Prérequis
Assurez-vous d'avoir **Python 3** installé, puis installez les dépendances :

```bash
pip install -r requirements.txt
```

### 2. Lancement
```bash
python comparateur_app.py
```

### 3. Intégration au menu clic droit Windows *(optionnel)*
L'intégration est automatisée et portable :

1. Double-cliquez sur **`install_raccourcis.bat`**.
2. Le script détecte automatiquement l'emplacement du dossier.
3. Choisissez la langue du menu (1 = Français, 2 = Anglais).
4. C'est prêt. Si vous déplacez le dossier, relancez simplement le `.bat`.

> **Important** — utilisez toujours `install_raccourcis.bat`, qui s'adapte
> à l'emplacement réel du dossier. N'importez pas de fichier `.reg` : un
> `.reg` contient un chemin figé qui ne correspondra pas à votre machine.

Pour retirer le menu : double-cliquez sur **`desinstaller_raccourcis.bat`**.

## ⌨️ Raccourcis clavier

| Raccourci | Action |
|---|---|
| **Espace** (maintenu) | Mode Blink : affiche l'image de référence |
| **Ctrl + Molette** | Zoom avant / arrière |
| **Clic droit** (maintenu) | Déplacer la vue (pan) |
| **Suppr** | Supprimer l'élément sélectionné |
| **Ctrl + C** | Copier la vue dans le presse-papier |
| **Ctrl + S** | Ouvrir la fenêtre d'export |
| **Clic** *(compilation)* | Sélectionner une case |
| **Glisser** *(compilation)* | Repositionner l'image dans sa case |
| **Ctrl + Glisser** *(compilation)* | Intervertir deux cases |

> 💡 Le récapitulatif complet est aussi disponible dans le logiciel, via ⚙ Paramètres.

## 📝 Licence

Projet distribué sous licence **[MIT](LICENSE)**. Utilisation, modification et
redistribution libres.

---

# 🇬🇧 English version

**Comparateur Pro** streamlines comparing multiple images at once, with perfect
zoom and pan synchronization, intelligent auto-alignment and heatmap analysis.
Since version 2.0 it also includes an **image compilation builder**: assemble
grids and boards (gallery covers, before/after sheets…) without any external
editing software.

It is the ideal tool for photographers, designers and anyone who needs precise
visual comparisons or polished image boards.

## ✨ Features

### 🔍 Image comparator
- **Multi-image comparison** — smooth movable sliders to reveal each image.
- **Full synchronization** — zoom (Ctrl + Scroll) and pan (Right-click) applied to all images at once.
- **Blink mode** — hold **Space** to instantly toggle the reference image.
- **Intelligent auto-alignment** — automatically aligns slightly shifted images (2D affine algorithm).
- **Heatmap analysis** — cumulative thermal map to visualize differences.
- **Professional export** — clean 1:1 images (JPEG, PNG, animated GIF) with customizable labels and watermark.
- **Windows context menu** — start a comparison or quick export straight from Explorer.

### 🧩 Image compilation *(new in v2.0)*
- **Grid templates** — 7 built-in layouts (2, 3, 4, 6, 9 cells) + an editor to create and save your own.
- **Drag & drop per cell** — drop each image directly into the cell you want.
- **Output formats** — ready-made presets (covers, 16:9, square, portrait…) or free pixel dimensions, with ratio lock and width/height swap.
- **Image adjustment** — reposition an image within its cell by dragging, zoom with the scroll wheel.
- **Swapping** — exchange two cells with a Ctrl + drag.
- **Optional separator** — bars between cells, adjustable color and thickness.
- **Per-cell labels** — click a label to choose its text: automatic (file name), favorite name or manual input.
- **Automatic export** — clean 1:1 save into your images' folder.

### ⚙️ Comfort & customization
- **Tabbed interface** — smooth switching between Comparator and Compilation.
- **Centralized settings** — ⚙ button always available.
- **Multilingual** — native French and English, automatic system-language detection.
- **Community translation** — export a language file, translate it, import it back.

## 🖼️ Screenshots

<!-- The screenshot placeholders above (French section) are shared. -->
*See the screenshots in the French section above.*

## 🚀 Installation

### 1. Requirements
Make sure **Python 3** is installed, then install the dependencies:

```bash
pip install -r requirements.txt
```

### 2. Run
```bash
python comparateur_app.py
```

### 3. Windows context menu integration *(optional)*
Integration is automated and portable:

1. Double-click **`install_raccourcis.bat`**.
2. The script automatically detects the folder location.
3. Choose the menu language (1 = French, 2 = English).
4. Done. If you move the folder, just run the `.bat` again.

> **Important** — always use `install_raccourcis.bat`, which adapts to the
> real folder location. Do not import a `.reg` file: a `.reg` contains a
> fixed path that will not match your machine.

To remove the menu: double-click **`desinstaller_raccourcis.bat`**.

## ⌨️ Keyboard shortcuts

| Shortcut | Action |
|---|---|
| **Space** (hold) | Blink mode: show reference image |
| **Ctrl + Scroll** | Zoom in / out |
| **Right-click** (hold) | Pan the view |
| **Delete** | Remove the selected item |
| **Ctrl + C** | Copy the view to clipboard |
| **Ctrl + S** | Open the export dialog |
| **Click** *(compilation)* | Select a cell |
| **Drag** *(compilation)* | Reposition the image in its cell |
| **Ctrl + Drag** *(compilation)* | Swap two cells |

> 💡 A full list is also available inside the app, under ⚙ Settings.

## 📝 License

Released under the **[MIT License](LICENSE)**. Free to use, modify and
redistribute.

---

<div align="center">
  <sub>Comparateur Pro — v2.0.0 · Made with Python, PyQt5, OpenCV &amp; Pillow</sub>
</div>

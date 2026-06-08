# -*- coding: utf-8 -*-
"""
================================================================================
 MODULE COMPILATION D'IMAGES  (Image Compilation Module)
================================================================================
Outil additionnel pour "Comparateur Pro".
Permet de creer des compilations / grilles d'images (couvertures CivitAI, etc.)

Fonctionnalites :
 - Gabarits (templates) de grille pre-enregistres + creation/sauvegarde perso
 - Importation des images en glisser-deposer DIRECTEMENT dans une case
 - Format de sortie parametrable : presets ratio (CivitAI, 16:9...) ou pixels libres
   + bouton d'inversion largeur <-> hauteur
 - Ajustement (recadrage) de l'image dans sa case par glisser simple
 - Interversion du contenu de deux cases par Ctrl + glisser
 - Selection d'une case par clic, vidage par touche Suppr
 - Nouvelle planche vierge (vide toutes les cases)
 - Disposition verticale ou horizontale (rotation du gabarit)
 - Separateur facultatif entre les cases (couleur + epaisseur parametrables),
   sans bordure systematique autour des images
 - Etiquette texte par case : on clique sur l'etiquette pour choisir son texte
   (auto nom de fichier / liste de favoris / saisie manuelle)
 - Etiquettes visibles en direct dans l'apercu
 - Export 1:1 propre via QPainter (sans bordure logicielle, sans fond noir)

Ce module est concu pour etre importe par comparateur_app.py SANS modifier
la logique existante. Il reutilise l'objet `config`, la fonction `tr` et le
dictionnaire LANGUAGES du module principal (injection legere ci-dessous).
================================================================================
"""

import os
import json
import copy
import glob
import shutil
import re
import math

from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QSpinBox, QLineEdit,
                             QMessageBox, QFrame, QColorDialog, QCheckBox,
                             QInputDialog, QScrollArea, QSlider, QGridLayout,
                             QSizePolicy, QMenu, QButtonGroup, QRadioButton,
                             QDialogButtonBox, QApplication, QFileDialog,
                             QListWidget, QListWidgetItem)
from PyQt5.QtGui import (QPainter, QPixmap, QColor, QFont, QPen, QFontMetrics,
                         QDrag, QIcon)
from PyQt5.QtCore import (Qt, QRect, QRectF, QPoint, QMimeData, QTimer,
                          QSize, pyqtSignal)


# ==============================================================================
#  INTEGRATION i18n  (textes ajoutes au dictionnaire du module principal)
# ==============================================================================
TEMPLATES_LOAD_WARNING = None
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')

# Cles prefixees "comp_" pour ne pas entrer en collision avec l'existant.
COMPILATION_LANG = {
    "en": {
        "comp_title": "Image Compilation - Grid Builder",
        "comp_open_btn": "🧩 Compilation",
        "comp_templates": "Grid templates",
        "comp_new_template": "+ New template",
        "comp_save_template": "Save current as template",
        "comp_del_template": "Delete template",
        "comp_layout": "Layout",
        "comp_orientation_h": "⬌ Horizontal",
        "comp_orientation_v": "⬍ Vertical",
        "comp_output": "Output format",
        "comp_preset": "Preset:",
        "comp_width": "Width (px):",
        "comp_height": "Height (px):",
        "comp_swap_wh": "⇅ Swap W/H",
        "comp_ratio_lock": "Lock ratio",
        "comp_separator_section": "Separator",
        "comp_separator_enable": "Show separator bars between cells",
        "comp_separator_color": "Separator color:",
        "comp_separator_thickness": "Separator thickness (px):",
        "comp_margin": "Outer margin (px):",
        "comp_bg_color": "Background color:",
        "comp_labels_section": "Text labels",
        "comp_label_enable": "Show labels on cells",
        "comp_label_hint": "Click a label on a cell to set its text.",
        "comp_label_pos": "Default position:",
        "comp_pos_tl": "Top-left",
        "comp_pos_tc": "Top-center",
        "comp_pos_tr": "Top-right",
        "comp_pos_bl": "Bottom-left",
        "comp_pos_bc": "Bottom-center",
        "comp_pos_br": "Bottom-right",
        "comp_label_size": "Text size:",
        "comp_label_txt_color": "Text color:",
        "comp_label_bg_color": "Background color:",
        "comp_label_bg_opacity": "Background opacity:",
        "comp_favorites": "Favorite names",
        "comp_add_fav": "+ Add",
        "comp_del_fav": "- Remove",
        "comp_new_board": "🗋 New blank board",
        "comp_save_project": "💾 Save project",
        "comp_open_project": "📂 Open project",
        "comp_project_saved": "Project saved:\n{path}",
        "comp_project_loaded": "Project loaded successfully.",
        "comp_project_err": "Project error:\n{err}",
        "comp_templates_backup": "Template file was unreadable. A backup was created:\n{path}",
        "comp_missing_image": "Missing image skipped: {path}",
        "comp_export": "Export compilation...",
        "comp_copy": "Copy to clipboard",
        "comp_drop_hint": "Drop an image here",
        "comp_cell": "Cell",
        "comp_export_ok": "Compilation exported:\n{path}",
        "comp_export_err": "Export error:\n{err}",
        "comp_copied": "Compilation copied to clipboard!",
        "comp_no_image": "Please drop at least one image into the grid first.",
        "comp_template_name": "Template name:",
        "comp_confirm_del": "Delete this template?",
        "comp_fav_input": "New favorite name:",
        "comp_template_exists": "A template with this name already exists.",
        "comp_cells_label": "Cells / Layout",
        "comp_preset_free": "Free (custom pixels)",
        "comp_adjust_hint": ("Drag = reposition image  |  Ctrl+Drag = swap two "
                             "cells  |  Click = select, Del = clear"),
        "comp_builtin": "(built-in)",
        "comp_clear_cell": "Clear this cell",
        "comp_new_board_confirm": "Clear all cells and start a new board?",
        "comp_label_dialog_title": "Cell label text",
        "comp_label_mode_auto": "Automatic (file name)",
        "comp_label_mode_fav": "Favorite name:",
        "comp_label_mode_manual": "Manual text:",
        "comp_label_mode_none": "No label on this cell",
        "comp_rows": "Rows:",
        "comp_cols": "Columns:",
        "comp_ok": "OK",
        "comp_cancel": "Cancel",
        "comp_border_section": "Per-image border",
        "comp_border_enable": "Draw a border around each image",
        "comp_border_color": "Border color:",
        "comp_border_thickness": "Border thickness (px):",
        "comp_watermark_section": "Watermark",
        "comp_watermark_enable": "Add a watermark to the compilation",
        "comp_watermark_text": "Watermark text:",
        "comp_watermark_size": "Watermark size:",
        "comp_watermark_opacity": "Watermark opacity:",
        "comp_watermark_pos": "Watermark position:",
        "comp_rotate_cell": "Rotate image in this cell",
        "comp_rotate_left": "↺ Rotate 90° left",
        "comp_rotate_right": "↻ Rotate 90° right",
        "comp_rotate_180": "⟳ Rotate 180°",
        "comp_reset_all_crop": "⌖ Reset crop of all cells",
        "comp_reset_all_done": "The framing of every cell has been reset.",
        "comp_preset_add": "+ Add",
        "comp_preset_edit": "Edit",
        "comp_preset_del": "- Delete",
        "comp_preset_name": "Preset name:",
        "comp_preset_exists": "A preset with this name already exists.",
        "comp_preset_builtin": "Built-in presets cannot be edited or deleted.",
        "comp_preset_confirm_del": "Delete this custom preset?",
        "comp_batch_panel": "Compilation packs",
        "comp_batch_add": "+ Pack",
        "comp_batch_del": "Delete pack",
        "comp_batch_pack_name": "Pack {n}",
        "comp_batch_empty_list": "No pack yet. Click \"+ Pack\" to add one.",
        "comp_batch_generate": "⚙ Generate all boards",
        "comp_batch_rename": "Rename pack",
        "comp_batch_rename_prompt": "Pack name:",
        "comp_batch_duplicate": "Duplicate",
        "comp_batch_clear_images": "Clear images",
        "comp_batch_none": "No pack to generate. Add at least one pack first.",
        "comp_batch_no_image": "Pack \"{name}\" is empty and was skipped.",
        "comp_batch_choose_out": "Choose the output folder for the boards",
        "comp_batch_done": "{count} board(s) generated in:\n{path}",
        "comp_batch_err": "Batch error:\n{err}",
        "comp_batch_skipped": "  ({skipped} empty pack(s) skipped)",
        "comp_batch_drop_created": "{packs} pack(s) created from {images} image(s).",
        "comp_import_mode": "Import mode",
        "comp_import_by_template": "📐 By template",
        "comp_import_dynamic": "🔀 Single board",
        "comp_batch_hint": ("Each pack becomes one board, all sharing the "
                            "current template. Select a pack to edit it, "
                            "drop images into the cells, then generate."),
    },
    "fr": {
        "comp_title": "Compilation d'images - Createur de grille",
        "comp_open_btn": "🧩 Compilation",
        "comp_templates": "Gabarits de grille",
        "comp_new_template": "+ Nouveau gabarit",
        "comp_save_template": "Sauver la grille actuelle",
        "comp_del_template": "Supprimer le gabarit",
        "comp_layout": "Disposition",
        "comp_orientation_h": "⬌ Horizontal",
        "comp_orientation_v": "⬍ Vertical",
        "comp_output": "Format de sortie",
        "comp_preset": "Preset :",
        "comp_width": "Largeur (px) :",
        "comp_height": "Hauteur (px) :",
        "comp_swap_wh": "⇅ Inverser L/H",
        "comp_ratio_lock": "Verrouiller le ratio",
        "comp_separator_section": "Separateur",
        "comp_separator_enable": "Afficher des barres separatrices entre les cases",
        "comp_separator_color": "Couleur du separateur :",
        "comp_separator_thickness": "Epaisseur du separateur (px) :",
        "comp_margin": "Marge exterieure (px) :",
        "comp_bg_color": "Couleur de fond :",
        "comp_labels_section": "Etiquettes texte",
        "comp_label_enable": "Afficher les etiquettes sur les cases",
        "comp_label_hint": "Cliquez sur l'etiquette d'une case pour saisir son texte.",
        "comp_label_pos": "Position par defaut :",
        "comp_pos_tl": "Haut-gauche",
        "comp_pos_tc": "Haut-centre",
        "comp_pos_tr": "Haut-droite",
        "comp_pos_bl": "Bas-gauche",
        "comp_pos_bc": "Bas-centre",
        "comp_pos_br": "Bas-droite",
        "comp_label_size": "Taille du texte :",
        "comp_label_txt_color": "Couleur du texte :",
        "comp_label_bg_color": "Couleur du fond :",
        "comp_label_bg_opacity": "Opacite du fond :",
        "comp_favorites": "Noms favoris",
        "comp_add_fav": "+ Ajouter",
        "comp_del_fav": "- Retirer",
        "comp_new_board": "🗋 Nouvelle planche vierge",
        "comp_save_project": "💾 Enregistrer le projet",
        "comp_open_project": "📂 Ouvrir un projet",
        "comp_project_saved": "Projet enregistre :\n{path}",
        "comp_project_loaded": "Projet charge avec succes.",
        "comp_project_err": "Erreur de projet :\n{err}",
        "comp_templates_backup": "Le fichier de gabarits etait illisible. Une sauvegarde a ete creee :\n{path}",
        "comp_missing_image": "Image introuvable ignoree : {path}",
        "comp_export": "Exporter la compilation...",
        "comp_copy": "Copier dans le presse-papier",
        "comp_drop_hint": "Deposez une image ici",
        "comp_cell": "Case",
        "comp_export_ok": "Compilation exportee :\n{path}",
        "comp_export_err": "Erreur d'export :\n{err}",
        "comp_copied": "Compilation copiee dans le presse-papier !",
        "comp_no_image": "Veuillez d'abord deposer au moins une image dans la grille.",
        "comp_template_name": "Nom du gabarit :",
        "comp_confirm_del": "Supprimer ce gabarit ?",
        "comp_fav_input": "Nouveau nom favori :",
        "comp_template_exists": "Un gabarit portant ce nom existe deja.",
        "comp_cells_label": "Cases / Disposition",
        "comp_preset_free": "Libre (pixels personnalises)",
        "comp_adjust_hint": ("Glisser = repositionner l'image  |  Ctrl+Glisser = "
                             "intervertir deux cases  |  Clic = selectionner, "
                             "Suppr = vider"),
        "comp_builtin": "(integre)",
        "comp_clear_cell": "Vider cette case",
        "comp_new_board_confirm": "Vider toutes les cases et commencer une nouvelle planche ?",
        "comp_label_dialog_title": "Texte de l'etiquette",
        "comp_label_mode_auto": "Automatique (nom du fichier)",
        "comp_label_mode_fav": "Nom favori :",
        "comp_label_mode_manual": "Texte manuel :",
        "comp_label_mode_none": "Aucune etiquette sur cette case",
        "comp_rows": "Lignes :",
        "comp_cols": "Colonnes :",
        "comp_ok": "OK",
        "comp_cancel": "Annuler",
        "comp_border_section": "Bordure par image",
        "comp_border_enable": "Dessiner une bordure autour de chaque image",
        "comp_border_color": "Couleur de la bordure :",
        "comp_border_thickness": "Epaisseur de la bordure (px) :",
        "comp_watermark_section": "Filigrane",
        "comp_watermark_enable": "Ajouter un filigrane a la compilation",
        "comp_watermark_text": "Texte du filigrane :",
        "comp_watermark_size": "Taille du filigrane :",
        "comp_watermark_opacity": "Opacite du filigrane :",
        "comp_watermark_pos": "Position du filigrane :",
        "comp_rotate_cell": "Pivoter l'image de cette case",
        "comp_rotate_left": "↺ Pivoter 90° a gauche",
        "comp_rotate_right": "↻ Pivoter 90° a droite",
        "comp_rotate_180": "⟳ Pivoter 180°",
        "comp_reset_all_crop": "⌖ Reinitialiser le cadrage de toutes les cases",
        "comp_reset_all_done": "Le cadrage de toutes les cases a ete reinitialise.",
        "comp_preset_add": "+ Ajouter",
        "comp_preset_edit": "Modifier",
        "comp_preset_del": "- Supprimer",
        "comp_preset_name": "Nom du preset :",
        "comp_preset_exists": "Un preset portant ce nom existe deja.",
        "comp_preset_builtin": "Les presets fournis ne peuvent etre ni modifies ni supprimes.",
        "comp_preset_confirm_del": "Supprimer ce preset personnalise ?",
        "comp_batch_panel": "Packs de compilation",
        "comp_batch_add": "+ Pack",
        "comp_batch_del": "Supprimer le pack",
        "comp_batch_pack_name": "Pack {n}",
        "comp_batch_empty_list": "Aucun pack. Cliquez sur \"+ Pack\" pour en ajouter.",
        "comp_batch_generate": "⚙ Generer toutes les planches",
        "comp_batch_rename": "Renommer le pack",
        "comp_batch_rename_prompt": "Nom du pack :",
        "comp_batch_duplicate": "Dupliquer",
        "comp_batch_clear_images": "Vider les images",
        "comp_batch_none": "Aucun pack a generer. Ajoutez d'abord au moins un pack.",
        "comp_batch_no_image": "Le pack \"{name}\" est vide et a ete ignore.",
        "comp_batch_choose_out": "Choisir le dossier de sortie des planches",
        "comp_batch_done": "{count} planche(s) generee(s) dans :\n{path}",
        "comp_batch_err": "Erreur du traitement par lot :\n{err}",
        "comp_batch_skipped": "  ({skipped} pack(s) vide(s) ignore(s))",
        "comp_batch_drop_created": "{packs} pack(s) cree(s) depuis {images} image(s).",
        "comp_import_mode": "Mode d'import",
        "comp_import_by_template": "📐 Par gabarit",
        "comp_import_dynamic": "🔀 Planche unique",
        "comp_batch_hint": ("Chaque pack devient une planche, tous partageant "
                            "le gabarit actuel. Selectionnez un pack pour "
                            "l'editer, deposez les images dans les cases, "
                            "puis generez."),
    }
}


# ==============================================================================
#  GABARITS PAR DEFAUT (built-in)
# ==============================================================================
DEFAULT_TEMPLATES = [
    {"name": "2 images (cote a cote)", "rows": 1, "cols": 2, "builtin": True},
    {"name": "2 images (empilees)",    "rows": 2, "cols": 1, "builtin": True},
    {"name": "3 images (bande)",       "rows": 1, "cols": 3, "builtin": True},
    {"name": "4 images (2x2)",         "rows": 2, "cols": 2, "builtin": True},
    {"name": "6 images (3x2)",         "rows": 2, "cols": 3, "builtin": True},
    {"name": "6 images (2x3)",         "rows": 3, "cols": 2, "builtin": True},
    {"name": "9 images (3x3)",         "rows": 3, "cols": 3, "builtin": True},
]

# Presets de format de sortie (largeur, hauteur en pixels).
OUTPUT_PRESETS = [
    {"name": "CivitAI couverture (1600x900)", "w": 1600, "h": 900},
    {"name": "CivitAI large (1920x1080)",     "w": 1920, "h": 1080},
    {"name": "Carre (1080x1080)",             "w": 1080, "h": 1080},
    {"name": "Carre HD (2048x2048)",          "w": 2048, "h": 2048},
    {"name": "16:9 (1280x720)",               "w": 1280, "h": 720},
    {"name": "4:3 (1280x960)",                "w": 1280, "h": 960},
    {"name": "3:2 (1500x1000)",               "w": 1500, "h": 1000},
    {"name": "Portrait 9:16 (1080x1920)",     "w": 1080, "h": 1920},
    {"name": "Portrait 2:3 (1000x1500)",      "w": 1000, "h": 1500},
]

POSITIONS = ["tl", "tc", "tr", "bl", "bc", "br"]

# Type MIME pour l'interversion de cases (drag interne).
MIME_CELL_SWAP = "application/x-comparateur-cell-index"

# ==============================================================================
#  PALETTE DU THEME "MIDNIGHT BLUE"  (sombre bleute + accent orange)
# ==============================================================================
# Centralisee ici pour rester coherent avec le STYLE_SHEET du module principal.
COL_FOND = "#0f1623"          # fond le plus sombre
COL_PANNEAU = "#161f2e"       # panneaux / sidebar
COL_CASE_VIDE = "#1d2839"     # case vide de la grille
COL_BORDURE = "#34425a"       # bordures discretes
COL_ACCENT = "#ff8c42"        # accent orange (selection, hover, titres)
COL_TITRE = "#ff8c42"         # titres de section
COL_TEXTE = "#e8edf4"         # texte clair
COL_TEXTE_DOUX = "#8b97a8"    # texte secondaire


# ==============================================================================
#  POINT D'INJECTION  (rempli par comparateur_app.py au moment de l'import)
# ==============================================================================
_CTX = {"config": None, "tr": None}


def init_compilation(config_obj, tr_func, languages_dict):
    """Injecte le contexte du module principal et fusionne les traductions."""
    _CTX["config"] = config_obj
    _CTX["tr"] = tr_func
    for lang_code, entries in COMPILATION_LANG.items():
        if lang_code in languages_dict:
            # Ne pas ecraser une traduction communautaire deja chargee.
            for k, v in entries.items():
                languages_dict[lang_code].setdefault(k, v)
        else:
            languages_dict[lang_code] = dict(entries)


def _cfg():
    return _CTX["config"]


def ct(key, **kwargs):
    """Traduction locale au module (delegue a tr du module principal)."""
    tr_func = _CTX["tr"]
    if tr_func is not None:
        return tr_func(key, **kwargs)
    txt = COMPILATION_LANG["fr"].get(key, key)
    return txt.format(**kwargs) if kwargs else txt


# ==============================================================================
#  PERSISTANCE DES GABARITS ET FAVORIS
# ==============================================================================
def _templates_file():
    """Fichier JSON des gabarits, range a cote du script principal."""
    import sys
    base = None
    try:
        main_mod = sys.modules.get("__main__")
        if main_mod is not None and getattr(main_mod, "__file__", None):
            base = os.path.dirname(os.path.abspath(main_mod.__file__))
    except Exception:
        base = None
    if not base:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "compilation_templates.json")


def charger_gabarits():
    """Retourne (templates, favoris, presets_perso). Built-in toujours en
    tete pour les gabarits."""
    global TEMPLATES_LOAD_WARNING
    chemin = _templates_file()
    templates = [copy.deepcopy(t) for t in DEFAULT_TEMPLATES]
    favoris = []
    presets_perso = []
    if os.path.exists(chemin):
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
            for t in data.get("templates", []):
                t["builtin"] = False
                templates.append(t)
            favoris = data.get("favoris", [])
            # Presets de format personnalises (au-dela des presets fournis).
            for p in data.get("presets", []):
                if "name" in p and "w" in p and "h" in p:
                    presets_perso.append({"name": p["name"],
                                          "w": int(p["w"]),
                                          "h": int(p["h"]),
                                          "builtin": False})
        except Exception:
            try:
                bak = chemin + ".bak"
                if os.path.exists(bak):
                    import time
                    bak = chemin + "." + time.strftime("%Y%m%d_%H%M%S") + ".bak"
                shutil.copy2(chemin, bak)
                TEMPLATES_LOAD_WARNING = bak
            except Exception:
                TEMPLATES_LOAD_WARNING = chemin
    return templates, favoris, presets_perso


def sauver_gabarits(templates, favoris, presets_perso=None):
    """Sauve les gabarits non built-in, les favoris et les presets perso."""
    chemin = _templates_file()
    perso = [t for t in templates if not t.get("builtin", False)]
    data = {"templates": perso, "favoris": favoris}
    if presets_perso is not None:
        data["presets"] = [{"name": p["name"], "w": p["w"], "h": p["h"]}
                           for p in presets_perso
                           if not p.get("builtin", False)]
    try:
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


# ==============================================================================
#  FONCTIONS DE RENDU PARTAGEES  (apercu ET export utilisent la meme logique)
# ==============================================================================
def _pixmap_pivote(pixmap, rotation):
    """Retourne le pixmap pivote de `rotation` degres (0/90/180/270).
    Pour 0 degre, renvoie le pixmap d'origine sans copie."""
    rotation = int(rotation) % 360
    if rotation == 0 or pixmap is None or pixmap.isNull():
        return pixmap
    from PyQt5.QtGui import QTransform
    return pixmap.transformed(QTransform().rotate(rotation),
                              Qt.SmoothTransformation)


def peindre_image_dans_rect(painter, pixmap, rect, offset_x, offset_y,
                            cell_zoom=1.0, rotation=0):
    """Dessine `pixmap` dans `rect` (QRectF) en mode "cover" : l'image
    couvre toute la case. offset_x/offset_y (0..1) deplacent la portion
    visible, cell_zoom agrandit l'image dans la case, rotation (0/90/180/270)
    pivote l'image avant le calcul de couverture."""
    if pixmap is None or pixmap.isNull() or rect.width() <= 0 or rect.height() <= 0:
        return
    # Rotation appliquee en amont : le reste du calcul reste identique.
    pixmap = _pixmap_pivote(pixmap, rotation)
    if pixmap is None or pixmap.isNull():
        return
    img_w = pixmap.width()
    img_h = pixmap.height()
    cell_w = rect.width()
    cell_h = rect.height()

    painter.save()
    painter.setClipRect(rect)
    echelle = max(cell_w / img_w, cell_h / img_h) * cell_zoom
    draw_w = img_w * echelle
    draw_h = img_h * echelle
    libre_x = draw_w - cell_w
    libre_y = draw_h - cell_h
    x = rect.x() - libre_x * offset_x
    y = rect.y() - libre_y * offset_y
    painter.drawPixmap(QRectF(x, y, draw_w, draw_h), pixmap,
                       QRectF(0, 0, img_w, img_h))
    painter.restore()


def dessiner_bordure_image(painter, rect, couleur, epaisseur):
    """Dessine une bordure interieure autour d'une case image (QRectF).
    Le trait est dessine vers l'interieur du rectangle pour ne pas
    deborder sur les cases voisines."""
    if epaisseur <= 0:
        return
    painter.save()
    stylo = QPen(QColor(couleur))
    stylo.setWidth(int(epaisseur))
    stylo.setJoinStyle(Qt.MiterJoin)
    painter.setPen(stylo)
    painter.setBrush(Qt.NoBrush)
    demi = epaisseur / 2.0
    painter.drawRect(QRectF(rect.x() + demi, rect.y() + demi,
                            rect.width() - epaisseur,
                            rect.height() - epaisseur))
    painter.restore()


def dessiner_filigrane(painter, rect, texte, position, taille_pt,
                       opacite, echelle=1.0):
    """Dessine un filigrane texte sur l'ensemble de la compilation.
    `rect` est la zone de rendu complete (QRectF), `echelle` agrandit
    le texte pour l'export haute resolution."""
    if not texte:
        return
    painter.save()
    pt = max(8, int(taille_pt * echelle))
    font = QFont("Segoe UI", pt, QFont.Bold)
    painter.setFont(font)
    fm = QFontMetrics(font)
    larg = fm.horizontalAdvance(texte)
    haut = fm.height()
    marge = max(6, int(18 * echelle))

    if position in ("tl", "bl"):
        tx = rect.x() + marge
    elif position in ("tr", "br"):
        tx = rect.x() + rect.width() - larg - marge
    else:
        tx = rect.x() + (rect.width() - larg) / 2

    if position in ("tl", "tc", "tr"):
        ty = rect.y() + marge
    else:
        ty = rect.y() + rect.height() - haut - marge

    zone_txt = QRectF(tx, ty, larg, haut)
    # Ombre legere pour la lisibilite sur fond clair comme fond sombre.
    painter.setPen(QColor(0, 0, 0, min(255, int(opacite))))
    painter.drawText(zone_txt.translated(max(1, echelle), max(1, echelle)),
                     Qt.AlignLeft | Qt.AlignVCenter, texte)
    painter.setPen(QColor(255, 255, 255, min(255, int(opacite))))
    painter.drawText(zone_txt, Qt.AlignLeft | Qt.AlignVCenter, texte)
    painter.restore()


def dessiner_label(painter, rect, texte, position, taille_pt, couleur_texte,
                   couleur_fond, opacite_fond, echelle=1.0):
    """Dessine une etiquette texte avec fond dans `rect` (QRectF).
    `echelle` agrandit le label pour l'export haute resolution."""
    if not texte:
        return
    painter.save()
    painter.setClipRect(rect)

    badge, zone_txt, font, fm = _calc_rect_label(
        rect, position, taille_pt, texte, echelle)
    painter.setFont(font)

    c_fond = QColor(couleur_fond)
    c_fond.setAlpha(int(opacite_fond))
    painter.setPen(Qt.NoPen)
    painter.setBrush(c_fond)
    rayon = max(2, int(6 * echelle))
    painter.drawRoundedRect(badge, rayon, rayon)

    painter.setPen(QColor(couleur_texte))
    ty = zone_txt.y()
    for ligne in texte.split("\n"):
        rect_ligne = QRectF(zone_txt.x(), ty, zone_txt.width(), fm.height())
        if position in ("tc", "bc"):
            align = Qt.AlignHCenter
        elif position in ("tr", "br"):
            align = Qt.AlignRight
        else:
            align = Qt.AlignLeft
        painter.drawText(rect_ligne, align | Qt.AlignVCenter, ligne)
        ty += fm.height()

    painter.restore()


def _calc_rect_label(rect, position, taille_pt, texte, echelle=1.0):
    """Calcule le rectangle reel du badge d'etiquette et sa zone texte."""
    rect = QRectF(rect)
    pt = max(6, int(taille_pt * echelle))
    font = QFont("Segoe UI", pt, QFont.Bold)
    fm = QFontMetrics(font)
    marge = max(2, int(8 * echelle))
    pad_x = max(3, int(10 * echelle))
    pad_y = max(2, int(6 * echelle))

    lignes = texte.split("\n") if texte else [""]
    larg_txt = max(fm.horizontalAdvance(l) for l in lignes)
    haut_txt = fm.height() * len(lignes)
    bg_w = larg_txt + pad_x * 2
    bg_h = haut_txt + pad_y * 2

    if position in ("tl", "bl"):
        bx = rect.x() + marge
    elif position in ("tr", "br"):
        bx = rect.x() + rect.width() - bg_w - marge
    else:
        bx = rect.x() + (rect.width() - bg_w) / 2

    if position in ("tl", "tc", "tr"):
        by = rect.y() + marge
    else:
        by = rect.y() + rect.height() - bg_h - marge

    badge = QRectF(bx, by, bg_w, bg_h)
    zone_txt = QRectF(bx + pad_x, by + pad_y, larg_txt, haut_txt)
    return badge, zone_txt, font, fm


def _resoudre_texte_label(cell):
    """Determine le texte d'etiquette d'une case selon son mode propre."""
    mode = cell.label_mode
    if mode == "none":
        return ""
    if mode == "auto":
        if cell.chemin:
            return os.path.splitext(os.path.basename(cell.chemin))[0]
        return ""
    if mode == "fav":
        return cell.label_text or ""
    if mode == "manual":
        return cell.label_text or ""
    return ""


def _cle_tri_naturel(chemin):
    """Tri lisible des chemins contenant des nombres."""
    morceaux = re.split(r"(\d+)", chemin.lower())
    return [int(m) if m.isdigit() else m for m in morceaux]


class VoletPacksCompilation(QFrame):
    """QFrame acceptant le drop d'images pour creer des packs."""
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        self.owner._drag_packs_enter(event)

    def dragMoveEvent(self, event):
        self.owner._drag_packs_enter(event)

    def dropEvent(self, event):
        self.owner._drop_images_packs(event)


class ListePacksCompilation(QListWidget):
    """Liste de packs acceptant le meme drop que le volet."""
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        self.owner._drag_packs_enter(event)

    def dragMoveEvent(self, event):
        self.owner._drag_packs_enter(event)

    def dropEvent(self, event):
        self.owner._drop_images_packs(event)


# ==============================================================================
#  DIALOGUE : CHOIX DU TEXTE D'ETIQUETTE D'UNE CASE
# ==============================================================================
class DialogueLabelCase(QDialog):
    """Petite fenetre pour choisir le texte de l'etiquette d'une case :
    automatique (nom de fichier) / nom favori / texte manuel / aucune."""

    def __init__(self, cell, favoris, parent=None):
        super().__init__(parent)
        self.setWindowTitle(ct("comp_label_dialog_title"))
        self.setMinimumWidth(340)
        self.cell = cell
        self.favoris = favoris

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.groupe = QButtonGroup(self)

        # Mode automatique.
        self.rb_auto = QRadioButton(ct("comp_label_mode_auto"))
        self.groupe.addButton(self.rb_auto)
        layout.addWidget(self.rb_auto)

        # Mode favori.
        h_fav = QHBoxLayout()
        self.rb_fav = QRadioButton(ct("comp_label_mode_fav"))
        self.groupe.addButton(self.rb_fav)
        self.combo_fav = QComboBox()
        for f in favoris:
            self.combo_fav.addItem(f)
        h_fav.addWidget(self.rb_fav)
        h_fav.addWidget(self.combo_fav, 1)
        layout.addLayout(h_fav)

        # Mode manuel.
        h_man = QHBoxLayout()
        self.rb_manual = QRadioButton(ct("comp_label_mode_manual"))
        self.groupe.addButton(self.rb_manual)
        self.edit_manual = QLineEdit()
        h_man.addWidget(self.rb_manual)
        h_man.addWidget(self.edit_manual, 1)
        layout.addLayout(h_man)

        # Mode aucune etiquette.
        self.rb_none = QRadioButton(ct("comp_label_mode_none"))
        self.groupe.addButton(self.rb_none)
        layout.addWidget(self.rb_none)

        # Pre-selection selon l'etat actuel de la case.
        if cell.label_mode == "auto":
            self.rb_auto.setChecked(True)
        elif cell.label_mode == "fav":
            self.rb_fav.setChecked(True)
            idx = self.combo_fav.findText(cell.label_text)
            if idx >= 0:
                self.combo_fav.setCurrentIndex(idx)
        elif cell.label_mode == "manual":
            self.rb_manual.setChecked(True)
            self.edit_manual.setText(cell.label_text)
        else:
            self.rb_none.setChecked(True)

        # Si pas de favoris, le mode favori est desactive.
        if not favoris:
            self.rb_fav.setEnabled(False)
            self.combo_fav.setEnabled(False)

        layout.addSpacing(8)
        boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        boutons.button(QDialogButtonBox.Ok).setText(ct("comp_ok"))
        boutons.button(QDialogButtonBox.Cancel).setText(ct("comp_cancel"))
        boutons.accepted.connect(self.accept)
        boutons.rejected.connect(self.reject)
        layout.addWidget(boutons)

    def resultat(self):
        """Retourne (mode, texte) a appliquer a la case."""
        if self.rb_auto.isChecked():
            return "auto", ""
        if self.rb_fav.isChecked():
            return "fav", self.combo_fav.currentText()
        if self.rb_manual.isChecked():
            return "manual", self.edit_manual.text()
        return "none", ""


# ==============================================================================
#  WIDGET : UNE CASE DE LA GRILLE
# ==============================================================================
class CelluleImage(QWidget):
    """
    Une case du gabarit.
     - Glisser-deposer d'un fichier image depuis l'exterieur => place l'image.
     - Glisser simple a la souris => repositionne l'image dans la case.
     - Ctrl + glisser => intervertit le contenu avec une autre case.
     - Clic simple => selectionne la case (cadre bleu) ; Suppr la vide.
     - Molette => zoom de l'image dans la case.
     - Clic sur la zone d'etiquette => ouvre le choix du texte d'etiquette.
    """
    image_changee = pyqtSignal()
    selection_demandee = pyqtSignal(int)      # index de la case selectionnee
    label_clic = pyqtSignal(int)              # index : on veut editer le label
    swap_demande = pyqtSignal(int, int)       # (source, destination)
    ajustement_termine = pyqtSignal()         # fin d'un recadrage/zoom de case

    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.chemin = None
        self.pixmap = None
        self.offset_x = 0.5
        self.offset_y = 0.5
        self.cell_zoom = 1.0
        self.rotation = 0           # rotation de l'image dans la case (0/90/180/270)
        # Etiquette propre a la case.
        self.label_mode = "auto"     # auto / fav / manual / none
        self.label_text = ""         # texte pour fav / manual
        # Fonction fournie par le widget parent : retourne le dict de style
        # d'etiquette courant (position, taille, couleurs, opacite, enabled).
        # Permet a la cellule de dessiner SON propre label par-dessus l'image,
        # donc visible en permanence dans l'apercu.
        self.fournisseur_style_label = None
        # Fournisseur du style de bordure par image (defini par WidgetCompilation).
        self.fournisseur_style_bordure = None
        # Etat d'interaction.
        self.selectionnee = False
        self._drag_souris = False
        self._last_pos = None
        self._press_pos = None
        self._ctrl_drag = False
        self._hover_fichier = False
        # Timer de regroupement : un enchainement de crans de molette ne
        # genere qu'un seul point d'annulation, declenche 400 ms apres le
        # dernier cran.
        self._timer_zoom = QTimer(self)
        self._timer_zoom.setSingleShot(True)
        self._timer_zoom.setInterval(400)
        self._timer_zoom.timeout.connect(self.ajustement_termine.emit)
        self.setAcceptDrops(True)
        self.setMinimumSize(50, 50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)

    # --- Donnees ---
    def definir_image(self, chemin):
        pix = QPixmap(chemin)
        if pix.isNull():
            return False
        self.chemin = chemin
        self.pixmap = pix
        self.offset_x = 0.5
        self.offset_y = 0.5
        self.cell_zoom = 1.0
        self.rotation = 0
        self.update()
        self.image_changee.emit()
        return True

    def vider(self):
        self.chemin = None
        self.pixmap = None
        self.offset_x = 0.5
        self.offset_y = 0.5
        self.cell_zoom = 1.0
        self.rotation = 0
        self.label_mode = "auto"
        self.label_text = ""
        self.update()
        self.image_changee.emit()

    def etat_serialisable(self):
        """Retourne l'etat de la case (pour reconstruire la grille / swap)."""
        return {
            "chemin": self.chemin, "pixmap": self.pixmap,
            "offset_x": self.offset_x, "offset_y": self.offset_y,
            "cell_zoom": self.cell_zoom, "rotation": self.rotation,
            "label_mode": self.label_mode, "label_text": self.label_text,
        }

    def restaurer_etat(self, etat):
        """Restaure l'etat. Reutilise le pixmap si fourni (evite de relire
        le fichier disque lors d'une interversion)."""
        self.chemin = etat.get("chemin")
        pix = etat.get("pixmap")
        if pix is None and self.chemin:
            pix = QPixmap(self.chemin)
            if pix.isNull():
                pix = None
        self.pixmap = pix
        self.offset_x = etat.get("offset_x", 0.5)
        self.offset_y = etat.get("offset_y", 0.5)
        self.cell_zoom = etat.get("cell_zoom", 1.0)
        self.rotation = int(etat.get("rotation", 0)) % 360
        self.label_mode = etat.get("label_mode", "auto")
        self.label_text = etat.get("label_text", "")
        self.update()

    # --- Glisser-deposer d'un fichier image depuis l'exterieur ---
    def dragEnterEvent(self, event):
        md = event.mimeData()
        # Interversion interne : un autre CelluleImage glisse vers ici.
        if md.hasFormat(MIME_CELL_SWAP):
            event.acceptProposedAction()
            self._hover_fichier = True
            self.update()
            return
        if md.hasUrls():
            for u in md.urls():
                if u.toLocalFile().lower().endswith(
                        ('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    event.acceptProposedAction()
                    self._hover_fichier = True
                    self.update()
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self._hover_fichier = False
        self.update()

    def dropEvent(self, event):
        self._hover_fichier = False
        md = event.mimeData()
        # Interversion interne.
        if md.hasFormat(MIME_CELL_SWAP):
            try:
                src = int(bytes(md.data(MIME_CELL_SWAP)).decode("ascii"))
            except Exception:
                src = -1
            if src >= 0 and src != self.index:
                self.swap_demande.emit(src, self.index)
            event.acceptProposedAction()
            self.update()
            return
        # Import d'un fichier image.
        for u in md.urls():
            chemin = u.toLocalFile()
            if chemin.lower().endswith(IMAGE_EXTENSIONS):
                self.definir_image(chemin)
                break
        self.update()

    # --- Zone cliquable de l'etiquette ---
    def _rect_etiquette(self):
        """Zone cliquable reelle du badge d'etiquette."""
        style = None
        if self.fournisseur_style_label is not None:
            try:
                style = self.fournisseur_style_label()
            except Exception:
                style = None
        texte = _resoudre_texte_label(self)
        if style and style.get("enabled") and texte:
            badge, _, _, _ = _calc_rect_label(
                QRectF(0, 0, self.width(), self.height()),
                style.get("position", "bl"),
                style.get("size", 16),
                texte,
                echelle=1.0)
            return badge.toAlignedRect()
        h = max(22, int(self.height() * 0.18))
        return QRect(0, self.height() - h, self.width(), h)

    # --- Souris ---
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        # Clic sur la zone d'etiquette => edition du texte d'etiquette.
        if self._rect_etiquette().contains(event.pos()):
            self.label_clic.emit(self.index)
            return
        # Selection de la case.
        self.selection_demandee.emit(self.index)
        self._press_pos = event.pos()
        self._last_pos = event.pos()
        self._ctrl_drag = bool(event.modifiers() & Qt.ControlModifier)
        # Glisser simple (ajustement) seulement si une image est presente.
        if self.pixmap is not None and not self._ctrl_drag:
            self._drag_souris = True
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        # Ctrl + glisser : on lance un drag d'interversion des qu'on bouge.
        if self._ctrl_drag and self.pixmap is not None and self._press_pos is not None:
            if (event.pos() - self._press_pos).manhattanLength() > 8:
                self._lancer_drag_swap()
                self._ctrl_drag = False
            return
        # Glisser simple : repositionnement de l'image.
        if self._drag_souris and self.pixmap is not None and self._last_pos is not None:
            delta = event.pos() - self._last_pos
            self._last_pos = event.pos()
            if self.width() > 0 and self.height() > 0:
                self.offset_x -= delta.x() / max(1, self.width())
                self.offset_y -= delta.y() / max(1, self.height())
                self.offset_x = min(1.0, max(0.0, self.offset_x))
                self.offset_y = min(1.0, max(0.0, self.offset_y))
                self.update()
            return
        # Curseur indicatif.
        if self._rect_etiquette().contains(event.pos()):
            self.setCursor(Qt.PointingHandCursor)
        elif self.pixmap is not None:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            etait_drag = self._drag_souris
            self._drag_souris = False
            self._ctrl_drag = False
            self._press_pos = None
            if self.pixmap is not None:
                self.setCursor(Qt.OpenHandCursor)
            # Fin d'un glisser de repositionnement : point d'annulation.
            if etait_drag:
                self.ajustement_termine.emit()

    def _lancer_drag_swap(self):
        """Demarre un glisser interne pour intervertir avec une autre case."""
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(MIME_CELL_SWAP, str(self.index).encode("ascii"))
        drag.setMimeData(mime)
        if self.pixmap is not None:
            apercu = self.pixmap.scaled(120, 120, Qt.KeepAspectRatio,
                                        Qt.SmoothTransformation)
            drag.setPixmap(apercu)
        drag.exec_(Qt.MoveAction)

    def wheelEvent(self, event):
        """Molette = zoom de l'image dans la case."""
        if self.pixmap is None:
            return
        pas = 1.1 if event.angleDelta().y() > 0 else (1 / 1.1)
        self.cell_zoom = min(5.0, max(1.0, self.cell_zoom * pas))
        self.update()
        # Regroupe les crans de molette : un seul point d'annulation 400 ms
        # apres le dernier cran.
        self._timer_zoom.start()

    def pivoter(self, delta):
        """Pivote l'image de la case de `delta` degres (multiple de 90)."""
        if self.pixmap is None:
            return
        self.rotation = (self.rotation + int(delta)) % 360
        self.update()
        # Une rotation est une modification de la planche : point d'annulation.
        self.ajustement_termine.emit()

    def contextMenuEvent(self, event):
        if self.pixmap is None:
            return
        menu = QMenu(self)
        sous_menu = menu.addMenu(ct("comp_rotate_cell"))
        act_left = sous_menu.addAction(ct("comp_rotate_left"))
        act_right = sous_menu.addAction(ct("comp_rotate_right"))
        act_180 = sous_menu.addAction(ct("comp_rotate_180"))
        menu.addSeparator()
        act_clear = menu.addAction(ct("comp_clear_cell"))
        action = menu.exec_(event.globalPos())
        if action == act_clear:
            self.vider()
        elif action == act_left:
            self.pivoter(-90)
        elif action == act_right:
            self.pivoter(90)
        elif action == act_180:
            self.pivoter(180)

    # --- Rendu de l'apercu de la case (sans bordure systematique) ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        rect = self.rect()

        if self.pixmap is None:
            # Case vide : zone discrete en pointilles.
            painter.fillRect(rect, QColor(COL_CASE_VIDE))
            pen = QPen(QColor(COL_ACCENT) if self._hover_fichier
                       else QColor(COL_BORDURE))
            pen.setStyle(Qt.DashLine)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(2, 2, -3, -3))
            painter.setPen(QColor(COL_TEXTE_DOUX))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(rect, Qt.AlignCenter,
                             "%s %d\n%s" % (ct("comp_cell"), self.index + 1,
                                            ct("comp_drop_hint")))
        else:
            # Case remplie : image en mode cover, AUCUNE bordure systematique.
            peindre_image_dans_rect(painter, self.pixmap, QRectF(rect),
                                    self.offset_x, self.offset_y,
                                    self.cell_zoom, self.rotation)
            # Bordure facultative par image (style fourni par le widget parent).
            style_b = None
            if self.fournisseur_style_bordure is not None:
                try:
                    style_b = self.fournisseur_style_bordure()
                except Exception:
                    style_b = None
            if style_b and style_b.get("enabled"):
                dessiner_bordure_image(painter, QRectF(rect),
                                       style_b.get("color", "#ffffff"),
                                       style_b.get("thickness", 4))

        # Etiquette : dessinee ICI, sur la cellule (widget le plus en avant),
        # donc toujours visible dans l'apercu en temps reel.
        style = None
        if self.fournisseur_style_label is not None:
            try:
                style = self.fournisseur_style_label()
            except Exception:
                style = None
        if style and style.get("enabled"):
            texte = _resoudre_texte_label(self)
            if texte:
                dessiner_label(painter, QRectF(rect), texte,
                               style.get("position", "bl"),
                               style.get("size", 16),
                               style.get("text_color", "#ffffff"),
                               style.get("bg_color", "#000000"),
                               style.get("bg_opacity", 150),
                               echelle=1.0)

        # Surbrillance si la case recoit un glisser de fichier.
        if self._hover_fichier:
            painter.setPen(QPen(QColor(COL_ACCENT), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect.adjusted(1, 1, -2, -2))

        # Cadre de selection (uniquement quand la case est selectionnee).
        if self.selectionnee:
            painter.setPen(QPen(QColor(COL_ACCENT), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect.adjusted(1, 1, -2, -2))

        painter.end()


# ==============================================================================
#  WIDGET : ZONE DE GRILLE
# ==============================================================================
class GrilleCompilation(QWidget):
    """Conteneur visuel de la grille. Recalcule la disposition des cellules
    et dessine le fond + le separateur facultatif entre les cases."""
    grille_modifiee = pyqtSignal()
    cellule_selectionnee = pyqtSignal(int)
    label_a_editer = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cellules = []
        self.rows = 2
        self.cols = 2
        self.margin = 12               # marge exterieure (apercu, px)
        self.bg_color = COL_FOND
        self.ratio = 16 / 9
        # Separateur facultatif entre les cases.
        self.separateur_actif = True
        self.separateur_couleur = "#ffffff"
        self.separateur_epaisseur = 6  # px (a l'echelle de l'apercu)
        # Fournisseur du style d'etiquette (defini par WidgetCompilation).
        # Chaque cellule l'utilise pour dessiner son label en direct.
        self.fournisseur_style_label = None
        # Fournisseur du style de bordure par image.
        self.fournisseur_style_bordure = None
        # Fournisseur du style de filigrane global (dessine dans l'apercu).
        self.fournisseur_style_filigrane = None
        self._index_selection = -1
        self.setMinimumSize(200, 150)
        self.appliquer_gabarit(2, 2)

    def appliquer_gabarit(self, rows, cols):
        """Reconstruit la grille en conservant le contenu des cases existantes."""
        anciens_etats = [c.etat_serialisable() for c in self.cellules]
        for c in self.cellules:
            if hasattr(c, "_timer_zoom"):
                c._timer_zoom.stop()
            c.setParent(None)
            c.deleteLater()
        self.cellules = []
        self.rows = max(1, rows)
        self.cols = max(1, cols)
        self._index_selection = -1
        nb = self.rows * self.cols
        for i in range(nb):
            cell = CelluleImage(i, self)
            cell.fournisseur_style_label = self.fournisseur_style_label
            cell.fournisseur_style_bordure = self.fournisseur_style_bordure
            cell.image_changee.connect(self.grille_modifiee.emit)
            cell.selection_demandee.connect(self._selectionner)
            cell.label_clic.connect(self.label_a_editer.emit)
            cell.swap_demande.connect(self.intervertir)
            # Fin d'un recadrage/zoom de case => point d'annulation.
            cell.ajustement_termine.connect(self.grille_modifiee.emit)
            self.cellules.append(cell)
            cell.show()
            if i < len(anciens_etats):
                cell.restaurer_etat(anciens_etats[i])
        self._replacer_cellules()
        self.update()
        self.grille_modifiee.emit()

    def definir_fournisseur_label(self, fournisseur):
        """Definit le fournisseur de style d'etiquette et le propage aux cases."""
        self.fournisseur_style_label = fournisseur
        for c in self.cellules:
            c.fournisseur_style_label = fournisseur

    def definir_fournisseur_bordure(self, fournisseur):
        """Definit le fournisseur de style de bordure et le propage aux cases."""
        self.fournisseur_style_bordure = fournisseur
        for c in self.cellules:
            c.fournisseur_style_bordure = fournisseur

    def definir_fournisseur_filigrane(self, fournisseur):
        """Definit le fournisseur de style de filigrane (dessine dans l'apercu)."""
        self.fournisseur_style_filigrane = fournisseur

    def reinitialiser_cadrage(self):
        """Recentre et dezoom toutes les cases remplies (sans toucher
        a la rotation ni au contenu)."""
        for c in self.cellules:
            if c.pixmap is not None:
                c.offset_x = 0.5
                c.offset_y = 0.5
                c.cell_zoom = 1.0
                c.update()
        self.grille_modifiee.emit()

    def definir_ratio(self, ratio):
        self.ratio = ratio if ratio and ratio > 0 else (16 / 9)
        self._replacer_cellules()
        self.update()

    def vider_images(self):
        for c in self.cellules:
            c.vider()
        self._selectionner(-1)

    def cellules_remplies(self):
        return [c for c in self.cellules if c.pixmap is not None]

    def _selectionner(self, index):
        """Met a jour la case selectionnee (cadre bleu) et notifie."""
        self._index_selection = index
        for c in self.cellules:
            etait = c.selectionnee
            c.selectionnee = (c.index == index)
            if etait != c.selectionnee:
                c.update()
        self.cellule_selectionnee.emit(index)

    def case_selectionnee(self):
        if 0 <= self._index_selection < len(self.cellules):
            return self.cellules[self._index_selection]
        return None

    def intervertir(self, src, dst):
        """Echange le contenu de deux cases."""
        if not (0 <= src < len(self.cellules)) or not (0 <= dst < len(self.cellules)):
            return
        a = self.cellules[src]
        b = self.cellules[dst]
        etat_a = a.etat_serialisable()
        etat_b = b.etat_serialisable()
        a.restaurer_etat(etat_b)
        b.restaurer_etat(etat_a)
        self.grille_modifiee.emit()

    # --- Zone de rendu (respecte le ratio de sortie) ---
    def rect_zone_rendu(self):
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return QRect(0, 0, 1, 1)
        if w / h > self.ratio:
            zone_h = h
            zone_w = int(h * self.ratio)
        else:
            zone_w = w
            zone_h = int(w / self.ratio)
        x = (w - zone_w) // 2
        y = (h - zone_h) // 2
        return QRect(x, y, zone_w, zone_h)

    def resizeEvent(self, event):
        self._replacer_cellules()
        super().resizeEvent(event)

    def showEvent(self, event):
        self._replacer_cellules()
        super().showEvent(event)

    def _espacement_apercu(self):
        """Espace entre cases dans l'apercu = epaisseur du separateur si actif,
        sinon 0 (cases jointives, pas de bordure)."""
        return self.separateur_epaisseur if self.separateur_actif else 0

    def _replacer_cellules(self):
        """Positionne chaque cellule dans la zone de rendu."""
        zone = self.rect_zone_rendu()
        if not self.cellules:
            return
        espace = self._espacement_apercu()
        inner_x = zone.x() + self.margin
        inner_y = zone.y() + self.margin
        inner_w = zone.width() - 2 * self.margin
        inner_h = zone.height() - 2 * self.margin
        if inner_w <= 0 or inner_h <= 0:
            return
        cell_w = (inner_w - (self.cols - 1) * espace) / self.cols
        cell_h = (inner_h - (self.rows - 1) * espace) / self.rows
        for i, cell in enumerate(self.cellules):
            r = i // self.cols
            c = i % self.cols
            x = inner_x + c * (cell_w + espace)
            y = inner_y + r * (cell_h + espace)
            cell.setGeometry(int(x), int(y), int(cell_w), int(cell_h))

    def paintEvent(self, event):
        """Fond global + fond de la zone de rendu + barres separatrices.
        Aucune bordure n'est dessinee autour de la zone de rendu."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(COL_FOND))
        zone = self.rect_zone_rendu()
        painter.fillRect(zone, QColor(self.bg_color))

        # Barres separatrices entre les cases (facultatives).
        if self.separateur_actif and self.separateur_epaisseur > 0 and self.cellules:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(self.separateur_couleur))
            espace = self._espacement_apercu()
            inner_x = zone.x() + self.margin
            inner_y = zone.y() + self.margin
            inner_w = zone.width() - 2 * self.margin
            inner_h = zone.height() - 2 * self.margin
            if inner_w > 0 and inner_h > 0:
                cell_w = (inner_w - (self.cols - 1) * espace) / self.cols
                cell_h = (inner_h - (self.rows - 1) * espace) / self.rows
                # Barres verticales.
                for c in range(1, self.cols):
                    bx = inner_x + c * cell_w + (c - 1) * espace
                    painter.drawRect(QRectF(bx, inner_y, espace, inner_h))
                # Barres horizontales.
                for r in range(1, self.rows):
                    by = inner_y + r * cell_h + (r - 1) * espace
                    painter.drawRect(QRectF(inner_x, by, inner_w, espace))
        painter.end()


# ==============================================================================
#  MOTEUR D'EXPORT  (rendu 1:1 a la taille de sortie reelle)
# ==============================================================================
def generer_pixmap_compilation(grille, sortie_w, sortie_h, params_label,
                               params_bordure=None, params_filigrane=None):
    """Construit le QPixmap final a la taille exacte (sortie_w x sortie_h).
    Pas de bordure logicielle imposee : seulement le fond, les images, le
    separateur facultatif, la bordure par image facultative, les etiquettes
    et le filigrane facultatif."""
    sortie_w = int(sortie_w)
    sortie_h = int(sortie_h)
    pix = QPixmap(sortie_w, sortie_h)
    pix.fill(QColor(grille.bg_color))

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    # Echelle apercu -> sortie reelle.
    zone_apercu = grille.rect_zone_rendu()
    ratio_echelle = sortie_w / zone_apercu.width() if zone_apercu.width() > 0 else 1.0

    marge = grille.margin * ratio_echelle
    espace = (grille.separateur_epaisseur * ratio_echelle
              if grille.separateur_actif else 0)

    inner_x = marge
    inner_y = marge
    inner_w = sortie_w - 2 * marge
    inner_h = sortie_h - 2 * marge
    if inner_w <= 0 or inner_h <= 0:
        inner_x = inner_y = 0
        inner_w, inner_h = sortie_w, sortie_h

    cell_w = (inner_w - (grille.cols - 1) * espace) / grille.cols
    cell_h = (inner_h - (grille.rows - 1) * espace) / grille.rows

    # Images.
    for i, cell in enumerate(grille.cellules):
        r = i // grille.cols
        c = i % grille.cols
        x = inner_x + c * (cell_w + espace)
        y = inner_y + r * (cell_h + espace)
        rect = QRectF(x, y, cell_w, cell_h)
        if cell.pixmap is not None:
            peindre_image_dans_rect(painter, cell.pixmap, rect,
                                    cell.offset_x, cell.offset_y,
                                    cell.cell_zoom,
                                    getattr(cell, "rotation", 0))

    # Bordure facultative autour de chaque image.
    if params_bordure and params_bordure.get("enabled"):
        epaisseur_b = params_bordure.get("thickness", 4) * ratio_echelle
        for i, cell in enumerate(grille.cellules):
            if cell.pixmap is None:
                continue
            r = i // grille.cols
            c = i % grille.cols
            x = inner_x + c * (cell_w + espace)
            y = inner_y + r * (cell_h + espace)
            dessiner_bordure_image(painter, QRectF(x, y, cell_w, cell_h),
                                   params_bordure.get("color", "#ffffff"),
                                   epaisseur_b)

    # Barres separatrices.
    if grille.separateur_actif and espace > 0:
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(grille.separateur_couleur))
        for c in range(1, grille.cols):
            bx = inner_x + c * cell_w + (c - 1) * espace
            painter.drawRect(QRectF(bx, inner_y, espace, inner_h))
        for r in range(1, grille.rows):
            by = inner_y + r * cell_h + (r - 1) * espace
            painter.drawRect(QRectF(inner_x, by, inner_w, espace))

    # Etiquettes (texte propre a chaque case).
    if params_label.get("enabled"):
        for i, cell in enumerate(grille.cellules):
            texte = _resoudre_texte_label(cell)
            if not texte:
                continue
            r = i // grille.cols
            c = i % grille.cols
            x = inner_x + c * (cell_w + espace)
            y = inner_y + r * (cell_h + espace)
            rect = QRectF(x, y, cell_w, cell_h)
            dessiner_label(painter, rect, texte,
                           params_label.get("position", "bl"),
                           params_label.get("size", 16),
                           params_label.get("text_color", "#ffffff"),
                           params_label.get("bg_color", "#000000"),
                           params_label.get("bg_opacity", 150),
                           echelle=ratio_echelle)

    # Filigrane global sur toute la compilation.
    if params_filigrane and params_filigrane.get("enabled"):
        texte_f = params_filigrane.get("text", "")
        if texte_f:
            zone_complete = QRectF(0, 0, sortie_w, sortie_h)
            dessiner_filigrane(painter, zone_complete, texte_f,
                               params_filigrane.get("position", "br"),
                               params_filigrane.get("size", 28),
                               params_filigrane.get("opacity", 160),
                               echelle=ratio_echelle)

    painter.end()
    return pix


# ==============================================================================
#  WIDGET : SUPERPOSITION DU FILIGRANE  (dessine par-dessus les cellules)
# ==============================================================================
class SuperpositionFiligrane(QWidget):
    """Widget transparent place au-dessus de la grille et des cellules.
    Il ne sert qu'a dessiner le filigrane global en direct dans l'apercu,
    car les cellules (widgets enfants) masqueraient un filigrane peint par
    la grille elle-meme. Il laisse passer tous les evenements souris."""

    def __init__(self, grille, parent=None):
        super().__init__(parent)
        self.grille = grille
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

    def paintEvent(self, event):
        fournisseur = getattr(self.grille, "fournisseur_style_filigrane", None)
        if fournisseur is None:
            return
        try:
            style = fournisseur()
        except Exception:
            style = None
        if not style or not style.get("enabled") or not style.get("text"):
            return
        zone = self.grille.rect_zone_rendu()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        dessiner_filigrane(painter, QRectF(zone), style.get("text", ""),
                           style.get("position", "br"),
                           style.get("size", 28),
                           style.get("opacity", 160),
                           echelle=1.0)
        painter.end()


# ==============================================================================
#  WIDGET PRINCIPAL DU MODULE COMPILATION
# ==============================================================================
class WidgetCompilation(QWidget):
    """Panneau de compilation : reglages a gauche (defilables), apercu a droite."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.templates, self.favoris, self.presets_perso = charger_gabarits()
        # Liste de travail des presets : presets fournis (builtin) + perso.
        self.presets = [dict(p, builtin=True) for p in OUTPUT_PRESETS] \
            + self.presets_perso
        # Permet au widget de recevoir les raccourcis clavier
        # (Ctrl+Z / Ctrl+Y / Suppr) meme apres un clic dans l'apercu.
        self.setFocusPolicy(Qt.StrongFocus)

        layout_global = QHBoxLayout(self)
        layout_global.setContentsMargins(0, 0, 0, 0)
        layout_global.setSpacing(0)

        # --- PANNEAU GAUCHE : zone defilable, largeur adaptative ---
        # QFrame (et non QWidget) pour que le style "QFrame#Sidebar" du theme
        # sombre s'applique. On force aussi le fond en dur par securite, afin
        # qu'aucun texte ne devienne illisible sur un fond clair par defaut.
        panneau = QFrame()
        panneau.setObjectName("Sidebar")
        panneau.setStyleSheet("QFrame#Sidebar { background-color: %s; }" % COL_PANNEAU)
        col = QVBoxLayout(panneau)
        col.setContentsMargins(14, 14, 14, 14)
        col.setSpacing(7)

        self._construire_section_gabarits(col)
        self._sep(col)
        self._construire_section_layout(col)
        self._sep(col)
        self._construire_section_format(col)
        self._sep(col)
        self._construire_section_separateur(col)
        self._sep(col)
        self._construire_section_bordure(col)
        self._sep(col)
        self._construire_section_labels(col)
        self._sep(col)
        self._construire_section_filigrane(col)
        self._sep(col)
        self._construire_section_actions(col)
        col.addStretch()

        # QScrollArea : le panneau defile verticalement et ne deborde jamais.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(panneau)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: %s; }" % COL_PANNEAU)
        # Largeur bornee mais souple : s'adapte sans deborder.
        scroll.setMinimumWidth(300)
        scroll.setMaximumWidth(370)
        scroll.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # --- ZONE DROITE : apercu ---
        zone_droite = QWidget()
        v_droite = QVBoxLayout(zone_droite)
        v_droite.setContentsMargins(10, 10, 10, 10)
        v_droite.setSpacing(8)

        self.hint = QLabel("ℹ  " + ct("comp_adjust_hint"))
        self.hint.setStyleSheet("color:#aaaaaa; font-size:12px;")
        self.hint.setWordWrap(True)
        v_droite.addWidget(self.hint)

        self.grille = GrilleCompilation()
        self.grille.definir_fournisseur_label(self._params_label)
        self.grille.definir_fournisseur_bordure(self._params_bordure)
        self.grille.definir_fournisseur_filigrane(self._params_filigrane)
        self.grille.grille_modifiee.connect(self._on_grille_modifiee)
        self.grille.label_a_editer.connect(self._editer_label_case)
        # Superposition transparente pour dessiner le filigrane en direct,
        # par-dessus les cellules. Reste synchronisee avec la taille de la grille.
        self.overlay_filigrane = SuperpositionFiligrane(self.grille, self.grille)
        self.grille.installEventFilter(self)
        v_droite.addWidget(self.grille, 1)

        # Pied de page facon Photoshop : affiche les messages de statut
        # (export reussi, etc.) sans bloquer avec une fenetre de dialogue.
        self.barre_statut = QLabel("")
        self.barre_statut.setStyleSheet(
            "QLabel { background-color:#161f2e; color:%s; border-top:1px "
            "solid #283750; padding:5px 12px; font-size:12px; }" % COL_TEXTE_DOUX)
        self.barre_statut.setMinimumHeight(28)
        v_droite.addWidget(self.barre_statut)
        # Timer pour effacer le message de statut apres quelques secondes.
        self._timer_statut = QTimer(self)
        self._timer_statut.setSingleShot(True)
        self._timer_statut.timeout.connect(lambda: self.barre_statut.setText(""))

        layout_global.addWidget(scroll)
        layout_global.addWidget(self._construire_volet_packs())
        layout_global.addWidget(zone_droite, 1)

        # --- Etat du volet des packs de compilation ---
        # batch_packs : liste de packs ; batch_index : pack charge (-1 = aucun).
        self.batch_packs = []
        self.batch_index = -1
        self._rafraichir_liste_packs()

        # Initialisation.
        self.combo_templates.setCurrentIndex(0)
        self._appliquer_template_courant()
        self.combo_preset.setCurrentIndex(0)
        self._appliquer_preset()
        self._maj_etat_labels()
        self._maj_grille_separateur()
        self._maj_etat_bordure()
        self._maj_etat_filigrane()
        cfg = _cfg()
        reglages_sauves = cfg.get("compilation_settings") if cfg is not None else None
        if isinstance(reglages_sauves, dict):
            self._appliquer_reglages_planche(reglages_sauves)

        # --- Historique annuler / retablir ---
        # Pile d'instantanes de la planche. _hist_index pointe sur l'etat
        # courant. _hist_gel evite d'enregistrer pendant une restauration.
        self._historique = []
        self._hist_index = -1
        self._hist_gel = False
        self._enregistrer_historique()  # etat initial
        if TEMPLATES_LOAD_WARNING:
            self._statut(ct("comp_templates_backup",
                            path=TEMPLATES_LOAD_WARNING),
                         succes=False, duree_ms=10000)

    # ------------------------------------------------------------------
    #  HELPERS DE CONSTRUCTION
    # ------------------------------------------------------------------
    def _sep(self, layout):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color:#3a3a3a; background:#3a3a3a; max-height:1px;")
        layout.addSpacing(3)
        layout.addWidget(line)
        layout.addSpacing(3)

    def _titre(self, texte):
        lbl = QLabel(texte)
        lbl.setStyleSheet("font-weight:bold; font-size:13px; color:%s;" % COL_TITRE)
        return lbl

    def _ligne(self, texte_label, widget):
        """Empile le libelle AU-DESSUS du widget. Le libelle dispose ainsi de
        toute la largeur du volet (pas de texte coupe) et est en blanc lisible.
        Le widget prend toute la largeur disponible."""
        v = QVBoxLayout()
        v.setSpacing(2)
        lbl = QLabel(texte_label)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color:#dddddd; font-size:12px;")
        v.addWidget(lbl)
        # Le widget ne doit pas etre bride en largeur (sauf boutons couleur).
        if not isinstance(widget, QPushButton):
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        v.addWidget(widget)
        return v

    # ------------------------------------------------------------------
    #  SECTION GABARITS
    # ------------------------------------------------------------------
    def _construire_section_gabarits(self, layout):
        layout.addWidget(self._titre(ct("comp_templates")))
        self.edit_filtre_templates = QLineEdit()
        self.edit_filtre_templates.setPlaceholderText("Filtrer...")
        self.edit_filtre_templates.textChanged.connect(self._filtrer_gabarits)
        layout.addWidget(self.edit_filtre_templates)
        self.combo_templates = QComboBox()
        self._remplir_combo_templates()
        self.combo_templates.currentIndexChanged.connect(self._appliquer_template_courant)
        layout.addWidget(self.combo_templates)

        h = QHBoxLayout()
        btn_new = QPushButton(ct("comp_new_template"))
        btn_new.clicked.connect(self._nouveau_gabarit)
        btn_del = QPushButton(ct("comp_del_template"))
        btn_del.setObjectName("DangerButton")
        btn_del.clicked.connect(self._supprimer_gabarit)
        h.addWidget(btn_new)
        h.addWidget(btn_del)
        layout.addLayout(h)

        btn_save = QPushButton(ct("comp_save_template"))
        btn_save.clicked.connect(self._sauver_gabarit_courant)
        layout.addWidget(btn_save)

    # ------------------------------------------------------------------
    #  SECTION DISPOSITION
    # ------------------------------------------------------------------
    def _construire_section_layout(self, layout):
        layout.addWidget(self._titre(ct("comp_layout")))

        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 10)
        self.spin_rows.setValue(2)
        self.spin_rows.valueChanged.connect(self._changer_dimensions_grille)
        layout.addLayout(self._ligne(ct("comp_rows"), self.spin_rows))

        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 10)
        self.spin_cols.setValue(2)
        self.spin_cols.valueChanged.connect(self._changer_dimensions_grille)
        layout.addLayout(self._ligne(ct("comp_cols"), self.spin_cols))

        self.btn_orientation = QPushButton(ct("comp_orientation_h"))
        self.btn_orientation.clicked.connect(self._basculer_orientation)
        layout.addWidget(self.btn_orientation)

        self.spin_margin = QSpinBox()
        self.spin_margin.setRange(0, 400)
        self.spin_margin.setValue(12)
        self.spin_margin.valueChanged.connect(self._maj_grille_apparence)
        layout.addLayout(self._ligne(ct("comp_margin"), self.spin_margin))

        self.btn_bg_color = QPushButton()
        self.bg_color = COL_FOND
        self.btn_bg_color.setStyleSheet("background-color:%s;" % self.bg_color)
        self.btn_bg_color.setFixedWidth(60)
        self.btn_bg_color.clicked.connect(self._choisir_bg_color)
        layout.addLayout(self._ligne(ct("comp_bg_color"), self.btn_bg_color))

    # ------------------------------------------------------------------
    #  SECTION FORMAT DE SORTIE
    # ------------------------------------------------------------------
    def _construire_section_format(self, layout):
        layout.addWidget(self._titre(ct("comp_output")))

        self.combo_preset = QComboBox()
        self._remplir_combo_presets()
        self.combo_preset.currentIndexChanged.connect(self._appliquer_preset)
        layout.addLayout(self._ligne(ct("comp_preset"), self.combo_preset))

        # Gestion des presets personnalises : ajouter / modifier / supprimer.
        h_preset = QHBoxLayout()
        btn_add_preset = QPushButton(ct("comp_preset_add"))
        btn_add_preset.clicked.connect(self._ajouter_preset)
        btn_edit_preset = QPushButton(ct("comp_preset_edit"))
        btn_edit_preset.clicked.connect(self._modifier_preset)
        btn_del_preset = QPushButton(ct("comp_preset_del"))
        btn_del_preset.setObjectName("DangerButton")
        btn_del_preset.clicked.connect(self._supprimer_preset)
        h_preset.addWidget(btn_add_preset)
        h_preset.addWidget(btn_edit_preset)
        h_preset.addWidget(btn_del_preset)
        layout.addLayout(h_preset)

        self.spin_w = QSpinBox()
        self.spin_w.setRange(64, 12000)
        self.spin_w.setValue(1600)
        self.spin_w.valueChanged.connect(self._dimensions_modifiees)
        layout.addLayout(self._ligne(ct("comp_width"), self.spin_w))

        self.spin_h = QSpinBox()
        self.spin_h.setRange(64, 12000)
        self.spin_h.setValue(900)
        self.spin_h.valueChanged.connect(self._dimensions_modifiees)
        layout.addLayout(self._ligne(ct("comp_height"), self.spin_h))

        # Bouton d'inversion largeur <-> hauteur.
        self.btn_swap_wh = QPushButton(ct("comp_swap_wh"))
        self.btn_swap_wh.clicked.connect(self._inverser_largeur_hauteur)
        layout.addWidget(self.btn_swap_wh)

        self.cb_ratio_lock = QCheckBox(ct("comp_ratio_lock"))
        self.cb_ratio_lock.setChecked(False)
        self._ratio_sortie = self.spin_w.value() / self.spin_h.value()
        self.cb_ratio_lock.stateChanged.connect(self._memoriser_ratio_sortie)
        layout.addWidget(self.cb_ratio_lock)

    # ------------------------------------------------------------------
    #  SECTION BORDURE PAR IMAGE
    # ------------------------------------------------------------------
    def _construire_section_bordure(self, layout):
        layout.addWidget(self._titre(ct("comp_border_section")))

        self.cb_bordure = QCheckBox(ct("comp_border_enable"))
        self.cb_bordure.setChecked(False)
        self.cb_bordure.stateChanged.connect(self._maj_etat_bordure)
        layout.addWidget(self.cb_bordure)

        self.btn_bordure_color = QPushButton()
        self.bordure_color = "#ffffff"
        self.btn_bordure_color.setStyleSheet("background-color:%s;" % self.bordure_color)
        self.btn_bordure_color.setFixedWidth(60)
        self.btn_bordure_color.clicked.connect(self._choisir_bordure_color)
        layout.addLayout(self._ligne(ct("comp_border_color"),
                                     self.btn_bordure_color))

        self.spin_bordure_epaisseur = QSpinBox()
        self.spin_bordure_epaisseur.setRange(1, 100)
        self.spin_bordure_epaisseur.setValue(4)
        self.spin_bordure_epaisseur.valueChanged.connect(self._maj_etat_bordure)
        layout.addLayout(self._ligne(ct("comp_border_thickness"),
                                     self.spin_bordure_epaisseur))

    # ------------------------------------------------------------------
    #  SECTION FILIGRANE GLOBAL
    # ------------------------------------------------------------------
    def _construire_section_filigrane(self, layout):
        layout.addWidget(self._titre(ct("comp_watermark_section")))

        self.cb_filigrane = QCheckBox(ct("comp_watermark_enable"))
        self.cb_filigrane.setChecked(False)
        self.cb_filigrane.stateChanged.connect(self._maj_etat_filigrane)
        layout.addWidget(self.cb_filigrane)

        self.edit_filigrane = QLineEdit()
        # Pre-remplissage depuis la config du comparateur si disponible.
        cfg = _cfg()
        if cfg is not None:
            txt_wm = cfg.get("watermark_text")
            if txt_wm:
                self.edit_filigrane.setText(txt_wm)
        self.edit_filigrane.textChanged.connect(self._rafraichir_apercu)
        layout.addLayout(self._ligne(ct("comp_watermark_text"),
                                     self.edit_filigrane))

        self.combo_filigrane_pos = QComboBox()
        for code in POSITIONS:
            self.combo_filigrane_pos.addItem(ct("comp_pos_" + code), code)
        self.combo_filigrane_pos.setCurrentIndex(POSITIONS.index("br"))
        self.combo_filigrane_pos.currentIndexChanged.connect(self._rafraichir_apercu)
        layout.addLayout(self._ligne(ct("comp_watermark_pos"),
                                     self.combo_filigrane_pos))

        self.spin_filigrane_size = QSpinBox()
        self.spin_filigrane_size.setRange(8, 200)
        self.spin_filigrane_size.setValue(28)
        self.spin_filigrane_size.valueChanged.connect(self._rafraichir_apercu)
        layout.addLayout(self._ligne(ct("comp_watermark_size"),
                                     self.spin_filigrane_size))

        self.slider_filigrane_op = QSlider(Qt.Horizontal)
        self.slider_filigrane_op.setRange(0, 255)
        self.slider_filigrane_op.setValue(160)
        self.slider_filigrane_op.valueChanged.connect(self._rafraichir_apercu)
        layout.addLayout(self._ligne(ct("comp_watermark_opacity"),
                                     self.slider_filigrane_op))

    # ------------------------------------------------------------------
    #  SECTION SEPARATEUR
    # ------------------------------------------------------------------
    def _construire_section_separateur(self, layout):
        layout.addWidget(self._titre(ct("comp_separator_section")))

        self.cb_separateur = QCheckBox(ct("comp_separator_enable"))
        self.cb_separateur.setChecked(True)
        self.cb_separateur.stateChanged.connect(self._maj_grille_separateur)
        layout.addWidget(self.cb_separateur)

        self.btn_sep_color = QPushButton()
        self.sep_color = "#ffffff"
        self.btn_sep_color.setStyleSheet("background-color:%s;" % self.sep_color)
        self.btn_sep_color.setFixedWidth(60)
        self.btn_sep_color.clicked.connect(self._choisir_sep_color)
        layout.addLayout(self._ligne(ct("comp_separator_color"), self.btn_sep_color))

        self.spin_sep_epaisseur = QSpinBox()
        self.spin_sep_epaisseur.setRange(1, 100)
        self.spin_sep_epaisseur.setValue(6)
        self.spin_sep_epaisseur.valueChanged.connect(self._maj_grille_separateur)
        layout.addLayout(self._ligne(ct("comp_separator_thickness"),
                                     self.spin_sep_epaisseur))

    # ------------------------------------------------------------------
    #  SECTION ETIQUETTES
    # ------------------------------------------------------------------
    def _construire_section_labels(self, layout):
        layout.addWidget(self._titre(ct("comp_labels_section")))

        self.cb_label = QCheckBox(ct("comp_label_enable"))
        self.cb_label.setChecked(True)
        self.cb_label.stateChanged.connect(self._maj_etat_labels)
        layout.addWidget(self.cb_label)

        lbl_hint = QLabel("ℹ  " + ct("comp_label_hint"))
        lbl_hint.setStyleSheet("color:#999999; font-size:11px;")
        lbl_hint.setWordWrap(True)
        layout.addWidget(lbl_hint)

        # Position par defaut des etiquettes.
        self.combo_pos = QComboBox()
        for code in POSITIONS:
            self.combo_pos.addItem(ct("comp_pos_" + code), code)
        self.combo_pos.setCurrentIndex(POSITIONS.index("bl"))
        self.combo_pos.currentIndexChanged.connect(self._rafraichir_apercu)
        layout.addLayout(self._ligne(ct("comp_label_pos"), self.combo_pos))

        self.spin_label_size = QSpinBox()
        self.spin_label_size.setRange(6, 96)
        self.spin_label_size.setValue(16)
        self.spin_label_size.valueChanged.connect(self._rafraichir_apercu)
        layout.addLayout(self._ligne(ct("comp_label_size"), self.spin_label_size))

        self.btn_txt_color = QPushButton()
        self.label_txt_color = "#ffffff"
        self.btn_txt_color.setStyleSheet("background-color:%s;" % self.label_txt_color)
        self.btn_txt_color.setFixedWidth(60)
        self.btn_txt_color.clicked.connect(self._choisir_txt_color)
        layout.addLayout(self._ligne(ct("comp_label_txt_color"), self.btn_txt_color))

        self.btn_label_bg = QPushButton()
        self.label_bg_color = "#000000"
        self.btn_label_bg.setStyleSheet("background-color:%s;" % self.label_bg_color)
        self.btn_label_bg.setFixedWidth(60)
        self.btn_label_bg.clicked.connect(self._choisir_label_bg)
        layout.addLayout(self._ligne(ct("comp_label_bg_color"), self.btn_label_bg))

        self.slider_label_op = QSlider(Qt.Horizontal)
        self.slider_label_op.setRange(0, 255)
        self.slider_label_op.setValue(150)
        self.slider_label_op.valueChanged.connect(self._rafraichir_apercu)
        layout.addLayout(self._ligne(ct("comp_label_bg_opacity"),
                                     self.slider_label_op))

        # Favoris (utilises dans le dialogue d'etiquette par case).
        layout.addSpacing(4)
        layout.addWidget(QLabel(ct("comp_favorites")))
        self.combo_fav = QComboBox()
        self._remplir_combo_fav()
        layout.addWidget(self.combo_fav)

        h_fav = QHBoxLayout()
        btn_add_fav = QPushButton(ct("comp_add_fav"))
        btn_add_fav.clicked.connect(self._ajouter_favori)
        btn_del_fav = QPushButton(ct("comp_del_fav"))
        btn_del_fav.clicked.connect(self._supprimer_favori)
        h_fav.addWidget(btn_add_fav)
        h_fav.addWidget(btn_del_fav)
        layout.addLayout(h_fav)

    # ------------------------------------------------------------------
    #  SECTION ACTIONS
    # ------------------------------------------------------------------
    def _construire_section_actions(self, layout):
        btn_new_board = QPushButton(ct("comp_new_board"))
        btn_new_board.clicked.connect(self._nouvelle_planche)
        layout.addWidget(btn_new_board)

        # Reinitialisation du cadrage de toutes les cases en un clic.
        btn_reset_crop = QPushButton(ct("comp_reset_all_crop"))
        btn_reset_crop.clicked.connect(self._reinitialiser_cadrage)
        layout.addWidget(btn_reset_crop)

        # Sauvegarde / ouverture d'un projet de compilation.
        h_proj = QHBoxLayout()
        btn_save_proj = QPushButton(ct("comp_save_project"))
        btn_save_proj.clicked.connect(self._sauver_projet)
        btn_open_proj = QPushButton(ct("comp_open_project"))
        btn_open_proj.clicked.connect(self._ouvrir_projet)
        h_proj.addWidget(btn_save_proj)
        h_proj.addWidget(btn_open_proj)
        layout.addLayout(h_proj)

        btn_copy = QPushButton(ct("comp_copy"))
        btn_copy.clicked.connect(self._copier)
        layout.addWidget(btn_copy)

        btn_export = QPushButton(ct("comp_export"))
        btn_export.setObjectName("PrimaryButton")
        btn_export.clicked.connect(self._exporter)
        layout.addWidget(btn_export)

    # ==================================================================
    #  CONSTRUCTION DU VOLET DES PACKS DE COMPILATION
    # ==================================================================
    def _construire_volet_packs(self):
        """Construit le volet lateral listant les packs de compilation.
        Chaque pack deviendra une planche ; tous partagent le gabarit
        actuel. Retourne le QFrame pret a etre insere dans le layout."""
        volet = VoletPacksCompilation(self)
        volet.setObjectName("Sidebar")
        volet.setStyleSheet("QFrame#Sidebar { background-color: %s; }"
                            % COL_PANNEAU)
        volet.setMinimumWidth(190)
        volet.setMaximumWidth(240)
        v = QVBoxLayout(volet)
        v.setContentsMargins(10, 12, 10, 12)
        v.setSpacing(7)

        titre = QLabel(ct("comp_batch_panel"))
        titre.setStyleSheet("font-weight:bold; font-size:14px; color:%s;"
                            % COL_TITRE)
        v.addWidget(titre)

        aide = QLabel(ct("comp_batch_hint"))
        aide.setStyleSheet("color:%s; font-size:11px;" % COL_TEXTE_DOUX)
        aide.setWordWrap(True)
        v.addWidget(aide)

        mode_label = QLabel(ct("comp_import_mode"))
        mode_label.setStyleSheet("color:%s; font-size:11px; font-weight:bold;"
                                 % COL_TEXTE_DOUX)
        v.addWidget(mode_label)

        h_mode = QHBoxLayout()
        h_mode.setSpacing(4)
        self.groupe_import_mode = QButtonGroup(self)
        self.rb_import_gabarit = QRadioButton(ct("comp_import_by_template"))
        self.rb_import_dynamique = QRadioButton(ct("comp_import_dynamic"))
        self.groupe_import_mode.addButton(self.rb_import_gabarit)
        self.groupe_import_mode.addButton(self.rb_import_dynamique)
        cfg = _cfg()
        mode_import = (cfg.get("compilation_import_mode")
                       if cfg is not None else None) or "gabarit"
        self.rb_import_dynamique.setChecked(mode_import == "dynamique")
        self.rb_import_gabarit.setChecked(mode_import != "dynamique")
        self.rb_import_gabarit.toggled.connect(self._sauver_mode_import)
        self.rb_import_dynamique.toggled.connect(self._sauver_mode_import)
        h_mode.addWidget(self.rb_import_gabarit)
        h_mode.addWidget(self.rb_import_dynamique)
        v.addLayout(h_mode)

        # Liste des packs : nom + vignette ; double-clic pour renommer.
        self.liste_packs = ListePacksCompilation(self)
        self.liste_packs.setIconSize(QSize(46, 46))
        self.liste_packs.currentRowChanged.connect(self._changer_pack)
        self.liste_packs.itemDoubleClicked.connect(self._renommer_pack)
        self.liste_packs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.liste_packs.customContextMenuRequested.connect(self._menu_pack)
        v.addWidget(self.liste_packs, 1)

        # Boutons d'ajout / suppression de pack.
        h = QHBoxLayout()
        btn_add = QPushButton(ct("comp_batch_add"))
        btn_add.clicked.connect(self._ajouter_pack)
        btn_del = QPushButton(ct("comp_batch_del"))
        btn_del.setObjectName("DangerButton")
        btn_del.clicked.connect(self._supprimer_pack)
        h.addWidget(btn_add)
        h.addWidget(btn_del)
        v.addLayout(h)

        # Bouton de generation de masse.
        self.btn_batch_gen = QPushButton(ct("comp_batch_generate"))
        self.btn_batch_gen.setObjectName("PrimaryButton")
        self.btn_batch_gen.clicked.connect(self._generer_tous_les_packs)
        self.btn_batch_gen.setEnabled(False)
        v.addWidget(self.btn_batch_gen)

        return volet

    # ==================================================================
    #  GABARITS
    # ==================================================================
    def _remplir_combo_templates(self):
        filtre = ""
        if hasattr(self, "edit_filtre_templates"):
            filtre = self.edit_filtre_templates.text().strip().lower()
        courant = self.combo_templates.currentData()
        if courant is None:
            courant = self.combo_templates.currentIndex()
        self.combo_templates.blockSignals(True)
        self.combo_templates.clear()
        index_a_restaurer = -1
        for idx, t in enumerate(self.templates):
            if filtre and filtre not in t["name"].lower():
                continue
            suffixe = "  " + ct("comp_builtin") if t.get("builtin") else ""
            self.combo_templates.addItem(t["name"] + suffixe, idx)
            if idx == courant:
                index_a_restaurer = self.combo_templates.count() - 1
        if index_a_restaurer >= 0:
            self.combo_templates.setCurrentIndex(index_a_restaurer)
        elif self.combo_templates.count() > 0:
            self.combo_templates.setCurrentIndex(0)
        self.combo_templates.blockSignals(False)

    def _filtrer_gabarits(self, texte):
        self._remplir_combo_templates()
        self._appliquer_template_courant()

    def _appliquer_template_courant(self):
        idx = self.combo_templates.currentData()
        if idx is None:
            idx = self.combo_templates.currentIndex()
        if idx < 0 or idx >= len(self.templates):
            return
        t = self.templates[idx]
        # Gabarit complet : on restaure tous les reglages enregistres.
        if t.get("settings"):
            self._appliquer_reglages_planche(t["settings"])
            return
        # Gabarit simple (built-in ou ancien) : disposition seule.
        self.spin_rows.blockSignals(True)
        self.spin_cols.blockSignals(True)
        self.spin_rows.setValue(t["rows"])
        self.spin_cols.setValue(t["cols"])
        self.spin_rows.blockSignals(False)
        self.spin_cols.blockSignals(False)
        self.grille.appliquer_gabarit(t["rows"], t["cols"])
        self._maj_texte_orientation()

    def _changer_dimensions_grille(self):
        self.grille.appliquer_gabarit(self.spin_rows.value(), self.spin_cols.value())
        self._maj_texte_orientation()

    def _basculer_orientation(self):
        r, c = self.spin_cols.value(), self.spin_rows.value()
        self.spin_rows.blockSignals(True)
        self.spin_cols.blockSignals(True)
        self.spin_rows.setValue(r)
        self.spin_cols.setValue(c)
        self.spin_rows.blockSignals(False)
        self.spin_cols.blockSignals(False)
        self.grille.appliquer_gabarit(r, c)
        self._maj_texte_orientation()

    def _maj_texte_orientation(self):
        if self.grille.cols >= self.grille.rows:
            self.btn_orientation.setText(ct("comp_orientation_h"))
        else:
            self.btn_orientation.setText(ct("comp_orientation_v"))

    def _nouveau_gabarit(self):
        resultat = self._demander_infos_gabarit(
            ct("comp_new_template"), avec_dimensions=True)
        if resultat is None:
            return
        nom, rows, cols = resultat
        self._ajouter_gabarit_complet(nom, rows, cols)

    def _demander_infos_gabarit(self, titre, avec_dimensions=False):
        """Demande les infos d'un gabarit en une seule validation."""
        dlg = QDialog(self)
        dlg.setWindowTitle(titre)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        layout.addWidget(QLabel(ct("comp_template_name")))
        edit_nom = QLineEdit()
        layout.addWidget(edit_nom)

        spin_rows = None
        spin_cols = None
        if avec_dimensions:
            ligne_dims = QHBoxLayout()
            spin_rows = QSpinBox()
            spin_rows.setRange(1, 10)
            spin_rows.setValue(self.spin_rows.value())
            spin_cols = QSpinBox()
            spin_cols.setRange(1, 10)
            spin_cols.setValue(self.spin_cols.value())
            ligne_dims.addWidget(QLabel(ct("comp_rows")))
            ligne_dims.addWidget(spin_rows)
            ligne_dims.addWidget(QLabel(ct("comp_cols")))
            ligne_dims.addWidget(spin_cols)
            layout.addLayout(ligne_dims)

        boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        boutons.button(QDialogButtonBox.Ok).setText(ct("comp_ok"))
        boutons.button(QDialogButtonBox.Cancel).setText(ct("comp_cancel"))
        boutons.accepted.connect(dlg.accept)
        boutons.rejected.connect(dlg.reject)
        layout.addWidget(boutons)

        if dlg.exec_() != QDialog.Accepted:
            return None
        nom = edit_nom.text().strip()
        if not nom:
            return None
        if any(t["name"] == nom for t in self.templates):
            QMessageBox.warning(self, titre, ct("comp_template_exists"))
            return None
        rows = spin_rows.value() if spin_rows is not None else self.spin_rows.value()
        cols = spin_cols.value() if spin_cols is not None else self.spin_cols.value()
        return nom, rows, cols

    def _ajouter_gabarit_complet(self, nom, rows, cols):
        """Ajoute un gabarit utilisateur complet depuis les reglages courants."""
        reglages = self._reglages_planche()
        reglages["rows"] = int(rows)
        reglages["cols"] = int(cols)
        self.templates.append({
            "name": nom,
            "rows": int(rows),
            "cols": int(cols),
            "builtin": False,
            "settings": reglages,
        })
        sauver_gabarits(self.templates, self.favoris, self.presets_perso)
        if hasattr(self, "edit_filtre_templates"):
            self.edit_filtre_templates.blockSignals(True)
            self.edit_filtre_templates.clear()
            self.edit_filtre_templates.blockSignals(False)
        self._remplir_combo_templates()
        for i in range(self.combo_templates.count()):
            if self.combo_templates.itemData(i) == len(self.templates) - 1:
                self.combo_templates.setCurrentIndex(i)
                break

    def _reglages_planche(self):
        """Retourne un dictionnaire de TOUS les reglages du volet (hors
        contenu des cases) : disposition, format, separateur, bordure,
        filigrane, etiquettes. Sert aux gabarits complets."""
        return {
            "rows": self.spin_rows.value(),
            "cols": self.spin_cols.value(),
            "margin": self.spin_margin.value(),
            "bg_color": self.bg_color,
            "output_w": self.spin_w.value(),
            "output_h": self.spin_h.value(),
            "separateur_actif": self.cb_separateur.isChecked(),
            "separateur_couleur": self.sep_color,
            "separateur_epaisseur": self.spin_sep_epaisseur.value(),
            "bordure_active": self.cb_bordure.isChecked(),
            "bordure_couleur": self.bordure_color,
            "bordure_epaisseur": self.spin_bordure_epaisseur.value(),
            "filigrane_actif": self.cb_filigrane.isChecked(),
            "filigrane_texte": self.edit_filigrane.text(),
            "filigrane_position": self.combo_filigrane_pos.currentData(),
            "filigrane_size": self.spin_filigrane_size.value(),
            "filigrane_opacity": self.slider_filigrane_op.value(),
            "label_enabled": self.cb_label.isChecked(),
            "label_position": self.combo_pos.currentData(),
            "label_size": self.spin_label_size.value(),
            "label_txt_color": self.label_txt_color,
            "label_bg_color": self.label_bg_color,
            "label_bg_opacity": self.slider_label_op.value(),
        }

    def sauvegarder_reglages(self):
        """Persiste les reglages du volet compilation dans la configuration."""
        cfg = _cfg()
        if cfg is not None:
            cfg.set("compilation_settings", self._reglages_planche())

    def _appliquer_reglages_planche(self, r):
        """Applique un dictionnaire de reglages de planche au volet et a la
        grille (sans toucher au contenu des cases)."""
        # Format de sortie.
        self.spin_w.blockSignals(True)
        self.spin_h.blockSignals(True)
        self.spin_w.setValue(int(r.get("output_w", self.spin_w.value())))
        self.spin_h.setValue(int(r.get("output_h", self.spin_h.value())))
        self.spin_w.blockSignals(False)
        self.spin_h.blockSignals(False)
        self.combo_preset.blockSignals(True)
        self.combo_preset.setCurrentIndex(len(self._presets()))  # "Libre"
        self.combo_preset.blockSignals(False)
        # Marge / fond.
        self.spin_margin.blockSignals(True)
        self.spin_margin.setValue(int(r.get("margin", self.spin_margin.value())))
        self.spin_margin.blockSignals(False)
        self.bg_color = r.get("bg_color", self.bg_color)
        self.btn_bg_color.setStyleSheet("background-color:%s;" % self.bg_color)
        # Separateur.
        self.cb_separateur.blockSignals(True)
        self.cb_separateur.setChecked(bool(r.get("separateur_actif", True)))
        self.cb_separateur.blockSignals(False)
        self.sep_color = r.get("separateur_couleur", self.sep_color)
        self.btn_sep_color.setStyleSheet("background-color:%s;" % self.sep_color)
        self.spin_sep_epaisseur.blockSignals(True)
        self.spin_sep_epaisseur.setValue(int(r.get("separateur_epaisseur", 6)))
        self.spin_sep_epaisseur.blockSignals(False)
        # Bordure.
        self.cb_bordure.blockSignals(True)
        self.cb_bordure.setChecked(bool(r.get("bordure_active", False)))
        self.cb_bordure.blockSignals(False)
        self.bordure_color = r.get("bordure_couleur", self.bordure_color)
        self.btn_bordure_color.setStyleSheet(
            "background-color:%s;" % self.bordure_color)
        self.spin_bordure_epaisseur.blockSignals(True)
        self.spin_bordure_epaisseur.setValue(int(r.get("bordure_epaisseur", 4)))
        self.spin_bordure_epaisseur.blockSignals(False)
        # Filigrane.
        self.cb_filigrane.blockSignals(True)
        self.cb_filigrane.setChecked(bool(r.get("filigrane_actif", False)))
        self.cb_filigrane.blockSignals(False)
        self.edit_filigrane.blockSignals(True)
        self.edit_filigrane.setText(r.get("filigrane_texte", ""))
        self.edit_filigrane.blockSignals(False)
        pos_f = r.get("filigrane_position", "br")
        if pos_f in POSITIONS:
            self.combo_filigrane_pos.blockSignals(True)
            self.combo_filigrane_pos.setCurrentIndex(POSITIONS.index(pos_f))
            self.combo_filigrane_pos.blockSignals(False)
        self.spin_filigrane_size.blockSignals(True)
        self.spin_filigrane_size.setValue(int(r.get("filigrane_size", 28)))
        self.spin_filigrane_size.blockSignals(False)
        self.slider_filigrane_op.blockSignals(True)
        self.slider_filigrane_op.setValue(int(r.get("filigrane_opacity", 160)))
        self.slider_filigrane_op.blockSignals(False)
        # Etiquettes.
        self.cb_label.blockSignals(True)
        self.cb_label.setChecked(bool(r.get("label_enabled", True)))
        self.cb_label.blockSignals(False)
        pos_l = r.get("label_position", "bl")
        if pos_l in POSITIONS:
            self.combo_pos.blockSignals(True)
            self.combo_pos.setCurrentIndex(POSITIONS.index(pos_l))
            self.combo_pos.blockSignals(False)
        self.spin_label_size.blockSignals(True)
        self.spin_label_size.setValue(int(r.get("label_size", 16)))
        self.spin_label_size.blockSignals(False)
        self.label_txt_color = r.get("label_txt_color", self.label_txt_color)
        self.btn_txt_color.setStyleSheet(
            "background-color:%s;" % self.label_txt_color)
        self.label_bg_color = r.get("label_bg_color", self.label_bg_color)
        self.btn_label_bg.setStyleSheet(
            "background-color:%s;" % self.label_bg_color)
        self.slider_label_op.blockSignals(True)
        self.slider_label_op.setValue(int(r.get("label_bg_opacity", 150)))
        self.slider_label_op.blockSignals(False)
        # Disposition (en dernier : reconstruit la grille).
        rows = int(r.get("rows", self.spin_rows.value()))
        cols = int(r.get("cols", self.spin_cols.value()))
        self.spin_rows.blockSignals(True)
        self.spin_cols.blockSignals(True)
        self.spin_rows.setValue(rows)
        self.spin_cols.setValue(cols)
        self.spin_rows.blockSignals(False)
        self.spin_cols.blockSignals(False)
        self.grille.appliquer_gabarit(rows, cols)
        # Rafraichissements.
        self.grille.bg_color = self.bg_color
        self.grille.margin = self.spin_margin.value()
        self._maj_grille_separateur()
        self._maj_ratio_grille()
        self._maj_etat_labels()
        self._maj_etat_bordure()
        self._maj_etat_filigrane()
        self._maj_texte_orientation()
        self._rafraichir_apercu()

    def _sauver_gabarit_courant(self):
        resultat = self._demander_infos_gabarit(
            ct("comp_save_template"), avec_dimensions=False)
        if resultat is None:
            return
        nom, rows, cols = resultat
        self._ajouter_gabarit_complet(
            nom, rows, cols)

    def _supprimer_gabarit(self):
        idx = self.combo_templates.currentData()
        if idx is None:
            idx = self.combo_templates.currentIndex()
        if idx < 0 or idx >= len(self.templates):
            return
        t = self.templates[idx]
        if t.get("builtin"):
            QMessageBox.information(self, ct("comp_del_template"),
                                    ct("comp_builtin"))
            return
        rep = QMessageBox.question(self, ct("comp_del_template"),
                                   ct("comp_confirm_del"),
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            self.templates.pop(idx)
            sauver_gabarits(self.templates, self.favoris, self.presets_perso)
            self._remplir_combo_templates()
            self.combo_templates.setCurrentIndex(0)
            self._appliquer_template_courant()

    # ==================================================================
    #  FORMAT DE SORTIE  (presets fournis + presets personnalises)
    # ==================================================================
    def _presets(self):
        """Liste de travail des presets (builtin + perso)."""
        return self.presets

    def _remplir_combo_presets(self):
        """Remplit le menu deroulant des presets : presets fournis et
        personnalises, puis l'entree 'Libre' en dernier."""
        self.combo_preset.blockSignals(True)
        self.combo_preset.clear()
        for p in self.presets:
            suffixe = "" if p.get("builtin") else "  ★"
            self.combo_preset.addItem("%s (%dx%d)%s"
                                      % (p["name"], p["w"], p["h"], suffixe))
        self.combo_preset.addItem(ct("comp_preset_free"))
        self.combo_preset.blockSignals(False)

    def _appliquer_preset(self):
        idx = self.combo_preset.currentIndex()
        if 0 <= idx < len(self.presets):
            p = self.presets[idx]
            self.spin_w.blockSignals(True)
            self.spin_h.blockSignals(True)
            self.spin_w.setValue(int(p["w"]))
            self.spin_h.setValue(int(p["h"]))
            self.spin_w.blockSignals(False)
            self.spin_h.blockSignals(False)
            self._maj_ratio_grille()

    def _index_libre(self):
        """Index de l'entree 'Libre' dans le combo (apres tous les presets)."""
        return len(self.presets)

    def _ajouter_preset(self):
        """Cree un nouveau preset de format a partir de dimensions saisies."""
        nom, ok = QInputDialog.getText(self, ct("comp_preset_add"),
                                       ct("comp_preset_name"))
        if not ok or not nom.strip():
            return
        nom = nom.strip()
        if any(p["name"] == nom for p in self.presets):
            QMessageBox.warning(self, ct("comp_preset_add"),
                                ct("comp_preset_exists"))
            return
        w, ok2 = QInputDialog.getInt(self, ct("comp_preset_add"),
                                     ct("comp_width"), self.spin_w.value(),
                                     64, 12000)
        if not ok2:
            return
        h, ok3 = QInputDialog.getInt(self, ct("comp_preset_add"),
                                     ct("comp_height"), self.spin_h.value(),
                                     64, 12000)
        if not ok3:
            return
        preset = {"name": nom, "w": w, "h": h, "builtin": False}
        self.presets.append(preset)
        self.presets_perso.append(preset)
        sauver_gabarits(self.templates, self.favoris, self.presets_perso)
        self._remplir_combo_presets()
        self.combo_preset.setCurrentIndex(len(self.presets) - 1)

    def _modifier_preset(self):
        """Modifie le preset personnalise actuellement selectionne."""
        idx = self.combo_preset.currentIndex()
        if not (0 <= idx < len(self.presets)):
            return
        p = self.presets[idx]
        if p.get("builtin"):
            QMessageBox.information(self, ct("comp_preset_edit"),
                                    ct("comp_preset_builtin"))
            return
        nom, ok = QInputDialog.getText(self, ct("comp_preset_edit"),
                                       ct("comp_preset_name"), text=p["name"])
        if not ok or not nom.strip():
            return
        nom = nom.strip()
        if any(q is not p and q["name"] == nom for q in self.presets):
            QMessageBox.warning(self, ct("comp_preset_edit"),
                                ct("comp_preset_exists"))
            return
        w, ok2 = QInputDialog.getInt(self, ct("comp_preset_edit"),
                                     ct("comp_width"), int(p["w"]), 64, 12000)
        if not ok2:
            return
        h, ok3 = QInputDialog.getInt(self, ct("comp_preset_edit"),
                                     ct("comp_height"), int(p["h"]), 64, 12000)
        if not ok3:
            return
        p["name"], p["w"], p["h"] = nom, w, h
        sauver_gabarits(self.templates, self.favoris, self.presets_perso)
        self._remplir_combo_presets()
        self.combo_preset.setCurrentIndex(idx)

    def _supprimer_preset(self):
        """Supprime le preset personnalise selectionne (les presets fournis
        ne sont pas supprimables)."""
        idx = self.combo_preset.currentIndex()
        if not (0 <= idx < len(self.presets)):
            return
        p = self.presets[idx]
        if p.get("builtin"):
            QMessageBox.information(self, ct("comp_preset_del"),
                                    ct("comp_preset_builtin"))
            return
        rep = QMessageBox.question(self, ct("comp_preset_del"),
                                   ct("comp_preset_confirm_del"),
                                   QMessageBox.Yes | QMessageBox.No)
        if rep != QMessageBox.Yes:
            return
        self.presets.remove(p)
        if p in self.presets_perso:
            self.presets_perso.remove(p)
        sauver_gabarits(self.templates, self.favoris, self.presets_perso)
        self._remplir_combo_presets()
        self.combo_preset.setCurrentIndex(0)
        self._appliquer_preset()

    def _dimensions_modifiees(self, valeur=None):
        if self.cb_ratio_lock.isChecked():
            sender = self.sender()
            ratio = getattr(self, "_ratio_sortie", None)
            if not ratio:
                ratio = self.spin_w.value() / max(1, self.spin_h.value())
            if sender is self.spin_w:
                self.spin_h.blockSignals(True)
                self.spin_h.setValue(max(64, int(self.spin_w.value() / ratio)))
                self.spin_h.blockSignals(False)
            elif sender is self.spin_h:
                self.spin_w.blockSignals(True)
                self.spin_w.setValue(max(64, int(self.spin_h.value() * ratio)))
                self.spin_w.blockSignals(False)
        else:
            # Les dimensions ne correspondent plus a un preset -> "Libre".
            if self.combo_preset.currentIndex() < self._index_libre():
                self.combo_preset.blockSignals(True)
                self.combo_preset.setCurrentIndex(self._index_libre())
                self.combo_preset.blockSignals(False)
        self._maj_ratio_grille()

    def _memoriser_ratio_sortie(self, valeur=None):
        self._ratio_sortie = self.spin_w.value() / max(1, self.spin_h.value())

    def _inverser_largeur_hauteur(self):
        """Echange les valeurs largeur et hauteur du format de sortie."""
        w, h = self.spin_w.value(), self.spin_h.value()
        self.spin_w.blockSignals(True)
        self.spin_h.blockSignals(True)
        self.spin_w.setValue(h)
        self.spin_h.setValue(w)
        self.spin_w.blockSignals(False)
        self.spin_h.blockSignals(False)
        # Le format devient "Libre" car les valeurs ne correspondent plus.
        if self.combo_preset.currentIndex() < self._index_libre():
            self.combo_preset.blockSignals(True)
            self.combo_preset.setCurrentIndex(self._index_libre())
            self.combo_preset.blockSignals(False)
        self._maj_ratio_grille()

    def _maj_ratio_grille(self):
        w, h = self.spin_w.value(), self.spin_h.value()
        if h > 0:
            self.grille.definir_ratio(w / h)
            if not self.cb_ratio_lock.isChecked():
                self._ratio_sortie = w / h

    # ==================================================================
    #  APPARENCE
    # ==================================================================
    def _maj_grille_apparence(self):
        self.grille.margin = self.spin_margin.value()
        self.grille._replacer_cellules()
        self.grille.update()

    def _maj_etat_bordure(self):
        """Met a jour l'etat des controles de bordure et rafraichit l'apercu."""
        actif = self.cb_bordure.isChecked()
        self.btn_bordure_color.setEnabled(actif)
        self.spin_bordure_epaisseur.setEnabled(actif)
        self._rafraichir_apercu()

    def _choisir_bordure_color(self):
        c = QColorDialog.getColor(QColor(self.bordure_color), self,
                                  ct("comp_border_color"))
        if c.isValid():
            self.bordure_color = c.name()
            self.btn_bordure_color.setStyleSheet(
                "background-color:%s;" % self.bordure_color)
            self._rafraichir_apercu()

    def _params_bordure(self):
        return {
            "enabled": self.cb_bordure.isChecked(),
            "color": self.bordure_color,
            "thickness": self.spin_bordure_epaisseur.value(),
        }

    def _maj_etat_filigrane(self):
        """Met a jour l'etat des controles de filigrane et rafraichit."""
        actif = self.cb_filigrane.isChecked()
        for w in [self.edit_filigrane, self.combo_filigrane_pos,
                  self.spin_filigrane_size, self.slider_filigrane_op]:
            w.setEnabled(actif)
        self._rafraichir_apercu()

    def _params_filigrane(self):
        return {
            "enabled": self.cb_filigrane.isChecked(),
            "text": self.edit_filigrane.text(),
            "position": self.combo_filigrane_pos.currentData(),
            "size": self.spin_filigrane_size.value(),
            "opacity": self.slider_filigrane_op.value(),
        }

    def _maj_grille_separateur(self):
        self.grille.separateur_actif = self.cb_separateur.isChecked()
        self.grille.separateur_couleur = self.sep_color
        self.grille.separateur_epaisseur = self.spin_sep_epaisseur.value()
        # Activer/desactiver les controles dependants.
        actif = self.cb_separateur.isChecked()
        self.btn_sep_color.setEnabled(actif)
        self.spin_sep_epaisseur.setEnabled(actif)
        self.grille._replacer_cellules()
        self.grille.update()

    def _choisir_bg_color(self):
        c = QColorDialog.getColor(QColor(self.bg_color), self, ct("comp_bg_color"))
        if c.isValid():
            self.bg_color = c.name()
            self.btn_bg_color.setStyleSheet("background-color:%s;" % self.bg_color)
            self.grille.bg_color = self.bg_color
            self.grille.update()

    def _choisir_sep_color(self):
        c = QColorDialog.getColor(QColor(self.sep_color), self,
                                  ct("comp_separator_color"))
        if c.isValid():
            self.sep_color = c.name()
            self.btn_sep_color.setStyleSheet("background-color:%s;" % self.sep_color)
            self._maj_grille_separateur()

    # ==================================================================
    #  ETIQUETTES / FAVORIS
    # ==================================================================
    def _remplir_combo_fav(self):
        self.combo_fav.clear()
        for f in self.favoris:
            self.combo_fav.addItem(f)

    def _ajouter_favori(self):
        nom, ok = QInputDialog.getText(self, ct("comp_add_fav"),
                                       ct("comp_fav_input"))
        if ok and nom.strip():
            self.favoris.append(nom.strip())
            sauver_gabarits(self.templates, self.favoris, self.presets_perso)
            self._remplir_combo_fav()
            self.combo_fav.setCurrentIndex(len(self.favoris) - 1)

    def _supprimer_favori(self):
        idx = self.combo_fav.currentIndex()
        if 0 <= idx < len(self.favoris):
            self.favoris.pop(idx)
            sauver_gabarits(self.templates, self.favoris, self.presets_perso)
            self._remplir_combo_fav()

    def _choisir_txt_color(self):
        c = QColorDialog.getColor(QColor(self.label_txt_color), self,
                                  ct("comp_label_txt_color"))
        if c.isValid():
            self.label_txt_color = c.name()
            self.btn_txt_color.setStyleSheet("background-color:%s;" % self.label_txt_color)
            self._rafraichir_apercu()

    def _choisir_label_bg(self):
        c = QColorDialog.getColor(QColor(self.label_bg_color), self,
                                  ct("comp_label_bg_color"))
        if c.isValid():
            self.label_bg_color = c.name()
            self.btn_label_bg.setStyleSheet("background-color:%s;" % self.label_bg_color)
            self._rafraichir_apercu()

    def _maj_etat_labels(self):
        actif = self.cb_label.isChecked()
        for w in [self.combo_pos, self.spin_label_size, self.btn_txt_color,
                  self.btn_label_bg, self.slider_label_op]:
            w.setEnabled(actif)
        self._rafraichir_apercu()

    def _editer_label_case(self, index):
        """Ouvre le dialogue de choix de texte pour l'etiquette d'une case."""
        if index < 0 or index >= len(self.grille.cellules):
            return
        cell = self.grille.cellules[index]
        dlg = DialogueLabelCase(cell, self.favoris, self)
        if dlg.exec_() == QDialog.Accepted:
            mode, texte = dlg.resultat()
            cell.label_mode = mode
            cell.label_text = texte
            self._rafraichir_apercu()
            self._enregistrer_historique()

    def _params_label(self):
        return {
            "enabled": self.cb_label.isChecked(),
            "position": self.combo_pos.currentData(),
            "size": self.spin_label_size.value(),
            "text_color": self.label_txt_color,
            "bg_color": self.label_bg_color,
            "bg_opacity": self.slider_label_op.value(),
        }

    # ==================================================================
    #  APERCU
    # ==================================================================
    def _on_grille_modifiee(self):
        self._rafraichir_apercu()
        # Toute modification de la grille cree un point d'annulation,
        # sauf si on est en train de restaurer un etat (gel actif).
        self._enregistrer_historique()

    def _rafraichir_apercu(self):
        """Redessine la grille et toutes les cellules (labels inclus)."""
        self.grille.update()
        for cell in self.grille.cellules:
            cell.update()
        # La superposition du filigrane se redessine elle aussi.
        if hasattr(self, "overlay_filigrane"):
            self.overlay_filigrane.raise_()
            self.overlay_filigrane.update()
        self.update()

    def eventFilter(self, obj, event):
        """Garde la superposition du filigrane a la meme taille que la grille
        et toujours au premier plan."""
        if obj is getattr(self, "grille", None) and hasattr(self, "overlay_filigrane"):
            if event.type() in (event.Resize, event.Show, event.ChildAdded,
                                event.ChildRemoved):
                self.overlay_filigrane.setGeometry(self.grille.rect())
                self.overlay_filigrane.raise_()
        return super().eventFilter(obj, event)

    # ==================================================================
    #  HISTORIQUE ANNULER / RETABLIR
    # ==================================================================
    def _enregistrer_historique(self):
        """Ajoute l'etat courant de la planche a la pile d'annulation."""
        if getattr(self, "_hist_gel", False):
            return
        if not hasattr(self, "_historique"):
            return
        etat = self._etat_projet()
        # Si on a annule puis modifie : on tronque la branche "retablir".
        if self._hist_index < len(self._historique) - 1:
            self._historique = self._historique[:self._hist_index + 1]
        # Eviter les doublons consecutifs identiques.
        if self._historique and self._historique[-1] == etat:
            return
        self._historique.append(etat)
        # Limiter la taille de l'historique (50 etats).
        if len(self._historique) > 50:
            self._historique.pop(0)
        self._hist_index = len(self._historique) - 1

    def _annuler(self):
        """Revient a l'etat precedent de la planche."""
        if not hasattr(self, "_historique") or self._hist_index <= 0:
            return
        self._hist_index -= 1
        self._restaurer_historique(self._historique[self._hist_index])

    def _retablir(self):
        """Avance vers l'etat suivant (apres une annulation)."""
        if not hasattr(self, "_historique"):
            return
        if self._hist_index >= len(self._historique) - 1:
            return
        self._hist_index += 1
        self._restaurer_historique(self._historique[self._hist_index])

    def _restaurer_historique(self, etat):
        """Applique un instantane sans le re-enregistrer dans l'historique."""
        self._hist_gel = True
        try:
            self._appliquer_projet(etat)
        finally:
            self._hist_gel = False

    # ==================================================================
    #  ACTIONS
    # ==================================================================
    def _nouvelle_planche(self):
        """Vide toutes les cases pour repartir d'une planche vierge."""
        if self.grille.cellules_remplies():
            rep = QMessageBox.question(self, ct("comp_new_board"),
                                       ct("comp_new_board_confirm"),
                                       QMessageBox.Yes | QMessageBox.No)
            if rep != QMessageBox.Yes:
                return
        self.grille.vider_images()
        self._rafraichir_apercu()

    def _reinitialiser_cadrage(self):
        """Recentre et dezoom toutes les cases remplies de la planche."""
        if not self.grille.cellules_remplies():
            QMessageBox.information(self, ct("comp_title"), ct("comp_no_image"))
            return
        self.grille.reinitialiser_cadrage()
        self._rafraichir_apercu()
        QMessageBox.information(self, ct("comp_title"), ct("comp_reset_all_done"))

    def _verifier_images(self):
        if not self.grille.cellules_remplies():
            QMessageBox.information(self, ct("comp_title"), ct("comp_no_image"))
            return False
        return True

    def _copier(self):
        if not self._verifier_images():
            return
        pix = generer_pixmap_compilation(self.grille, self.spin_w.value(),
                                         self.spin_h.value(), self._params_label(),
                                         self._params_bordure(),
                                         self._params_filigrane())
        QApplication.clipboard().setPixmap(pix)
        QMessageBox.information(self, ct("comp_title"), ct("comp_copied"))

    def _statut(self, message, succes=True, duree_ms=6000):
        """Affiche un message dans le pied de page (sans fenetre bloquante)."""
        couleur = "#46cd82" if succes else "#e0483a"
        self.barre_statut.setStyleSheet(
            "QLabel { background-color:#161f2e; color:%s; border-top:1px "
            "solid #283750; padding:5px 12px; font-size:12px; "
            "font-weight:bold; }" % couleur)
        self.barre_statut.setText(message)
        if duree_ms > 0:
            self._timer_statut.start(duree_ms)

    def _exporter(self):
        """Exporte la compilation immediatement (sans dialogue de
        confirmation). Le resultat est annonce dans le pied de page."""
        if not self.grille.cellules_remplies():
            self._statut(ct("comp_no_image"), succes=False)
            return
        # Dossier de sortie : celui de la premiere image placee.
        remplies = self.grille.cellules_remplies()
        dossier = ""
        if remplies and remplies[0].chemin:
            dossier = os.path.dirname(remplies[0].chemin)
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        chemin = os.path.join(dossier, "Compilation_%s.png" % timestamp)
        compteur = 1
        while os.path.exists(chemin):
            chemin = os.path.join(dossier,
                                  "Compilation_%s_%d.png" % (timestamp, compteur))
            compteur += 1
        try:
            pix = generer_pixmap_compilation(self.grille, self.spin_w.value(),
                                             self.spin_h.value(),
                                             self._params_label(),
                                             self._params_bordure(),
                                             self._params_filigrane())
            pix.save(chemin, "PNG")
            # Succes : message dans le pied de page, pas de fenetre.
            self._statut(ct("comp_export_status", path=chemin), succes=True)
        except Exception as e:
            self._statut(ct("comp_export_err", err=str(e)), succes=False)

    # ==================================================================
    #  VOLET DES PACKS DE COMPILATION  (generation de masse)
    # ==================================================================
    #  Chaque pack represente une future planche. Tous les packs partagent
    #  le gabarit et les reglages actuels ; seul le contenu des cases (les
    #  images et leur ajustement) est propre a chaque pack.
    #
    #  Modele de donnees : self.batch_packs est une liste de dicts
    #      { "nom": str, "cases": [ <etat de cellule>, ... ] }
    #  ou chaque <etat de cellule> a la meme forme que dans _etat_projet.
    #  self.batch_index pointe sur le pack actuellement charge dans la
    #  grille (-1 = aucun).
    # ==================================================================
    def _mode_import_packs(self):
        if getattr(self, "rb_import_dynamique", None) is not None:
            return "dynamique" if self.rb_import_dynamique.isChecked() else "gabarit"
        return "gabarit"

    def _sauver_mode_import(self, checked=False):
        if not checked:
            return
        cfg = _cfg()
        if cfg is not None:
            cfg.set("compilation_import_mode", self._mode_import_packs())

    def _etat_case_vide(self, chemin=None):
        return {"chemin": chemin, "offset_x": 0.5, "offset_y": 0.5,
                "cell_zoom": 1.0, "rotation": 0,
                "label_mode": "auto", "label_text": ""}

    def _mime_contient_images(self, mime):
        if not mime or not mime.hasUrls():
            return False
        for url in mime.urls():
            chemin = url.toLocalFile()
            if chemin and chemin.lower().endswith(IMAGE_EXTENSIONS):
                return True
        return False

    def _chemins_images_depuis_mime(self, mime):
        chemins = []
        vus = set()
        if not mime or not mime.hasUrls():
            return chemins
        for url in mime.urls():
            chemin = url.toLocalFile()
            cle = os.path.normcase(os.path.abspath(chemin)) if chemin else ""
            if (chemin and cle not in vus and os.path.isfile(chemin)
                    and chemin.lower().endswith(IMAGE_EXTENSIONS)):
                pix = QPixmap(chemin)
                if not pix.isNull():
                    vus.add(cle)
                    chemins.append(chemin)
        return sorted(chemins, key=_cle_tri_naturel)

    def _drag_packs_enter(self, event):
        if self._mime_contient_images(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def _drop_images_packs(self, event):
        chemins = self._chemins_images_depuis_mime(event.mimeData())
        if not chemins:
            event.ignore()
            return
        if self._mode_import_packs() == "dynamique":
            nb_packs = self._creer_pack_dynamique_depuis_images(chemins)
        else:
            nb_packs = self._creer_packs_depuis_images(chemins)
        self._statut(ct("comp_batch_drop_created",
                        packs=nb_packs, images=len(chemins)),
                     succes=True, duree_ms=5000)
        event.acceptProposedAction()

    def _creer_packs_depuis_images(self, chemins):
        """Cree des packs par groupes de rows*cols images."""
        self._sauver_pack_courant()
        nb_cases = max(1, self.grille.rows * self.grille.cols)
        premier_index = len(self.batch_packs)
        nb_crees = 0
        for debut in range(0, len(chemins), nb_cases):
            groupe = chemins[debut:debut + nb_cases]
            cases = []
            for i in range(nb_cases):
                chemin = groupe[i] if i < len(groupe) else None
                cases.append(self._etat_case_vide(chemin))
            self.batch_packs.append({
                "nom": ct("comp_batch_pack_name",
                          n=len(self.batch_packs) + 1),
                "cases": cases,
            })
            nb_crees += 1
        self._rafraichir_liste_packs()
        if nb_crees:
            self.liste_packs.setCurrentRow(premier_index)
        return nb_crees

    def _creer_pack_dynamique_depuis_images(self, chemins):
        """Cree un seul pack et adapte la grille au nombre d'images."""
        self._sauver_pack_courant()
        n = max(1, len(chemins))
        cols = int(math.ceil(math.sqrt(n)))
        rows = int(math.ceil(n / cols))
        nb_cases = rows * cols

        self.spin_rows.blockSignals(True)
        self.spin_cols.blockSignals(True)
        self.spin_rows.setMaximum(max(self.spin_rows.maximum(), rows))
        self.spin_cols.setMaximum(max(self.spin_cols.maximum(), cols))
        self.spin_rows.setValue(rows)
        self.spin_cols.setValue(cols)
        self.spin_rows.blockSignals(False)
        self.spin_cols.blockSignals(False)
        self.grille.appliquer_gabarit(rows, cols)
        self._maj_texte_orientation()

        cases = []
        for i in range(nb_cases):
            chemin = chemins[i] if i < len(chemins) else None
            cases.append(self._etat_case_vide(chemin))

        premier_index = len(self.batch_packs)
        self.batch_packs.append({
            "nom": ct("comp_batch_pack_name", n=len(self.batch_packs) + 1),
            "cases": cases,
        })
        self._rafraichir_liste_packs()
        self.liste_packs.setCurrentRow(premier_index)
        return 1

    def _cases_serialisees(self):
        """Retourne l'etat serialisable des cellules de la grille (images,
        cadrage, rotation, etiquettes). Meme forme que _etat_projet."""
        cases = []
        for c in self.grille.cellules:
            cases.append({
                "chemin": c.chemin,
                "offset_x": c.offset_x, "offset_y": c.offset_y,
                "cell_zoom": c.cell_zoom,
                "rotation": getattr(c, "rotation", 0),
                "label_mode": c.label_mode, "label_text": c.label_text,
            })
        return cases

    def _appliquer_cases(self, cases):
        """Applique une liste d'etats de cellules a la grille actuelle.
        Les cases excedentaires sont videes ; une image introuvable est
        ignoree sans bloquer."""
        manquants = []
        for i, cell in enumerate(self.grille.cellules):
            precedent = cell.blockSignals(True)
            try:
                if i < len(cases):
                    info = cases[i]
                    chemin_img = info.get("chemin")
                    if chemin_img and os.path.exists(chemin_img):
                        if cell.definir_image(chemin_img):
                            cell.offset_x = info.get("offset_x", 0.5)
                            cell.offset_y = info.get("offset_y", 0.5)
                            cell.cell_zoom = info.get("cell_zoom", 1.0)
                            cell.rotation = int(info.get("rotation", 0)) % 360
                        else:
                            manquants.append(chemin_img)
                            cell.vider()
                    else:
                        if chemin_img:
                            manquants.append(chemin_img)
                        cell.vider()
                    cell.label_mode = info.get("label_mode", "auto")
                    cell.label_text = info.get("label_text", "")
                else:
                    cell.vider()
            finally:
                cell.blockSignals(precedent)
            cell.update()
        if manquants:
            self._statut(ct("comp_missing_image", path=manquants[0]),
                         succes=False, duree_ms=6000)

    def _sauver_pack_courant(self):
        """Enregistre l'etat actuel de la grille dans le pack selectionne.
        Appele avant de basculer vers un autre pack ou de generer."""
        if 0 <= self.batch_index < len(self.batch_packs):
            self.batch_packs[self.batch_index]["cases"] = \
                self._cases_serialisees()

    def _vignette_pack(self, pack):
        """Retourne un QPixmap miniature : 1re image non vide du pack."""
        for case in pack.get("cases", []):
            chemin = case.get("chemin")
            if chemin and os.path.exists(chemin):
                return QPixmap(chemin).scaled(46, 46, Qt.KeepAspectRatio,
                                              Qt.SmoothTransformation)
        return QPixmap()

    def _rafraichir_liste_packs(self):
        """Reconstruit la liste visuelle des packs (nom + vignette)."""
        self.liste_packs.blockSignals(True)
        self.liste_packs.clear()
        for pack in self.batch_packs:
            item = QListWidgetItem(pack.get("nom", "?"))
            pix = self._vignette_pack(pack)
            if not pix.isNull():
                item.setIcon(QIcon(pix))
            self.liste_packs.addItem(item)
        self.liste_packs.blockSignals(False)
        # Etat du bouton Generer : actif s'il existe au moins un pack.
        self.btn_batch_gen.setEnabled(bool(self.batch_packs))

    def _ajouter_pack(self):
        """Cree un nouveau pack vide (autant de cases que la grille) et le
        selectionne aussitot pour edition."""
        # On memorise l'etat du pack courant avant de changer.
        self._sauver_pack_courant()
        nb_cases = len(self.grille.cellules)
        cases_courantes = self._cases_serialisees()
        utiliser_cases_courantes = (
            self.batch_index == -1 and
            any(c.get("chemin") for c in cases_courantes)
        )
        pack = {
            "nom": ct("comp_batch_pack_name", n=len(self.batch_packs) + 1),
            "cases": (cases_courantes if utiliser_cases_courantes else
                      [self._etat_case_vide()
                       for _ in range(nb_cases)]),
        }
        self.batch_packs.append(pack)
        self.batch_index = len(self.batch_packs) - 1
        self._rafraichir_liste_packs()
        self.liste_packs.setCurrentRow(self.batch_index)
        if not utiliser_cases_courantes:
            # Grille videe pour le nouveau pack.
            self._appliquer_cases(pack["cases"])
        self._rafraichir_apercu()
        self._statut(ct("comp_batch_add"), succes=True, duree_ms=2500)

    def _supprimer_pack(self):
        """Supprime le pack selectionne."""
        idx = self.liste_packs.currentRow()
        if idx < 0 or idx >= len(self.batch_packs):
            return
        self.batch_packs.pop(idx)
        # On reajuste l'index courant.
        if not self.batch_packs:
            self.batch_index = -1
        else:
            self.batch_index = min(idx, len(self.batch_packs) - 1)
        self._rafraichir_liste_packs()
        if self.batch_index >= 0:
            self.liste_packs.setCurrentRow(self.batch_index)
        else:
            # Plus aucun pack : grille videe.
            for cell in self.grille.cellules:
                cell.vider()
            self._rafraichir_apercu()

    def _menu_pack(self, pos):
        item = self.liste_packs.itemAt(pos)
        if item is None:
            return
        idx = self.liste_packs.row(item)
        if idx < 0 or idx >= len(self.batch_packs):
            return
        menu = QMenu(self)
        act_renommer = menu.addAction(ct("comp_batch_rename"))
        act_dupliquer = menu.addAction(ct("comp_batch_duplicate"))
        act_vider = menu.addAction(ct("comp_batch_clear_images"))
        menu.addSeparator()
        act_supprimer = menu.addAction(ct("comp_batch_del"))
        action = menu.exec_(self.liste_packs.mapToGlobal(pos))
        if action == act_renommer:
            self._renommer_pack(item)
        elif action == act_dupliquer:
            self._dupliquer_pack(idx)
        elif action == act_vider:
            self._vider_images_pack(idx)
        elif action == act_supprimer:
            self.liste_packs.setCurrentRow(idx)
            self._supprimer_pack()

    def _dupliquer_pack(self, idx):
        if idx < 0 or idx >= len(self.batch_packs):
            return
        self._sauver_pack_courant()
        pack = copy.deepcopy(self.batch_packs[idx])
        pack["nom"] = "%s (copie)" % pack.get("nom", ct("comp_batch_pack_name", n=idx + 1))
        self.batch_packs.insert(idx + 1, pack)
        self.batch_index = idx + 1
        self._rafraichir_liste_packs()
        self.liste_packs.blockSignals(True)
        self.liste_packs.setCurrentRow(self.batch_index)
        self.liste_packs.blockSignals(False)
        self._appliquer_cases(pack["cases"])
        self._rafraichir_apercu()

    def _vider_images_pack(self, idx):
        if idx < 0 or idx >= len(self.batch_packs):
            return
        nb_cases = len(self.batch_packs[idx].get("cases", []))
        if nb_cases <= 0:
            nb_cases = len(self.grille.cellules)
        self.batch_packs[idx]["cases"] = [self._etat_case_vide()
                                          for _ in range(nb_cases)]
        self.batch_index = idx
        self._rafraichir_liste_packs()
        self.liste_packs.blockSignals(True)
        self.liste_packs.setCurrentRow(idx)
        self.liste_packs.blockSignals(False)
        self._appliquer_cases(self.batch_packs[idx]["cases"])
        self._rafraichir_apercu()

    def _renommer_pack(self, item):
        """Renomme le pack (double-clic sur son entree dans la liste)."""
        idx = self.liste_packs.row(item)
        if idx < 0 or idx >= len(self.batch_packs):
            return
        actuel = self.batch_packs[idx].get("nom", "")
        nouveau, ok = QInputDialog.getText(
            self, ct("comp_batch_rename"),
            ct("comp_batch_rename_prompt"), text=actuel)
        if ok and nouveau.strip():
            self.batch_packs[idx]["nom"] = nouveau.strip()
            self._rafraichir_liste_packs()
            self.liste_packs.setCurrentRow(idx)

    def _changer_pack(self, idx):
        """Bascule vers le pack d'indice idx : sauvegarde le pack quitte,
        charge le nouveau dans la grille."""
        if idx < 0 or idx >= len(self.batch_packs):
            return
        # Sauvegarde du pack courant avant de recharger la grille.
        self._sauver_pack_courant()
        self.batch_index = idx
        self._appliquer_cases(self.batch_packs[idx]["cases"])
        self._rafraichir_apercu()

    def _generer_tous_les_packs(self):
        """Genere une planche PNG par pack. Tous les packs utilisent le
        gabarit et les reglages actuels ; seules les images different.
        L'etat de la grille est restaure a la fin."""
        # On enregistre d'abord le pack en cours d'edition.
        self._sauver_pack_courant()
        if not self.batch_packs:
            QMessageBox.information(self, ct("comp_title"),
                                    ct("comp_batch_none"))
            return

        # Dossier de sortie choisi par l'utilisateur.
        dossier = QFileDialog.getExistingDirectory(
            self, ct("comp_batch_choose_out"))
        if not dossier:
            return

        # Sauvegarde de l'etat courant de la grille (pour restauration).
        etat_grille = self._cases_serialisees()

        import time
        horodatage = time.strftime("%Y%m%d_%H%M%S")
        nb_ok = 0
        nb_skip = 0
        try:
            for i, pack in enumerate(self.batch_packs):
                cases = pack.get("cases", [])
                # Un pack sans aucune image valide est ignore.
                a_une_image = any(
                    c.get("chemin") and os.path.exists(c.get("chemin"))
                    for c in cases)
                if not a_une_image:
                    nb_skip += 1
                    continue
                # On applique le pack a la grille puis on exporte.
                self._appliquer_cases(cases)
                pix = generer_pixmap_compilation(
                    self.grille, self.spin_w.value(), self.spin_h.value(),
                    self._params_label(), self._params_bordure(),
                    self._params_filigrane())
                nom = "Compilation_%s_%03d.png" % (horodatage, i + 1)
                pix.save(os.path.join(dossier, nom), "PNG")
                nb_ok += 1
        finally:
            # Restauration de la grille telle qu'avant la generation.
            self._appliquer_cases(etat_grille)
            self._rafraichir_apercu()

        message = ct("comp_batch_done", count=nb_ok, path=dossier)
        if nb_skip:
            message += "\n" + ct("comp_batch_skipped", skipped=nb_skip)
        QMessageBox.information(self, ct("comp_title"), message)

    # ==================================================================
    #  SAUVEGARDE / OUVERTURE D'UN PROJET DE COMPILATION
    # ==================================================================
    def _etat_projet(self):
        """Construit un dictionnaire JSON-serialisable decrivant la planche
        complete : grille, format, separateur, etiquettes, contenu des cases."""
        cases = []
        for c in self.grille.cellules:
            cases.append({
                "chemin": c.chemin,
                "offset_x": c.offset_x, "offset_y": c.offset_y,
                "cell_zoom": c.cell_zoom,
                "rotation": getattr(c, "rotation", 0),
                "label_mode": c.label_mode, "label_text": c.label_text,
            })
        return {
            "_type": "comparateur_pro_compilation",
            "version": 4,
            "rows": self.grille.rows, "cols": self.grille.cols,
            "margin": self.spin_margin.value(),
            "bg_color": self.bg_color,
            "output_w": self.spin_w.value(),
            "output_h": self.spin_h.value(),
            "separateur_actif": self.cb_separateur.isChecked(),
            "separateur_couleur": self.sep_color,
            "separateur_epaisseur": self.spin_sep_epaisseur.value(),
            "bordure_active": self.cb_bordure.isChecked(),
            "bordure_couleur": self.bordure_color,
            "bordure_epaisseur": self.spin_bordure_epaisseur.value(),
            "filigrane_actif": self.cb_filigrane.isChecked(),
            "filigrane_texte": self.edit_filigrane.text(),
            "filigrane_position": self.combo_filigrane_pos.currentData(),
            "filigrane_size": self.spin_filigrane_size.value(),
            "filigrane_opacity": self.slider_filigrane_op.value(),
            "label_enabled": self.cb_label.isChecked(),
            "label_position": self.combo_pos.currentData(),
            "label_size": self.spin_label_size.value(),
            "label_txt_color": self.label_txt_color,
            "label_bg_color": self.label_bg_color,
            "label_bg_opacity": self.slider_label_op.value(),
            "cases": cases,
        }

    def _sauver_projet(self):
        """Enregistre la planche dans un fichier .comproj (JSON)."""
        import time
        defaut = "Projet_%s.comproj" % time.strftime("%Y%m%d_%H%M%S")
        # Dossier suggere : celui de la premiere image, sinon dossier courant.
        remplies = self.grille.cellules_remplies()
        dossier = ""
        if remplies and remplies[0].chemin:
            dossier = os.path.dirname(remplies[0].chemin)
        chemin, _ = QFileDialog.getSaveFileName(
            self, ct("comp_save_project"), os.path.join(dossier, defaut),
            "Projet de compilation (*.comproj)")
        if not chemin:
            return
        if not chemin.lower().endswith(".comproj"):
            chemin += ".comproj"
        try:
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(self._etat_projet(), f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, ct("comp_title"),
                                    ct("comp_project_saved", path=chemin))
        except Exception as e:
            QMessageBox.critical(self, ct("comp_title"),
                                 ct("comp_project_err", err=str(e)))

    def _ouvrir_projet(self):
        """Recharge une planche depuis un fichier .comproj."""
        chemin, _ = QFileDialog.getOpenFileName(
            self, ct("comp_open_project"), "",
            "Projet de compilation (*.comproj)")
        if not chemin:
            return
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("_type") != "comparateur_pro_compilation":
                raise ValueError("format non reconnu")
        except Exception as e:
            QMessageBox.critical(self, ct("comp_title"),
                                 ct("comp_project_err", err=str(e)))
            return
        self._appliquer_projet(data)
        QMessageBox.information(self, ct("comp_title"),
                                ct("comp_project_loaded"))

    def _appliquer_projet(self, data):
        """Applique un dictionnaire de projet a l'interface et a la grille."""
        # Format de sortie.
        self.spin_w.blockSignals(True)
        self.spin_h.blockSignals(True)
        self.spin_w.setValue(int(data.get("output_w", 1600)))
        self.spin_h.setValue(int(data.get("output_h", 900)))
        self.spin_w.blockSignals(False)
        self.spin_h.blockSignals(False)
        self.combo_preset.blockSignals(True)
        self.combo_preset.setCurrentIndex(self._index_libre())  # "Libre"
        self.combo_preset.blockSignals(False)

        # Marge et fond.
        self.spin_margin.blockSignals(True)
        self.spin_margin.setValue(int(data.get("margin", 12)))
        self.spin_margin.blockSignals(False)
        self.bg_color = data.get("bg_color", COL_FOND)
        self.btn_bg_color.setStyleSheet("background-color:%s;" % self.bg_color)

        # Separateur.
        self.cb_separateur.blockSignals(True)
        self.cb_separateur.setChecked(bool(data.get("separateur_actif", True)))
        self.cb_separateur.blockSignals(False)
        self.sep_color = data.get("separateur_couleur", "#ffffff")
        self.btn_sep_color.setStyleSheet("background-color:%s;" % self.sep_color)
        self.spin_sep_epaisseur.blockSignals(True)
        self.spin_sep_epaisseur.setValue(int(data.get("separateur_epaisseur", 6)))
        self.spin_sep_epaisseur.blockSignals(False)

        # Bordure par image.
        self.cb_bordure.blockSignals(True)
        self.cb_bordure.setChecked(bool(data.get("bordure_active", False)))
        self.cb_bordure.blockSignals(False)
        self.bordure_color = data.get("bordure_couleur", "#ffffff")
        self.btn_bordure_color.setStyleSheet(
            "background-color:%s;" % self.bordure_color)
        self.spin_bordure_epaisseur.blockSignals(True)
        self.spin_bordure_epaisseur.setValue(int(data.get("bordure_epaisseur", 4)))
        self.spin_bordure_epaisseur.blockSignals(False)

        # Filigrane global.
        self.cb_filigrane.blockSignals(True)
        self.cb_filigrane.setChecked(bool(data.get("filigrane_actif", False)))
        self.cb_filigrane.blockSignals(False)
        self.edit_filigrane.blockSignals(True)
        self.edit_filigrane.setText(data.get("filigrane_texte", ""))
        self.edit_filigrane.blockSignals(False)
        pos_f = data.get("filigrane_position", "br")
        if pos_f in POSITIONS:
            self.combo_filigrane_pos.blockSignals(True)
            self.combo_filigrane_pos.setCurrentIndex(POSITIONS.index(pos_f))
            self.combo_filigrane_pos.blockSignals(False)
        self.spin_filigrane_size.blockSignals(True)
        self.spin_filigrane_size.setValue(int(data.get("filigrane_size", 28)))
        self.spin_filigrane_size.blockSignals(False)
        self.slider_filigrane_op.blockSignals(True)
        self.slider_filigrane_op.setValue(int(data.get("filigrane_opacity", 160)))
        self.slider_filigrane_op.blockSignals(False)

        # Etiquettes.
        self.cb_label.blockSignals(True)
        self.cb_label.setChecked(bool(data.get("label_enabled", True)))
        self.cb_label.blockSignals(False)
        pos = data.get("label_position", "bl")
        if pos in POSITIONS:
            self.combo_pos.blockSignals(True)
            self.combo_pos.setCurrentIndex(POSITIONS.index(pos))
            self.combo_pos.blockSignals(False)
        self.spin_label_size.blockSignals(True)
        self.spin_label_size.setValue(int(data.get("label_size", 16)))
        self.spin_label_size.blockSignals(False)
        self.label_txt_color = data.get("label_txt_color", "#ffffff")
        self.btn_txt_color.setStyleSheet("background-color:%s;" % self.label_txt_color)
        self.label_bg_color = data.get("label_bg_color", "#000000")
        self.btn_label_bg.setStyleSheet("background-color:%s;" % self.label_bg_color)
        self.slider_label_op.blockSignals(True)
        self.slider_label_op.setValue(int(data.get("label_bg_opacity", 150)))
        self.slider_label_op.blockSignals(False)

        # Grille : dimensions puis contenu des cases.
        rows = int(data.get("rows", 2))
        cols = int(data.get("cols", 2))
        self.spin_rows.blockSignals(True)
        self.spin_cols.blockSignals(True)
        self.spin_rows.setValue(rows)
        self.spin_cols.setValue(cols)
        self.spin_rows.blockSignals(False)
        self.spin_cols.blockSignals(False)
        grille_signaux = self.grille.blockSignals(True)
        try:
            self.grille.appliquer_gabarit(rows, cols)
            self._appliquer_cases(data.get("cases", []))
        finally:
            self.grille.blockSignals(grille_signaux)

        # Mise a jour de l'affichage.
        self.grille.bg_color = self.bg_color
        self.grille.margin = self.spin_margin.value()
        self._maj_grille_separateur()
        self._maj_ratio_grille()
        self._maj_etat_labels()
        self._maj_texte_orientation()
        self._rafraichir_apercu()

    # ==================================================================
    #  CLAVIER : Suppr vide la case, Ctrl+Z / Ctrl+Y annulent / retablissent
    # ==================================================================
    def keyPressEvent(self, event):
        ctrl = bool(event.modifiers() & Qt.ControlModifier)
        if not ctrl and event.key() in (Qt.Key_Tab, Qt.Key_Backtab):
            if self.grille.cellules:
                idx = getattr(self.grille, "_index_selection", -1)
                if idx < 0:
                    nouveau = 0
                elif event.key() == Qt.Key_Backtab or event.modifiers() & Qt.ShiftModifier:
                    nouveau = (idx - 1) % len(self.grille.cellules)
                else:
                    nouveau = (idx + 1) % len(self.grille.cellules)
                self.grille._selectionner(nouveau)
                return
        # Ctrl+S : export rapide de la compilation (sans dialogue).
        if ctrl and event.key() == Qt.Key_S:
            self._exporter()
            return
        # Annuler / Retablir.
        if ctrl and event.key() == Qt.Key_Z:
            self._annuler()
            return
        if ctrl and (event.key() == Qt.Key_Y
                     or (event.key() == Qt.Key_Z
                         and event.modifiers() & Qt.ShiftModifier)):
            self._retablir()
            return
        # Suppr : vide la case selectionnee.
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            case = self.grille.case_selectionnee()
            if case is not None:
                case.vider()
                self._rafraichir_apercu()
                return
        super().keyPressEvent(event)


# ==============================================================================
#  POINTS D'ENTREE PUBLICS
# ==============================================================================
def creer_widget_compilation(parent=None):
    """Retourne le panneau de compilation pret a inserer comme onglet."""
    return WidgetCompilation(parent)


def ouvrir_fenetre_compilation(parent=None):
    """Ouvre la compilation dans une fenetre independante (mode optionnel)."""
    dlg = QDialog(parent)
    dlg.setWindowTitle(ct("comp_title"))
    dlg.resize(1280, 820)
    dlg.setMinimumSize(900, 600)
    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(WidgetCompilation(dlg))
    dlg.show()
    return dlg

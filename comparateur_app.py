import sys
import io

# --- CORRECTIF CRITIQUE POUR PYW ---
# Empêche PyQt5 de crasher silencieusement s'il essaie de logger une info sans console
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()
# -----------------------------------

import os
import time
import json
import glob
import tempfile
import locale
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QStackedWidget, QFrame, QMessageBox, QListWidget, 
                             QListWidgetItem, QAbstractItemView, QDialog, QSpinBox, 
                             QSlider, QColorDialog, QCheckBox, QComboBox, QLineEdit,
                             QTabWidget)
from PyQt5.QtGui import (QPainter, QPixmap, QPen, QFont, QColor, QCursor, QImage, QIcon)
from PyQt5.QtCore import Qt, QRect, QRectF, QSize, QBuffer, QIODevice, pyqtSignal, QTimer

def global_exception_handler(exctype, value, traceback_obj):
    import traceback
    err_msg = "".join(traceback.format_exception(exctype, value, traceback_obj))
    try:
        with open(os.path.join(tempfile.gettempdir(), "comparateur_crash.log"), "w") as f:
            f.write(err_msg)
        from PyQt5.QtWidgets import QApplication, QMessageBox
        if not QApplication.instance():
            app = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Erreur Critique / Critical Error")
        msg.setText("Le logiciel a rencontré une erreur fatale :\n\n" + err_msg)
        msg.exec_()
    except: pass
    sys.exit(1)

sys.excepthook = global_exception_handler

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
FICHIER_CONFIG = os.path.join(DOSSIER_SCRIPT, "comparateur_config.json")


def ecrire_log_erreur(contexte, exception):
    """Ajoute une erreur non bloquante au journal de diagnostic."""
    try:
        chemin_log = os.path.join(tempfile.gettempdir(), "comparateur_crash.log")
        with open(chemin_log, "a", encoding="utf-8") as f:
            f.write("\n\n[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), contexte))
            f.write("".join(traceback.format_exception_only(type(exception), exception)))
    except Exception:
        pass

# ==========================================
# DICTIONNAIRE MULTILINGUE (i18n)
# ==========================================
LANGUAGES = {
    "en": {
        "app_title": "Pro Comparator (Ctrl+Scroll to Zoom, Right-click to Pan)",
        "settings_title": "Premium Settings",
        "language": "Language / Langue :",
        "cursor_color": "Cursor color:",
        "cursor_thickness": "Cursor thickness:",
        "label_size": "Label text size:",
        "label_opacity": "Label background opacity:",
        "watermark_enable": "Enable watermark on export",
        "watermark_text": "Watermark text:",
        "close": "Close",
        "export_title": "Export",
        "export_labels": "Include information labels",
        "export_zoom": "Export only the current zoomed area",
        "format": "Format:",
        "export_btn": "Export...",
        "heatmap_title": "Difference Analysis (Heatmap)",
        "heatmap_info": "🔥 Heatmap: RED areas indicate strong differences.",
        "heatmap_global": "🔥 Global Heatmap ({count} images): Cumulative differences.",
        "my_comparisons": "My Comparisons",
        "new_pack": "+ New Pack",
        "del_pack": "Delete this pack",
        "clear_list": "Clear list",
        "recent_btn": "🕘 Recent",
        "recent_title": "Recent comparisons",
        "recent_empty": "No recent comparisons yet.",
        "recent_open": "Open",
        "recent_clear": "Clear history",
        "recent_missing": "Some images of this comparison are missing and were skipped.",
        "recent_gone": "None of this comparison's images could be found.",
        "recent_not_enough": "Not enough valid images remain to open this comparison.",
        "vertical": "⬍ Vertical",
        "horizontal": "⬌ Horizontal",
        "center": "Center",
        "originals": "↺ Originals",
        "auto_align": "🪄 Auto-Align",
        "heatmap_btn": "🔥 Difference (Heatmap)",
        "copy": "Copy (Ctrl+C)",
        "settings": "⚙ Settings",
        "export": "Export",
        "drop_text": "Drag & Drop your images here\nto create a new pack",
        "add_img": "+ Add image",
        "remove_img": "- Remove image",
        "warn_min_images": "Please drop at least 2 images to create a new pack.",
        "warn_pack_min": "A pack must contain at least 2 images to be compared.",
        "info_sel_img": "Select an image in the bottom bar to remove it.",
        "clear_confirm": "Do you really want to delete the entire pack history?",
        "align_start": "Alignment will start. Click OK to begin.",
        "align_success": "All images have been aligned and cropped to the first one!",
        "err_sim": "Not enough similarities with image {idx}.",
        "err_trans": "Cannot calculate a reliable transformation for image {idx}.",
        "err_align": "Alignment failed:\n{err}",
        "copied": "The comparison has been copied to the clipboard!",
        "exp_success": "Quick export complete!\n\nSaved in:\n{path}",
        "gif_success": "Animated GIF successfully generated!",
        "err_gif": "Error generating GIF: {err}",
        "err_gen": "Generation error:\n{err}",
        "missing_dep": "Requires OpenCV. Open CMD and type:\npip install opencv-python numpy",
        "invalid_image_skip": "Unreadable image skipped: {path}",
        "diff_failed_status": "Pixel difference failed; back to slider mode.",
        "close_compilation_packs": "Compilation packs are still open. Close anyway?",
        "restart_lang": "Please restart the application to apply the language change.",
        "img_word": "img",
        "warning": "Warning",
        "info": "Information",
        "success": "Success",
        "error": "Error",
        "tab_comparateur": "Comparator",
        "tab_compilation": "Compilation",
        "shortcuts_title": "Keyboard shortcuts",
        "shortcuts_section_general": "General",
        "shortcuts_section_compare": "Comparator view",
        "shortcuts_section_compil": "Compilation view",
        "sc_fullscreen": "Toggle fullscreen",
        "sc_copy": "Copy to clipboard",
        "sc_export": "Open export dialog",
        "sc_quick_export": "Quick 1:1 JPEG export",
        "sc_delete_pack": "Delete selected pack / image",
        "sc_next_pack": "Next / previous pack",
        "sc_switch_tabs": "Switch Comparator / Compilation tab",
        "sc_zoom": "Zoom in / out",
        "sc_pan": "Pan the view",
        "sc_blink": "Blink mode (reference vs current)",
        "sc_undo": "Undo cursor move",
        "sc_move_cursor": "Nudge the first cursor",
        "sc_comp_select": "Select a cell (single click)",
        "sc_comp_delete": "Clear the selected cell",
        "sc_comp_swap": "Swap two cells (Ctrl + drag & drop)",
        "sc_comp_adjust": "Reposition image inside a cell (drag)",
        "sc_comp_zoom_cell": "Zoom image inside a cell (wheel)",
        "sc_comp_undo": "Undo last action",
        "sc_comp_redo": "Redo last action",
        "sc_comp_export": "Quick export of the compilation",
        "sc_comp_next_cell": "Select next / previous cell",
        "settings_language_section": "Language",
        "settings_export_lang": "Export language file...",
        "settings_import_lang": "Import language file...",
        "settings_lang_exported": "Language template exported:\n{path}",
        "settings_lang_imported": "Language imported: {name}\nRestart to apply if needed.",
        "settings_lang_err": "Could not read this language file.",
        "settings_shortcuts_btn": "View keyboard shortcuts",
        "settings_translate_help": "To translate the app: export a language file, edit the texts, then import it back.",
        "view_mode": "View mode:",
        "view_mode_slider": "Slider compare",
        "view_mode_side": "Side by side",
        "view_mode_diff": "Pixel difference",
        "side_gap": "Gap between images:",
        "loupe_enable": "🔎 Magnifier (Loupe)",
        "loupe_zoom": "Loupe zoom:",
        "diff_btn": "🔬 Pixel difference",
        "diff_title": "Pixel Difference (subtraction)",
        "diff_info": "🔬 Pixel difference: brighter areas changed more.",
        "similarity_btn": "📊 Similarity score",
        "similarity_title": "Similarity measure",
        "similarity_info": "Comparison of image {idx} against the reference (image 1):",
        "similarity_ssim": "SSIM (structural similarity)",
        "similarity_psnr": "PSNR (peak signal-to-noise)",
        "similarity_diffpct": "Differing pixels",
        "similarity_identical": "Images are identical.",
        "similarity_need_two": "At least 2 images are required.",
        "settings_slider_live": "Move the slider live on mouse hover (no click)",
        "settings_loupe_zoom": "Magnifier zoom level:",
        "settings_pack_overlay": "Show pack name overlay in the image view",
        "export_done_status": "✔ Export saved: {path}",
        "export_rapide_status": "✔ Quick export saved: {path}",
        "comp_export_status": "✔ Compilation exported: {path}"
    },
    "fr": {
        "app_title": "Comparateur Pro (Ctrl+Molette pour Zoomer, Clic-droit pour déplacer)",
        "settings_title": "Paramètres Premium",
        "language": "Langue / Language :",
        "cursor_color": "Couleur du curseur :",
        "cursor_thickness": "Épaisseur curseur :",
        "label_size": "Taille texte labels :",
        "label_opacity": "Opacité fond labels :",
        "watermark_enable": "Activer le filigrane à l'export",
        "watermark_text": "Texte :",
        "close": "Fermer",
        "export_title": "Exportation",
        "export_labels": "Inclure les labels d'information",
        "export_zoom": "Exporter uniquement la zone zoomée actuelle",
        "format": "Format :",
        "export_btn": "Exporter...",
        "heatmap_title": "Analyse des Différences (Heatmap)",
        "heatmap_info": "🔥 Carte de chaleur : Les zones en ROUGE indiquent une forte différence.",
        "heatmap_global": "🔥 Carte de chaleur Globale ({count} images) : Différences cumulées.",
        "my_comparisons": "Mes Comparaisons",
        "new_pack": "+ Nouveau Pack",
        "del_pack": "Supprimer ce pack",
        "clear_list": "Vider la liste",
        "recent_btn": "🕘 Récents",
        "recent_title": "Comparaisons récentes",
        "recent_empty": "Aucune comparaison récente pour l'instant.",
        "recent_open": "Ouvrir",
        "recent_clear": "Vider l'historique",
        "recent_missing": "Certaines images de cette comparaison sont introuvables et ont été ignorées.",
        "recent_gone": "Aucune image de cette comparaison n'a pu être retrouvée.",
        "recent_not_enough": "Il ne reste pas assez d'images valides pour ouvrir cette comparaison.",
        "vertical": "⬍ Vertical",
        "horizontal": "⬌ Horizontal",
        "center": "Centrer",
        "originals": "↺ Originaux",
        "auto_align": "🪄 Auto-Alignement",
        "heatmap_btn": "🔥 Différence (Heatmap)",
        "copy": "Copier (Ctrl+C)",
        "settings": "⚙ Paramètres",
        "export": "Exporter",
        "drop_text": "Glissez & Déposez vos images ici\npour créer un nouveau pack",
        "add_img": "+ Ajouter image",
        "remove_img": "- Enlever image",
        "warn_min_images": "Veuillez déposer au moins 2 images pour créer un nouveau pack.",
        "warn_pack_min": "Un pack doit contenir au moins 2 images pour être comparé.",
        "info_sel_img": "Sélectionnez une image dans la barre du bas pour la retirer.",
        "clear_confirm": "Voulez-vous vraiment supprimer tout l'historique des packs ?",
        "align_start": "L'alignement va commencer. Cliquez sur OK pour lancer le calcul.",
        "align_success": "Toutes les images ont été alignées et recadrées sur la première !",
        "err_sim": "Pas assez de similitudes avec l'image {idx}.",
        "err_trans": "Impossible de calculer une transformation fiable pour l'image {idx}.",
        "err_align": "L'alignement a échoué :\n{err}",
        "copied": "La comparaison a été copiée dans le presse-papier !",
        "exp_success": "Export rapide terminé !\n\nSauvegardé dans :\n{path}",
        "gif_success": "GIF Animé généré avec succès !",
        "err_gif": "Erreur GIF : {err}",
        "err_gen": "Erreur de génération :\n{err}",
        "missing_dep": "Nécessite OpenCV. Ouvrez CMD et tapez :\npip install opencv-python numpy",
        "invalid_image_skip": "Image illisible ignoree : {path}",
        "diff_failed_status": "Difference de pixels impossible ; retour au mode curseur.",
        "close_compilation_packs": "Des packs de compilation sont encore ouverts. Fermer quand meme ?",
        "restart_lang": "Veuillez redémarrer l'application pour appliquer le changement de langue.",
        "img_word": "img",
        "warning": "Attention",
        "info": "Info",
        "success": "Succès",
        "error": "Erreur",
        "tab_comparateur": "Comparateur",
        "tab_compilation": "Compilation",
        "shortcuts_title": "Raccourcis clavier",
        "shortcuts_section_general": "General",
        "shortcuts_section_compare": "Vue Comparateur",
        "shortcuts_section_compil": "Vue Compilation",
        "sc_fullscreen": "Basculer en plein ecran",
        "sc_copy": "Copier dans le presse-papier",
        "sc_export": "Ouvrir la fenetre d'export",
        "sc_quick_export": "Export JPEG 1:1 rapide",
        "sc_delete_pack": "Supprimer le pack / l'image selectionne",
        "sc_next_pack": "Pack suivant / precedent",
        "sc_switch_tabs": "Basculer Comparateur / Compilation",
        "sc_zoom": "Zoomer / dezoomer",
        "sc_pan": "Deplacer la vue",
        "sc_blink": "Mode Blink (reference vs vue actuelle)",
        "sc_undo": "Annuler le deplacement de curseur",
        "sc_move_cursor": "Deplacer finement le premier curseur",
        "sc_comp_select": "Selectionner une case (clic simple)",
        "sc_comp_delete": "Vider la case selectionnee",
        "sc_comp_swap": "Intervertir deux cases (Ctrl + glisser-deposer)",
        "sc_comp_adjust": "Repositionner l'image dans une case (glisser)",
        "sc_comp_zoom_cell": "Zoomer l'image dans une case (molette)",
        "sc_comp_undo": "Annuler la derniere action",
        "sc_comp_redo": "Retablir la derniere action",
        "sc_comp_export": "Export rapide de la compilation",
        "sc_comp_next_cell": "Selectionner la case suivante / precedente",
        "settings_language_section": "Langue",
        "settings_export_lang": "Exporter un fichier de langue...",
        "settings_import_lang": "Importer un fichier de langue...",
        "settings_lang_exported": "Modele de langue exporte :\n{path}",
        "settings_lang_imported": "Langue importee : {name}\nRedemarrez pour appliquer si besoin.",
        "settings_lang_err": "Impossible de lire ce fichier de langue.",
        "settings_shortcuts_btn": "Voir les raccourcis clavier",
        "settings_translate_help": "Pour traduire le logiciel : exportez un fichier de langue, modifiez les textes, puis reimportez-le.",
        "view_mode": "Mode d'affichage :",
        "view_mode_slider": "Comparaison a curseur",
        "view_mode_side": "Cote a cote",
        "view_mode_diff": "Difference de pixels",
        "side_gap": "Espace entre les images :",
        "loupe_enable": "🔎 Loupe",
        "loupe_zoom": "Zoom de la loupe :",
        "diff_btn": "🔬 Difference de pixels",
        "diff_title": "Difference de pixels (soustraction)",
        "diff_info": "🔬 Difference de pixels : les zones claires ont le plus change.",
        "similarity_btn": "📊 Score de similarite",
        "similarity_title": "Mesure de similarite",
        "similarity_info": "Comparaison de l'image {idx} avec la reference (image 1) :",
        "similarity_ssim": "SSIM (similarite structurelle)",
        "similarity_psnr": "PSNR (rapport signal/bruit)",
        "similarity_diffpct": "Pixels differents",
        "similarity_identical": "Les images sont identiques.",
        "similarity_need_two": "Au moins 2 images sont necessaires.",
        "settings_slider_live": "Deplacer le curseur en direct au survol (sans clic)",
        "settings_loupe_zoom": "Niveau de zoom de la loupe :",
        "settings_pack_overlay": "Afficher le nom du pack dans la vue image",
        "export_done_status": "✔ Export enregistre : {path}",
        "export_rapide_status": "✔ Export rapide enregistre : {path}",
        "comp_export_status": "✔ Compilation exportee : {path}"
    }
}

# ==========================================
# SYSTEME DE LANGUES IMPORTABLES
# ==========================================
# Les langues integrees (fr/en) sont completees par les fichiers .json
# presents dans le dossier "langues" a cote du script. Cela permet aux
# utilisateurs de traduire le logiciel et de partager leurs traductions.
DOSSIER_LANGUES = os.path.join(DOSSIER_SCRIPT, "langues")

# Noms d'affichage des langues integrees.
NOMS_LANGUES = {"fr": "Francais", "en": "English"}


def charger_langues_externes():
    """Scanne le dossier 'langues' et fusionne chaque fichier .json trouve
    dans le dictionnaire LANGUAGES. Format attendu d'un fichier :
        { "_meta": {"code": "de", "name": "Deutsch"}, "app_title": "...", ... }
    Le code de langue sert de cle ; le name est affiche dans les reglages."""
    if not os.path.isdir(DOSSIER_LANGUES):
        return
    for nom_fichier in os.listdir(DOSSIER_LANGUES):
        if not nom_fichier.lower().endswith(".json"):
            continue
        chemin = os.path.join(DOSSIER_LANGUES, nom_fichier)
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta = data.get("_meta", {})
            code = meta.get("code") or os.path.splitext(nom_fichier)[0]
            nom_affiche = meta.get("name", code)
            # On retire la cle technique _meta avant fusion.
            traductions = {k: v for k, v in data.items() if k != "_meta"}
            if code in LANGUAGES:
                # Langue existante : on complete/ecrase les cles fournies.
                LANGUAGES[code].update(traductions)
            else:
                LANGUAGES[code] = traductions
            NOMS_LANGUES[code] = nom_affiche
        except Exception as e:
            # Un fichier de langue corrompu ne doit pas bloquer le logiciel.
            ecrire_log_erreur("Chargement langue externe: %s" % chemin, e)


charger_langues_externes()

class ConfigManager:
    def __init__(self):
        try:
            sys_lang = locale.getdefaultlocale()[0]
            default_lang = "fr" if sys_lang and sys_lang.startswith("fr") else "en"
        except Exception:
            default_lang = "en"
        
        self.config = {
            "language": default_lang,
            "cursor_color": "#00a8ff",
            "cursor_thickness": 2,
            "label_size": 14,
            "label_bg_opacity": 150,
            "orientation": "Vertical",
            "watermark_enabled": False,
            "watermark_text": "Comparateur Pro",
            "slider_live": False,
            "loupe_zoom": 2.5,
            "show_pack_name_overlay": True,
            "last_packs": [],
            "last_pack_index": 0,
            "recent_packs": []
        }
        self.charger()

    def charger(self):
        if os.path.exists(FICHIER_CONFIG):
            try:
                with open(FICHIER_CONFIG, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
            except: pass

    def sauver(self):
        try:
            with open(FICHIER_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except: pass

    def get(self, key): return self.config.get(key)
    def set(self, key, value): 
        self.config[key] = value
        self.sauver()

config = ConfigManager()

def tr(key, **kwargs):
    """Traduit une cle. Repli en cascade : langue choisie -> anglais ->
    francais -> cle brute. Cela protege des traductions utilisateur
    incompletes (une cle manquante n'affiche jamais de vide)."""
    lang = config.get("language")
    text = None
    if lang in LANGUAGES and key in LANGUAGES[lang]:
        text = LANGUAGES[lang][key]
    elif "en" in LANGUAGES and key in LANGUAGES["en"]:
        text = LANGUAGES["en"][key]
    elif "fr" in LANGUAGES and key in LANGUAGES["fr"]:
        text = LANGUAGES["fr"][key]
    else:
        text = key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

# ==========================================
# MODULE ADDITIONNEL : COMPILATION D'IMAGES
# ==========================================
# Import optionnel : si le fichier est absent, le logiciel fonctionne
# normalement sans le bouton de compilation (fail-safe).
try:
    import compilation_module
    compilation_module.init_compilation(config, tr, LANGUAGES)
    HAS_COMPILATION = True
except Exception:
    HAS_COMPILATION = False

STYLE_SHEET = """
/* ============================================================
   THEME "MIDNIGHT BLUE" - sombre bleute moderne, accents orange
   ============================================================ */
QMainWindow, QDialog { background-color: #0f1623; color: #e8edf4; }
QWidget { color: #e8edf4; font-size: 13px; }
QLabel { color: #e8edf4; }
QLabel#Titre { font-size: 24px; font-weight: bold; color: #ffffff; }
QLabel#SousTitre { color: #8b97a8; font-size: 14px; }

/* Zone de depot */
QFrame#DropFrame { border: 2px dashed #34425a; border-radius: 14px; background-color: #161f2e; }
QFrame#DropFrame[hover="true"] { border: 2px dashed #ff8c42; background-color: #1d2839; }

/* Boutons : standard sombre bleute */
QPushButton {
    background-color: #1d2839; color: #e8edf4;
    border: 1px solid #34425a; border-radius: 7px;
    padding: 7px 14px; font-weight: 600;
}
QPushButton:hover { background-color: #283750; border: 1px solid #4a9eff; }
QPushButton:pressed { background-color: #161f2e; }
QPushButton:disabled { background-color: #161f2e; color: #5a6578; border: 1px solid #232f44; }

/* Bouton primaire : orange premium */
QPushButton#PrimaryButton {
    background-color: #ff8c42; color: #1a1205;
    border: none; font-weight: 700;
}
QPushButton#PrimaryButton:hover { background-color: #ffa05f; }
QPushButton#PrimaryButton:pressed { background-color: #ff7a1a; }

/* Bouton danger : rouge desature */
QPushButton#DangerButton { background-color: #c0392b; color: #ffffff; border: none; }
QPushButton#DangerButton:hover { background-color: #e0483a; }

/* Barres et panneaux */
QFrame#Toolbar, QFrame#Sidebar { background-color: #161f2e; }
QFrame#Toolbar { border-bottom: 1px solid #283750; }
QFrame#Sidebar { border-right: 1px solid #283750; }

/* Listes */
QListWidget { background-color: #161f2e; border: 1px solid #283750; border-radius: 7px; outline: 0; }
QListWidget::item { border: 2px solid transparent; border-radius: 6px; padding: 5px; }
QListWidget::item:selected { border: 2px solid #ff8c42; background-color: #1d2839; }
QListWidget::item:hover { background-color: #1d2839; }

/* Champs de saisie */
QSpinBox, QSlider, QComboBox, QLineEdit {
    background-color: #1d2839; color: #e8edf4;
    border: 1px solid #34425a; border-radius: 6px; padding: 5px;
}
QSpinBox:focus, QComboBox:focus, QLineEdit:focus { border: 1px solid #4a9eff; }
QComboBox QAbstractItemView {
    background-color: #1d2839; color: #e8edf4;
    border: 1px solid #34425a; selection-background-color: #ff8c42;
    selection-color: #1a1205;
}
QSpinBox::up-button, QSpinBox::down-button { background-color: #283750; border: none; width: 16px; }
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #ff8c42; }

/* Curseur (slider) */
QSlider::groove:horizontal { height: 5px; background: #283750; border-radius: 2px; }
QSlider::handle:horizontal {
    background: #ff8c42; width: 15px; margin: -6px 0; border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: #ffa05f; }
QSlider::sub-page:horizontal { background: #ff8c42; border-radius: 2px; }

/* Cases a cocher / radios */
QCheckBox, QRadioButton { color: #e8edf4; spacing: 6px; }
QCheckBox::indicator, QRadioButton::indicator { width: 16px; height: 16px; }
QCheckBox::indicator { border: 1px solid #34425a; border-radius: 4px; background: #1d2839; }
QCheckBox::indicator:checked { background: #ff8c42; border: 1px solid #ff8c42; }
QRadioButton::indicator { border: 1px solid #34425a; border-radius: 8px; background: #1d2839; }
QRadioButton::indicator:checked { background: #ff8c42; border: 3px solid #1d2839; }

/* Barres de defilement */
QScrollBar:vertical { background: #161f2e; width: 11px; margin: 0; }
QScrollBar::handle:vertical { background: #34425a; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #4a9eff; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #161f2e; height: 11px; margin: 0; }
QScrollBar::handle:horizontal { background: #34425a; border-radius: 5px; min-width: 24px; }
QScrollBar::handle:horizontal:hover { background: #4a9eff; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* Menus */
QMenu { background-color: #1d2839; color: #e8edf4; border: 1px solid #34425a; }
QMenu::item:selected { background-color: #ff8c42; color: #1a1205; }

/* Onglets principaux */
QTabWidget#OngletsPrincipaux::pane { border: none; background-color: #0f1623; }
QTabWidget#OngletsPrincipaux QTabBar::tab {
    background-color: #161f2e; color: #8b97a8;
    border: 1px solid #283750; border-bottom: none;
    border-top-left-radius: 8px; border-top-right-radius: 8px;
    padding: 9px 24px; margin-right: 3px; font-weight: 700; font-size: 13px;
}
QTabWidget#OngletsPrincipaux QTabBar::tab:selected {
    background-color: #0f1623; color: #ff8c42;
    border-bottom: 2px solid #ff8c42;
}
QTabWidget#OngletsPrincipaux QTabBar::tab:hover:!selected {
    background-color: #1d2839; color: #e8edf4;
}

/* Bouton parametres dans le coin des onglets */
QPushButton#SettingsCorner {
    background-color: transparent; color: #8b97a8;
    border: none; padding: 7px 16px; font-weight: 700; font-size: 13px;
}
QPushButton#SettingsCorner:hover {
    background-color: #1d2839; color: #ff8c42; border-radius: 7px;
}

/* Tooltips */
QToolTip {
    background-color: #1d2839; color: #e8edf4;
    border: 1px solid #ff8c42; padding: 4px;
}
"""

class ComparateurWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.images_originales = []
        self.infos_images = []
        self.ratios = []
        self.afficher_labels = True
        self.blink_mode = False
        self.curseur_actif = None
        self.historique_ratios = []
        self.total_zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.panning = False
        self.last_mouse_pos = None
        # Mode d'affichage : "slider" (curseur), "side" (cote a cote),
        # "diff" (difference de pixels). Le mode slider est le mode d'origine.
        self.mode_affichage = "slider"
        self.espace_side = 12          # espace entre images en mode cote a cote
        self.pixmap_diff = None        # QPixmap de difference (mode diff)
        # Loupe : fenetre grossissante qui suit le curseur.
        self.loupe_active = False
        self.loupe_zoom = float(config.get("loupe_zoom") or 2.5)
        self.loupe_taille = 200        # diametre de la loupe en pixels
        self.souris_pos = None         # derniere position connue de la souris
        self.nom_pack = ""
        # Mode "slider en direct" : si actif, le curseur suit la souris au
        # survol (sans clic). Sinon, comportement clic-maintenu classique.
        self.slider_live = bool(config.get("slider_live"))
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def charger_images(self, chemins):
        self.images_originales = []
        self.infos_images = []
        for c in chemins:
            pixmap = QPixmap(c)
            if pixmap.isNull():
                ecrire_log_erreur(tr("invalid_image_skip", path=c),
                                  RuntimeError("QPixmap null"))
                continue
            self.images_originales.append(pixmap)
            taille_mo = os.path.getsize(c) / (1024 * 1024)
            nom = os.path.basename(c)
            info = f"{nom}\n{pixmap.width()} x {pixmap.height()} px\n{taille_mo:.1f} Mo"
            self.infos_images.append(info)
        if not self.images_originales:
            self.pixmap_diff = None
            self.update()
            return
        # Le pack a change : la difference pre-calculee n'est plus valable.
        self.pixmap_diff = None
        self.reset_ratios()
        # Recentrage selon le mode courant ; recalcul de la difference si besoin.
        if self.mode_affichage == "diff":
            self.calculer_difference()
            self.centrer_vue_mode()
        elif self.mode_affichage == "side":
            self.centrer_vue_mode()
        else:
            self.centrer_vue()

    def reset_ratios(self):
        nb_curseurs = len(self.images_originales) - 1
        if nb_curseurs > 0:
            self.ratios = [(i + 1) / (nb_curseurs + 1) for i in range(nb_curseurs)]
            self.historique_ratios = [list(self.ratios)]
        self.update()

    def centrer_vue(self):
        if not self.images_originales: return
        img_w, img_h = self.images_originales[0].width(), self.images_originales[0].height()
        vue_w, vue_h = self.width(), self.height()
        zoom_w = vue_w / img_w if img_w > 0 else 1
        zoom_h = vue_h / img_h if img_h > 0 else 1
        self.total_zoom = min(zoom_w, zoom_h, 1.0)
        self.pan_x = (vue_w - (img_w * self.total_zoom)) / 2
        self.pan_y = (vue_h - (img_h * self.total_zoom)) / 2
        self.update()

    def resizeEvent(self, event):
        if not self.images_originales: return
        if self.mode_affichage == "slider":
            self.centrer_vue()
        else:
            self.centrer_vue_mode()
            self.update()
        super().resizeEvent(event)

    def paintEvent(self, event):
        if not self.images_originales: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        img_base = self.images_originales[0]
        w_orig, h_orig = img_base.width(), img_base.height()
        w_aff = w_orig * self.total_zoom
        h_aff = h_orig * self.total_zoom

        # --- Modes d'affichage alternatifs (cote a cote / difference) ---
        # Le mode "slider" (curseur) reste le comportement d'origine ci-dessous.
        if self.mode_affichage == "side":
            self._peindre_cote_a_cote(painter)
            self._peindre_loupe(painter)
            self._peindre_nom_pack(painter)
            return
        if self.mode_affichage == "diff":
            self._peindre_difference(painter)
            self._peindre_loupe(painter)
            self._peindre_nom_pack(painter)
            return

        if getattr(self, 'blink_mode', False):
            rect_dest = QRect(int(self.pan_x), int(self.pan_y), int(w_aff), int(h_aff))
            rect_source = QRect(0, 0, w_orig, h_orig)
            painter.drawPixmap(rect_dest, img_base, rect_source)
            self._peindre_loupe(painter)
            self._peindre_nom_pack(painter)
            return

        orientation = config.get("orientation")
        is_vert = orientation == "Vertical"
        dim_max = w_aff if is_vert else h_aff
        curseurs_px = [int(dim_max * r) for r in self.ratios]

        for i in range(len(self.images_originales)):
            c_gauche = 0 if i == 0 else curseurs_px[i-1]
            c_droite = dim_max if i == len(self.images_originales)-1 else curseurs_px[i]
            if is_vert:
                rect_dest = QRect(int(self.pan_x + c_gauche), int(self.pan_y), int(c_droite - c_gauche), int(h_aff))
                rect_source = QRect(int(c_gauche / self.total_zoom), 0, int((c_droite - c_gauche) / self.total_zoom), h_orig)
            else:
                rect_dest = QRect(int(self.pan_x), int(self.pan_y + c_gauche), int(w_aff), int(c_droite - c_gauche))
                rect_source = QRect(0, int(c_gauche / self.total_zoom), w_orig, int((c_droite - c_gauche) / self.total_zoom))
            painter.drawPixmap(rect_dest, self.images_originales[i], rect_source)

        couleur = QColor(config.get("cursor_color"))
        epaisseur = config.get("cursor_thickness")
        stylo = QPen(couleur, epaisseur)
        painter.setPen(stylo)
        painter.setBrush(couleur)

        for c in curseurs_px:
            if is_vert:
                x_ligne = int(self.pan_x + c)
                painter.drawLine(x_ligne, int(self.pan_y), x_ligne, int(self.pan_y + h_aff))
                painter.drawEllipse(x_ligne - 5, int(self.pan_y + h_aff//2 - 15), 10, 30)
            else:
                y_ligne = int(self.pan_y + c)
                painter.drawLine(int(self.pan_x), y_ligne, int(self.pan_x + w_aff), y_ligne)
                painter.drawEllipse(int(self.pan_x + w_aff//2 - 15), y_ligne - 5, 30, 10)

        taille_label_base = config.get("label_size")
        opacite = config.get("label_bg_opacity")
        if self.afficher_labels:
            for i in range(len(self.infos_images)):
                c_gauche = 0 if i == 0 else curseurs_px[i-1]
                c_droite = dim_max if i == len(self.images_originales)-1 else curseurs_px[i]
                if is_vert:
                    slice_left = int(self.pan_x + c_gauche)
                    slice_right = int(self.pan_x + c_droite)
                    visible_left = max(0, slice_left)
                    visible_right = min(self.width(), slice_right)
                    visible_width = visible_right - visible_left
                    if visible_width > 40:
                        texte = self.infos_images[i]
                        taille_actuelle = taille_label_base
                        font = QFont("Segoe UI", taille_actuelle, QFont.Bold)
                        painter.setFont(font)
                        rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte)
                        largeur_tranche = slice_right - slice_left
                        while rect_text.width() + 20 > largeur_tranche and taille_actuelle > 6:
                            taille_actuelle -= 1
                            font.setPointSize(taille_actuelle)
                            painter.setFont(font)
                            rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte)
                        tx = max(10, slice_left + 10)
                        tx = min(tx, slice_right - rect_text.width() - 10)
                        ty = max(10, int(self.pan_y) + 10)
                        ty = min(ty, self.height() - rect_text.height() - 10)
                        painter.save()
                        clip_rect = QRect(slice_left, 0, largeur_tranche, self.height())
                        painter.setClipRect(clip_rect)
                        bg_rect = QRect(int(tx - 5), int(ty - 5), rect_text.width() + 10, rect_text.height() + 10)
                        painter.setPen(Qt.NoPen)
                        painter.setBrush(QColor(0, 0, 0, opacite))
                        painter.drawRoundedRect(bg_rect, 5, 5)
                        painter.setPen(Qt.white)
                        painter.drawText(int(tx), int(ty), rect_text.width(), rect_text.height(), Qt.AlignLeft, texte)
                        painter.restore()
                else:
                    slice_top = int(self.pan_y + c_gauche)
                    slice_bottom = int(self.pan_y + c_droite)
                    visible_top = max(0, slice_top)
                    visible_bottom = min(self.height(), slice_bottom)
                    visible_height = visible_bottom - visible_top
                    if visible_height > 40:
                        texte = self.infos_images[i]
                        taille_actuelle = taille_label_base
                        font = QFont("Segoe UI", taille_actuelle, QFont.Bold)
                        painter.setFont(font)
                        rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte)
                        hauteur_tranche = slice_bottom - slice_top
                        while rect_text.height() + 20 > hauteur_tranche and taille_actuelle > 6:
                            taille_actuelle -= 1
                            font.setPointSize(taille_actuelle)
                            painter.setFont(font)
                            rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte)
                        tx = max(10, int(self.pan_x) + 10)
                        tx = min(tx, self.width() - rect_text.width() - 10)
                        ty = max(10, slice_top + 10)
                        ty = min(ty, slice_bottom - rect_text.height() - 10)
                        painter.save()
                        clip_rect = QRect(0, slice_top, self.width(), hauteur_tranche)
                        painter.setClipRect(clip_rect)
                        bg_rect = QRect(int(tx - 5), int(ty - 5), rect_text.width() + 10, rect_text.height() + 10)
                        painter.setPen(Qt.NoPen)
                        painter.setBrush(QColor(0, 0, 0, opacite))
                        painter.drawRoundedRect(bg_rect, 5, 5)
                        painter.setPen(Qt.white)
                        painter.drawText(int(tx), int(ty), rect_text.width(), rect_text.height(), Qt.AlignLeft, texte)
                        painter.restore()

        # Loupe par-dessus le rendu (mode curseur).
        self._peindre_loupe(painter)
        self._peindre_nom_pack(painter)

    def _peindre_nom_pack(self, painter):
        if not config.get("show_pack_name_overlay"):
            return
        nom = getattr(self, "nom_pack", "")
        if not nom:
            return
        painter.save()
        font = QFont("Segoe UI", 11)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 128))
        rect = QRect(10, 8, self.width() - 20, 24)
        painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, nom)
        painter.restore()

    # ------------------------------------------------------------------
    #  MODE COTE A COTE  (toutes les images alignees, sans curseur)
    # ------------------------------------------------------------------
    def _disposition_side(self):
        """Calcule la disposition cote a cote : retourne (liste de QRect
        destination a l'echelle, largeur virtuelle, hauteur virtuelle).
        On respecte la hauteur de l'image de reference ; chaque image garde
        son ratio. zoom et pan s'appliquent comme en mode curseur."""
        is_vert = config.get("orientation") == "Vertical"
        ref = self.images_originales[0]
        rects = []
        if is_vert:
            # Images alignees horizontalement, hauteur commune = ref.height().
            h_ref = ref.height()
            x = 0
            for img in self.images_originales:
                if img.height() > 0:
                    w_img = img.width() * (h_ref / img.height())
                else:
                    w_img = img.width()
                rects.append((x, 0, w_img, h_ref))
                x += w_img + self.espace_side
            virt_w = x - self.espace_side if rects else 0
            virt_h = h_ref
        else:
            # Images empilees verticalement, largeur commune = ref.width().
            w_ref = ref.width()
            y = 0
            for img in self.images_originales:
                if img.width() > 0:
                    h_img = img.height() * (w_ref / img.width())
                else:
                    h_img = img.height()
                rects.append((0, y, w_ref, h_img))
                y += h_img + self.espace_side
            virt_w = w_ref
            virt_h = y - self.espace_side if rects else 0
        return rects, virt_w, virt_h

    def _peindre_cote_a_cote(self, painter):
        rects, virt_w, virt_h = self._disposition_side()
        for i, img in enumerate(self.images_originales):
            x, y, w, h = rects[i]
            rect_dest = QRect(int(self.pan_x + x * self.total_zoom),
                              int(self.pan_y + y * self.total_zoom),
                              int(w * self.total_zoom),
                              int(h * self.total_zoom))
            painter.drawPixmap(rect_dest, img, QRect(0, 0, img.width(), img.height()))
        # Etiquettes (une par image).
        if self.afficher_labels:
            taille = config.get("label_size")
            opacite = config.get("label_bg_opacity")
            for i, info in enumerate(self.infos_images):
                x, y, w, h = rects[i]
                px = int(self.pan_x + x * self.total_zoom) + 10
                py = int(self.pan_y + y * self.total_zoom) + 10
                font = QFont("Segoe UI", taille, QFont.Bold)
                painter.setFont(font)
                rt = painter.fontMetrics().boundingRect(QRect(0, 0, 0, 0),
                                                        Qt.AlignLeft, info)
                bg = QRect(px - 5, py - 5, rt.width() + 10, rt.height() + 10)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(0, 0, 0, opacite))
                painter.drawRoundedRect(bg, 5, 5)
                painter.setPen(Qt.white)
                painter.drawText(px, py, rt.width(), rt.height(),
                                 Qt.AlignLeft, info)

    # ------------------------------------------------------------------
    #  MODE DIFFERENCE DE PIXELS
    # ------------------------------------------------------------------
    def _peindre_difference(self, painter):
        """Affiche l'image de difference pre-calculee (self.pixmap_diff).
        Si elle n'existe pas encore, affiche simplement l'image de base."""
        pix = self.pixmap_diff if self.pixmap_diff is not None else \
            self.images_originales[0]
        w_aff = pix.width() * self.total_zoom
        h_aff = pix.height() * self.total_zoom
        rect_dest = QRect(int(self.pan_x), int(self.pan_y),
                          int(w_aff), int(h_aff))
        painter.drawPixmap(rect_dest, pix, QRect(0, 0, pix.width(), pix.height()))

    # ------------------------------------------------------------------
    #  LOUPE  (fenetre grossissante qui suit le curseur)
    # ------------------------------------------------------------------
    def _peindre_loupe(self, painter):
        """Dessine une loupe circulaire centree sur la souris.

        La loupe ne capture PAS le widget (grab() pendant un paintEvent
        actif est instable et peut faire planter PyQt5). A la place, elle
        redessine directement la portion concernee a partir des pixmaps
        sources, avec un facteur de grossissement superieur."""
        if not self.loupe_active or self.souris_pos is None:
            return
        if not self.images_originales:
            return
        sx, sy = self.souris_pos.x(), self.souris_pos.y()
        if sx < 0 or sy < 0 or sx > self.width() or sy > self.height():
            return
        d = self.loupe_taille
        z = max(1.1, self.loupe_zoom)

        # Position de la loupe : decalee pour ne pas masquer le curseur,
        # ramenee dans la fenetre si elle deborde.
        lx = sx + 24
        ly = sy + 24
        if lx + d > self.width():
            lx = sx - d - 24
        if ly + d > self.height():
            ly = sy - d - 24
        lx = max(0, min(lx, self.width() - d))
        ly = max(0, min(ly, self.height() - d))
        zone = QRect(int(lx), int(ly), d, d)

        # Conversion : point souris -> coordonnees dans l'image de reference.
        # On reutilise la meme transformation que le rendu courant : un point
        # ecran (px) correspond a (px - pan) / total_zoom dans la toile.
        img_ref = self.images_originales[0]
        # Echelle effective de la loupe : grossissement applique par-dessus
        # le zoom courant de la vue.
        echelle_loupe = self.total_zoom * z

        painter.save()
        # Decoupe circulaire de la zone de la loupe.
        from PyQt5.QtGui import QPainterPath
        chemin = QPainterPath()
        chemin.addEllipse(QRectF(zone))
        painter.setClipPath(chemin)
        # Fond neutre sous la loupe.
        painter.fillRect(zone, QColor("#0f1623"))

        # Position, dans la toile virtuelle, du point sous le curseur.
        toile_x = (sx - self.pan_x) / self.total_zoom if self.total_zoom else 0
        toile_y = (sy - self.pan_y) / self.total_zoom if self.total_zoom else 0

        if self.mode_affichage == "diff" and self.pixmap_diff is not None:
            # Mode difference : on grossit l'image de difference.
            self._loupe_dessiner_pixmap(painter, self.pixmap_diff, zone,
                                        toile_x, toile_y, echelle_loupe)
        elif self.mode_affichage == "side":
            # Mode cote a cote : on retrouve l'image survolee.
            rects, _, _ = self._disposition_side()
            image_proche = None
            distance_proche = None
            for i, img in enumerate(self.images_originales):
                rx, ry, rw, rh = rects[i]
                if rx <= toile_x < rx + rw and ry <= toile_y < ry + rh:
                    self._loupe_dessiner_pixmap(
                        painter, img, zone,
                        toile_x - rx, toile_y - ry, echelle_loupe)
                    break
                dx = max(rx - toile_x, 0, toile_x - (rx + rw))
                dy = max(ry - toile_y, 0, toile_y - (ry + rh))
                distance = dx * dx + dy * dy
                if distance_proche is None or distance < distance_proche:
                    distance_proche = distance
                    image_proche = (img, rx, ry)
            else:
                if image_proche is not None:
                    img, rx, ry = image_proche
                    self._loupe_dessiner_pixmap(
                        painter, img, zone,
                        toile_x - rx, toile_y - ry, echelle_loupe)
        else:
            # Mode curseur : on dessine, dans la loupe, la tranche d'image
            # correspondant a la position (comme le rendu principal).
            is_vert = config.get("orientation") == "Vertical"
            dim_max = (img_ref.width() if is_vert else img_ref.height())
            curseurs = [dim_max * r for r in self.ratios]
            for i, img in enumerate(self.images_originales):
                c_g = 0 if i == 0 else curseurs[i - 1]
                c_d = dim_max if i == len(self.images_originales) - 1 else curseurs[i]
                pos = toile_x if is_vert else toile_y
                if c_g <= pos < c_d or i == len(self.images_originales) - 1:
                    if c_g <= pos < c_d:
                        self._loupe_dessiner_pixmap(painter, img, zone,
                                                    toile_x, toile_y,
                                                    echelle_loupe)
                        break

        painter.setClipping(False)
        # Anneau de la loupe.
        painter.setPen(QPen(QColor(config.get("cursor_color")), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(zone)
        # Petite croix au centre.
        cx, cy = zone.center().x(), zone.center().y()
        painter.setPen(QPen(QColor(config.get("cursor_color")), 1))
        painter.drawLine(cx - 6, cy, cx + 6, cy)
        painter.drawLine(cx, cy - 6, cx, cy + 6)
        painter.restore()

    def _loupe_dessiner_pixmap(self, painter, pixmap, zone, src_x, src_y,
                               echelle):
        """Dessine, dans `zone` (carre de la loupe), la portion de `pixmap`
        centree sur (src_x, src_y) image, agrandie au facteur `echelle`."""
        if pixmap is None or pixmap.isNull():
            return
        # Demi-cote de la portion source a echantillonner.
        demi_src = (zone.width() / echelle) / 2.0
        sx0 = src_x - demi_src
        sy0 = src_y - demi_src
        rect_source = QRectF(sx0, sy0, demi_src * 2, demi_src * 2)
        painter.drawPixmap(QRectF(zone), pixmap, rect_source)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return
        if event.button() == Qt.LeftButton and self.mode_affichage == "slider" and self.ratios:
            self.historique_ratios.append(list(self.ratios))
            if len(self.historique_ratios) > 20: self.historique_ratios.pop(0)
            is_vert = config.get("orientation") == "Vertical"
            pos_relative = (event.x() - self.pan_x) if is_vert else (event.y() - self.pan_y)
            dim_max = (self.images_originales[0].width() * self.total_zoom) if is_vert else (self.images_originales[0].height() * self.total_zoom)
            curseurs_px = [dim_max * r for r in self.ratios]
            distances = [abs(c - pos_relative) for c in curseurs_px]
            if distances:
                min_dist = min(distances)
                # Tolerance de saisie elargie (40 px) pour attraper le curseur
                # plus facilement, surtout sur ecran haute densite.
                if min_dist < 40:
                    self.curseur_actif = distances.index(min_dist)
                    self.update_curseur(pos_relative, dim_max)

    def mouseMoveEvent(self, event):
        is_vert = config.get("orientation") == "Vertical"
        # Suivi de la souris pour la loupe (tous modes).
        self.souris_pos = event.pos()
        if self.loupe_active:
            self.update()
        if self.panning and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()
            return
        # En mode cote a cote / difference, seul le pan et la loupe sont actifs.
        if self.mode_affichage != "slider":
            return
        if self.curseur_actif is not None:
            pos_relative = (event.x() - self.pan_x) if is_vert else (event.y() - self.pan_y)
            dim_max = (self.images_originales[0].width() * self.total_zoom) if is_vert else (self.images_originales[0].height() * self.total_zoom)
            self.update_curseur(pos_relative, dim_max)
        elif getattr(self, "slider_live", False) and self.ratios:
            # Mode "slider en direct" : le 1er curseur suit la souris sans
            # qu'il faille cliquer. Pratique pour balayer rapidement.
            pos_relative = (event.x() - self.pan_x) if is_vert else (event.y() - self.pan_y)
            dim_max = (self.images_originales[0].width() * self.total_zoom) if is_vert else (self.images_originales[0].height() * self.total_zoom)
            if dim_max > 0:
                ratio = max(0.0, min(1.0, pos_relative / dim_max))
                # On ne bouge que le 1er curseur, borne par le suivant.
                borne_max = 1.0 if len(self.ratios) == 1 else self.ratios[1] - 0.01
                self.ratios[0] = max(0.0, min(ratio, borne_max))
                self.update()
            if not self.panning:
                self.setCursor(Qt.SplitHCursor if is_vert else Qt.SplitVCursor)
        else:
            pos_relative = (event.x() - self.pan_x) if is_vert else (event.y() - self.pan_y)
            dim_max = (self.images_originales[0].width() * self.total_zoom) if is_vert else (self.images_originales[0].height() * self.total_zoom)
            curseurs_px = [dim_max * r for r in self.ratios]
            survol = any(abs(c - pos_relative) < 15 for c in curseurs_px)
            self.setCursor(Qt.SplitHCursor if is_vert and survol else (Qt.SplitVCursor if survol else Qt.ArrowCursor))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.panning = False
            self.setCursor(Qt.ArrowCursor)
        elif event.button() == Qt.LeftButton:
            self.curseur_actif = None

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            factor = 1.15 if zoom_in else (1 / 1.15)
            new_zoom = self.total_zoom * factor
            if new_zoom < 0.05 or new_zoom > 50.0: return
            mouse_x, mouse_y = event.x(), event.y()
            self.pan_x = mouse_x - (mouse_x - self.pan_x) * factor
            self.pan_y = mouse_y - (mouse_y - self.pan_y) * factor
            self.total_zoom = new_zoom
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.blink_mode = True
            self.update()
            return
        if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            if len(self.historique_ratios) > 1:
                self.historique_ratios.pop()
                self.ratios = list(self.historique_ratios[-1])
                self.update()
        pas = 0.002
        if event.key() in (Qt.Key_Left, Qt.Key_Up) and self.ratios:
            self.ratios[0] = max(0.0, self.ratios[0] - pas)
            self.update()
        elif event.key() in (Qt.Key_Right, Qt.Key_Down) and self.ratios:
            self.ratios[0] = min(1.0, self.ratios[0] + pas)
            self.update()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.blink_mode = False
            self.update()
            return
        super().keyReleaseEvent(event)

    def update_curseur(self, pos_relative, dim_max):
        min_r = 0.0 if self.curseur_actif == 0 else self.ratios[self.curseur_actif - 1] + 0.01
        max_r = 1.0 if self.curseur_actif == len(self.ratios) - 1 else self.ratios[self.curseur_actif + 1] - 0.01
        nouveau_ratio = pos_relative / dim_max
        for snap in [0.25, 0.50, 0.75]:
            if abs(nouveau_ratio - snap) < 0.02:
                nouveau_ratio = snap
                break
        self.ratios[self.curseur_actif] = max(min_r, min(nouveau_ratio, max_r))
        self.update()

    # ------------------------------------------------------------------
    #  GESTION DES MODES D'AFFICHAGE
    # ------------------------------------------------------------------
    def definir_mode(self, mode):
        """Change le mode d'affichage : 'slider', 'side' ou 'diff'.
        Recalcule la difference si necessaire puis recentre la vue."""
        if mode not in ("slider", "side", "diff"):
            mode = "slider"
        self.mode_affichage = mode
        if mode == "diff":
            self.calculer_difference()
        self.centrer_vue_mode()
        self.update()

    def centrer_vue_mode(self):
        """Centre la vue selon le mode courant (la 'toile' virtuelle change
        de taille selon le mode)."""
        if not self.images_originales:
            return
        if self.mode_affichage == "side":
            _, virt_w, virt_h = self._disposition_side()
        elif self.mode_affichage == "diff":
            if self.pixmap_diff is None or self.pixmap_diff.isNull():
                self.mode_affichage = "slider"
                self._message_statut(tr("diff_failed_status"))
                virt_w = self.images_originales[0].width()
                virt_h = self.images_originales[0].height()
            else:
                virt_w = self.pixmap_diff.width()
                virt_h = self.pixmap_diff.height()
        else:
            virt_w = self.images_originales[0].width()
            virt_h = self.images_originales[0].height()
        vue_w, vue_h = self.width(), self.height()
        zoom_w = vue_w / virt_w if virt_w > 0 else 1
        zoom_h = vue_h / virt_h if virt_h > 0 else 1
        self.total_zoom = min(zoom_w, zoom_h, 1.0)
        self.pan_x = (vue_w - virt_w * self.total_zoom) / 2
        self.pan_y = (vue_h - virt_h * self.total_zoom) / 2

    def _message_statut(self, message):
        """Affiche un message discret si la fenetre principale expose une barre."""
        try:
            fenetre = self.window()
            if hasattr(fenetre, "statusBar"):
                fenetre.statusBar().showMessage(message, 5000)
        except Exception:
            pass

    def calculer_difference(self):
        """Construit self.pixmap_diff : image de difference absolue entre
        la reference (image 1) et la 2e image. Utilise OpenCV si present,
        sinon un repli QImage pixel par pixel."""
        if len(self.images_originales) < 2:
            self.pixmap_diff = None
            return
        ref = self.images_originales[0]
        autre = self.images_originales[1]
        try:
            import cv2
            import numpy as np
            a = self._qpixmap_vers_array(ref)
            b = self._qpixmap_vers_array(autre)
            if a is None or b is None:
                raise RuntimeError("conversion impossible")
            if a.shape != b.shape:
                b = cv2.resize(b, (a.shape[1], a.shape[0]))
            diff = cv2.absdiff(a, b)
            # Accentuation legere pour rendre les ecarts plus lisibles.
            diff = cv2.convertScaleAbs(diff, alpha=2.0)
            self.pixmap_diff = self._array_vers_qpixmap(diff)
        except Exception:
            # Repli pur Qt : difference via QImage.
            self.pixmap_diff = self._difference_qimage(ref, autre)

    def _qpixmap_vers_array(self, pixmap):
        """Convertit un QPixmap en tableau numpy BGR (pour OpenCV)."""
        try:
            import numpy as np
            img = pixmap.toImage().convertToFormat(QImage.Format_RGB888)
            w, h = img.width(), img.height()
            ptr = img.constBits()
            ptr.setsize(h * img.bytesPerLine())
            arr = np.frombuffer(ptr, np.uint8).reshape(
                (h, img.bytesPerLine()))
            arr = arr[:, :w * 3].reshape((h, w, 3))
            # RGB -> BGR pour rester coherent avec OpenCV.
            return arr[:, :, ::-1].copy()
        except Exception:
            return None

    def _array_vers_qpixmap(self, arr):
        """Convertit un tableau numpy BGR en QPixmap."""
        h, w = arr.shape[:2]
        rgb = arr[:, :, ::-1].copy()
        img = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        return QPixmap.fromImage(img.copy())

    def _difference_qimage(self, ref, autre):
        """Repli sans OpenCV : difference absolue vectorisee via Pillow."""
        if HAS_PIL:
            try:
                from PIL import ImageChops, ImageEnhance
                a = ref.toImage().convertToFormat(QImage.Format_RGBA8888)
                b = autre.toImage().convertToFormat(QImage.Format_RGBA8888)
                if a.size() != b.size():
                    b = b.scaled(a.width(), a.height())
                ptr_a = a.constBits()
                ptr_a.setsize(a.height() * a.bytesPerLine())
                ptr_b = b.constBits()
                ptr_b.setsize(b.height() * b.bytesPerLine())
                img_a = Image.frombytes("RGBA", (a.width(), a.height()), bytes(ptr_a))
                img_b = Image.frombytes("RGBA", (b.width(), b.height()), bytes(ptr_b))
                diff = ImageChops.difference(img_a, img_b).convert("RGB")
                diff = ImageEnhance.Brightness(diff).enhance(2.0)
                data = diff.tobytes("raw", "RGB")
                qimg = QImage(data, diff.width, diff.height,
                              diff.width * 3, QImage.Format_RGB888)
                return QPixmap.fromImage(qimg.copy())
            except Exception as e:
                ecrire_log_erreur("Difference Pillow", e)
        self._message_statut(tr("missing_dep"))
        return QPixmap()

class BarreMiniatures(QListWidget):
    reordonne = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFlow(QListWidget.LeftToRight)
        self.setIconSize(QSize(80, 80))
        self.setFixedHeight(110)
        self.setSpacing(10)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        
    def charger(self, chemins):
        self.clear()
        for c in chemins:
            item = QListWidgetItem()
            icon = QPixmap(c).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            item.setIcon(QIcon(icon))
            item.setToolTip(os.path.basename(c))
            item.setData(Qt.UserRole, c)
            self.addItem(item)

    def dropEvent(self, event):
        super().dropEvent(event)
        chemins = [self.item(i).data(Qt.UserRole) for i in range(self.count())]
        self.reordonne.emit(chemins)

    def mousePressEvent(self, event):
        self.setFocus()
        super().mousePressEvent(event)

class DialogueRaccourcis(QDialog):
    """Fenetre recapitulative des raccourcis clavier (pour les nouveaux
    utilisateurs decouvrant le logiciel)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("shortcuts_title"))
        self.resize(440, 520)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(4)

        # Structure : (titre de section, [(touche, description), ...])
        sections = [
            (tr("shortcuts_section_general"), [
                ("F", tr("sc_fullscreen")),
                ("Ctrl + C", tr("sc_copy")),
                ("Ctrl + S", tr("sc_export")),
                ("Ctrl + Shift + S", tr("sc_quick_export")),
                ("Ctrl + Tab", tr("sc_switch_tabs")),
                ("Suppr / Del", tr("sc_delete_pack")),
            ]),
            (tr("shortcuts_section_compare"), [
                ("Tab / Shift + Tab", tr("sc_next_pack")),
                ("Ctrl + " + tr("sc_zoom").split()[0], tr("sc_zoom")),
                (tr("sc_pan").split()[0], tr("sc_pan")),
                (tr("img_word") and "Espace / Space", tr("sc_blink")),
                ("Ctrl + Z", tr("sc_undo")),
                ("← → ↑ ↓", tr("sc_move_cursor")),
            ]),
            (tr("shortcuts_section_compil"), [
                ("Clic / Click", tr("sc_comp_select")),
                ("Suppr / Del", tr("sc_comp_delete")),
                ("Ctrl + Glisser", tr("sc_comp_swap")),
                ("Glisser / Drag", tr("sc_comp_adjust")),
                ("Molette / Wheel", tr("sc_comp_zoom_cell")),
                ("Tab / Shift + Tab", tr("sc_comp_next_cell")),
                ("Ctrl + Z", tr("sc_comp_undo")),
                ("Ctrl + Y", tr("sc_comp_redo")),
                ("Ctrl + S", tr("sc_comp_export")),
            ]),
        ]

        for titre, lignes in sections:
            lbl_t = QLabel(titre)
            lbl_t.setStyleSheet("font-weight:bold; font-size:14px; "
                                "color:#ff8c42; margin-top:10px;")
            layout.addWidget(lbl_t)
            for touche, desc in lignes:
                ligne = QHBoxLayout()
                lbl_k = QLabel(str(touche))
                lbl_k.setStyleSheet(
                    "background-color:#1d2839; border:1px solid #34425a; "
                    "border-radius:4px; padding:3px 8px; font-weight:bold;")
                lbl_k.setFixedWidth(150)
                lbl_k.setAlignment(Qt.AlignCenter)
                lbl_d = QLabel(desc)
                lbl_d.setWordWrap(True)
                ligne.addWidget(lbl_k)
                ligne.addSpacing(10)
                ligne.addWidget(lbl_d, 1)
                layout.addLayout(ligne)

        layout.addStretch()
        btn = QPushButton(tr("close"))
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(self.accept)
        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(btn)
        layout.addLayout(h)


class DialogueParametres(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle(tr("settings_title"))
        self.resize(380, 520)
        layout = QVBoxLayout(self)

        # --- SECTION LANGUE ---
        lbl_lang_sec = QLabel(tr("settings_language_section"))
        lbl_lang_sec.setStyleSheet("font-weight:bold; color:#ff8c42;")
        layout.addWidget(lbl_lang_sec)

        h_lang = QHBoxLayout()
        h_lang.addWidget(QLabel(tr("language")))
        self.combo_lang = QComboBox()
        # Remplissage dynamique : toutes les langues connues (integrees + importees).
        self.codes_langues = []
        for code in sorted(LANGUAGES.keys()):
            self.combo_lang.addItem(NOMS_LANGUES.get(code, code), code)
            self.codes_langues.append(code)
        # Selectionner la langue courante.
        cur = config.get("language")
        if cur in self.codes_langues:
            self.combo_lang.setCurrentIndex(self.codes_langues.index(cur))
        h_lang.addWidget(self.combo_lang)
        layout.addLayout(h_lang)

        # Export / import de fichiers de langue.
        h_io = QHBoxLayout()
        btn_exp_lang = QPushButton(tr("settings_export_lang"))
        btn_exp_lang.clicked.connect(self.exporter_langue)
        btn_imp_lang = QPushButton(tr("settings_import_lang"))
        btn_imp_lang.clicked.connect(self.importer_langue)
        h_io.addWidget(btn_exp_lang)
        h_io.addWidget(btn_imp_lang)
        layout.addLayout(h_io)

        lbl_aide = QLabel(tr("settings_translate_help"))
        lbl_aide.setWordWrap(True)
        lbl_aide.setStyleSheet("color:#8b97a8; font-size:11px;")
        layout.addWidget(lbl_aide)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("color:#283750; background:#283750; max-height:1px;")
        layout.addSpacing(6)
        layout.addWidget(sep1)
        layout.addSpacing(6)

        # --- SECTION CURSEUR / LABELS ---
        h_col = QHBoxLayout()
        h_col.addWidget(QLabel(tr("cursor_color")))
        self.btn_col = QPushButton()
        self.btn_col.setStyleSheet(f"background-color: {config.get('cursor_color')};")
        self.btn_col.clicked.connect(self.choisir_couleur)
        h_col.addWidget(self.btn_col)
        layout.addLayout(h_col)

        h_ep = QHBoxLayout()
        h_ep.addWidget(QLabel(tr("cursor_thickness")))
        self.spin_ep = QSpinBox()
        self.spin_ep.setRange(1, 10)
        self.spin_ep.setValue(config.get("cursor_thickness"))
        h_ep.addWidget(self.spin_ep)
        layout.addLayout(h_ep)

        h_taille = QHBoxLayout()
        h_taille.addWidget(QLabel(tr("label_size")))
        self.spin_taille = QSpinBox()
        self.spin_taille.setRange(8, 40)
        self.spin_taille.setValue(config.get("label_size"))
        h_taille.addWidget(self.spin_taille)
        layout.addLayout(h_taille)

        h_op = QHBoxLayout()
        h_op.addWidget(QLabel(tr("label_opacity")))
        self.slider_op = QSlider(Qt.Horizontal)
        self.slider_op.setRange(0, 255)
        self.slider_op.setValue(config.get("label_bg_opacity"))
        h_op.addWidget(self.slider_op)
        layout.addLayout(h_op)

        layout.addSpacing(10)
        self.cb_watermark = QCheckBox(tr("watermark_enable"))
        self.cb_watermark.setChecked(config.get("watermark_enabled"))
        layout.addWidget(self.cb_watermark)
        
        h_wm = QHBoxLayout()
        h_wm.addWidget(QLabel(tr("watermark_text")))
        self.edit_wm = QLineEdit(config.get("watermark_text"))
        h_wm.addWidget(self.edit_wm)
        layout.addLayout(h_wm)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color:#283750; background:#283750; max-height:1px;")
        layout.addSpacing(6)
        layout.addWidget(sep2)
        layout.addSpacing(6)

        # --- SECTION COMPARATEUR : curseur en direct + zoom loupe ---
        self.cb_slider_live = QCheckBox(tr("settings_slider_live"))
        self.cb_slider_live.setChecked(bool(config.get("slider_live")))
        layout.addWidget(self.cb_slider_live)

        self.cb_pack_overlay = QCheckBox(tr("settings_pack_overlay"))
        self.cb_pack_overlay.setChecked(bool(config.get("show_pack_name_overlay")))
        layout.addWidget(self.cb_pack_overlay)

        h_loupe = QHBoxLayout()
        h_loupe.addWidget(QLabel(tr("settings_loupe_zoom")))
        self.spin_loupe = QSpinBox()
        self.spin_loupe.setRange(2, 10)
        self.spin_loupe.setValue(int(config.get("loupe_zoom") or 3))
        h_loupe.addWidget(self.spin_loupe)
        layout.addLayout(h_loupe)

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("color:#283750; background:#283750; max-height:1px;")
        layout.addSpacing(6)
        layout.addWidget(sep3)
        layout.addSpacing(6)

        # --- BOUTON RACCOURCIS ---
        btn_sc = QPushButton(tr("settings_shortcuts_btn"))
        btn_sc.clicked.connect(self.ouvrir_raccourcis)
        layout.addWidget(btn_sc)

        layout.addStretch()
        btn_box = QHBoxLayout()
        btn_ok = QPushButton(tr("close"))
        btn_ok.setObjectName("PrimaryButton")
        btn_ok.clicked.connect(self.accept)
        btn_box.addStretch()
        btn_box.addWidget(btn_ok)
        layout.addSpacing(10)
        layout.addLayout(btn_box)

        self.spin_ep.valueChanged.connect(self.sauvegarder_live)
        self.spin_taille.valueChanged.connect(self.sauvegarder_live)
        self.slider_op.valueChanged.connect(self.sauvegarder_live)
        self.cb_watermark.stateChanged.connect(self.sauvegarder_live)
        self.edit_wm.textChanged.connect(self.sauvegarder_live)
        self.cb_slider_live.stateChanged.connect(self.sauvegarder_live)
        self.cb_pack_overlay.stateChanged.connect(self.sauvegarder_live)
        self.spin_loupe.valueChanged.connect(self.sauvegarder_live)
        self.combo_lang.currentIndexChanged.connect(self.changer_langue)

    def ouvrir_raccourcis(self):
        dlg = DialogueRaccourcis(self)
        dlg.exec_()

    def exporter_langue(self):
        """Exporte la langue courante comme modele .json a traduire."""
        code = config.get("language")
        base = LANGUAGES.get(code) or LANGUAGES.get("en", {})
        modele = {"_meta": {"code": "xx", "name": "My Language"}}
        modele.update(base)
        chemin, _ = QFileDialog.getSaveFileName(
            self, tr("settings_export_lang"),
            os.path.join(DOSSIER_LANGUES if os.path.isdir(DOSSIER_LANGUES)
                         else DOSSIER_SCRIPT, "ma_langue.json"),
            "JSON (*.json)")
        if not chemin:
            return
        try:
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(modele, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, tr("info"),
                                    tr("settings_lang_exported", path=chemin))
        except Exception as e:
            QMessageBox.critical(self, tr("error"), str(e))

    def importer_langue(self):
        """Importe un fichier .json de langue : il est copie dans le dossier
        'langues' et ajoute immediatement a la liste."""
        chemin, _ = QFileDialog.getOpenFileName(
            self, tr("settings_import_lang"),
            DOSSIER_LANGUES if os.path.isdir(DOSSIER_LANGUES) else DOSSIER_SCRIPT,
            "JSON (*.json)")
        if not chemin:
            return
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta = data.get("_meta", {})
            code = meta.get("code") or os.path.splitext(os.path.basename(chemin))[0]
            nom = meta.get("name", code)
            traductions = {k: v for k, v in data.items() if k != "_meta"}
            # Copie dans le dossier des langues pour persistance.
            os.makedirs(DOSSIER_LANGUES, exist_ok=True)
            dest = os.path.join(DOSSIER_LANGUES, "%s.json" % code)
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            # Fusion immediate.
            if code in LANGUAGES:
                LANGUAGES[code].update(traductions)
            else:
                LANGUAGES[code] = traductions
            NOMS_LANGUES[code] = nom
            # Ajout a la combo si nouvelle langue.
            if code not in self.codes_langues:
                self.combo_lang.addItem(nom, code)
                self.codes_langues.append(code)
            QMessageBox.information(self, tr("info"),
                                    tr("settings_lang_imported", name=nom))
        except Exception:
            QMessageBox.critical(self, tr("error"), tr("settings_lang_err"))

    def choisir_couleur(self):
        c = QColorDialog.getColor(QColor(config.get("cursor_color")), self, "Color")
        if c.isValid():
            self.btn_col.setStyleSheet(f"background-color: {c.name()};")
            config.set("cursor_color", c.name())
            if self.main_window: self.main_window.vue_comparateur.update()

    def sauvegarder_live(self):
        config.set("cursor_thickness", self.spin_ep.value())
        config.set("label_size", self.spin_taille.value())
        config.set("label_bg_opacity", self.slider_op.value())
        config.set("watermark_enabled", self.cb_watermark.isChecked())
        config.set("watermark_text", self.edit_wm.text())
        config.set("slider_live", self.cb_slider_live.isChecked())
        config.set("show_pack_name_overlay", self.cb_pack_overlay.isChecked())
        config.set("loupe_zoom", self.spin_loupe.value())
        if self.main_window:
            vc = self.main_window.vue_comparateur
            # Application immediate des reglages du comparateur.
            vc.slider_live = self.cb_slider_live.isChecked()
            vc.loupe_zoom = float(self.spin_loupe.value())
            vc.update()

    def changer_langue(self, index):
        if 0 <= index < len(self.codes_langues):
            new_lang = self.codes_langues[index]
            if new_lang != config.get("language"):
                config.set("language", new_lang)
                QMessageBox.information(self, tr("info"), tr("restart_lang"))

class DialogueRecents(QDialog):
    """Fenetre listant les comparaisons recemment ouvertes. Double-clic
    ou bouton Ouvrir pour recharger une comparaison dans le comparateur.
    L'historique persiste entre les sessions (cle 'recent_packs')."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle(tr("recent_title"))
        self.resize(460, 480)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        titre = QLabel(tr("recent_title"))
        titre.setStyleSheet("font-weight:bold; font-size:16px;")
        layout.addWidget(titre)

        self.liste = QListWidget()
        self.liste.setIconSize(QSize(48, 48))
        self.liste.itemDoubleClicked.connect(self._ouvrir_selection)
        layout.addWidget(self.liste, 1)

        self.recents = config.get("recent_packs") or []
        self._remplir_liste()

        ligne = QHBoxLayout()
        self.btn_clear = QPushButton(tr("recent_clear"))
        self.btn_clear.setObjectName("DangerButton")
        self.btn_clear.clicked.connect(self._vider_historique)
        btn_ouvrir = QPushButton(tr("recent_open"))
        btn_ouvrir.setObjectName("PrimaryButton")
        btn_ouvrir.clicked.connect(self._ouvrir_selection)
        btn_fermer = QPushButton(tr("close"))
        btn_fermer.clicked.connect(self.accept)
        ligne.addWidget(self.btn_clear)
        ligne.addStretch()
        ligne.addWidget(btn_ouvrir)
        ligne.addWidget(btn_fermer)
        layout.addLayout(ligne)

    def _remplir_liste(self):
        """Peuple la liste ; affiche un message si l'historique est vide."""
        self.liste.clear()
        if not self.recents:
            item = QListWidgetItem(tr("recent_empty"))
            item.setFlags(Qt.NoItemFlags)
            self.liste.addItem(item)
            self.btn_clear.setEnabled(False)
            return
        self.btn_clear.setEnabled(True)
        for entree in self.recents:
            chemins = entree.get("chemins", [])
            date = entree.get("date", "")
            libelle = "%s\n%s" % (entree.get("nom", "?"), date)
            item = QListWidgetItem(libelle)
            # Vignette : 1re image existante de la comparaison.
            for c in chemins:
                if os.path.isfile(c):
                    pix = QPixmap(c).scaled(48, 48, Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)
                    item.setIcon(QIcon(pix))
                    break
            item.setData(Qt.UserRole, chemins)
            self.liste.addItem(item)

    def _ouvrir_selection(self, *args):
        """Recharge la comparaison selectionnee puis ferme la fenetre."""
        item = self.liste.currentItem()
        if item is None:
            return
        chemins = item.data(Qt.UserRole)
        if not chemins:
            return
        self.accept()
        if self.parent_app is not None:
            self.parent_app.charger_pack_recent(chemins)

    def _vider_historique(self):
        """Efface l'historique des recents apres confirmation."""
        rep = QMessageBox.question(self, tr("recent_clear"),
                                   tr("clear_confirm"),
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            self.recents = []
            config.set("recent_packs", [])
            self._remplir_liste()

class DialogueExport(QDialog):
    def __init__(self, parent, zoom_actif):
        super().__init__(parent)
        self.setWindowTitle(tr("export_title"))
        self.resize(350, 200)
        layout = QVBoxLayout(self)

        self.cb_labels = QCheckBox(tr("export_labels"))
        self.cb_labels.setChecked(True)
        layout.addWidget(self.cb_labels)

        self.cb_zoom = QCheckBox(tr("export_zoom"))
        self.cb_zoom.setChecked(zoom_actif)
        self.cb_zoom.setEnabled(zoom_actif)
        layout.addWidget(self.cb_zoom)

        h_fmt = QHBoxLayout()
        h_fmt.addWidget(QLabel(tr("format")))
        self.combo_format = QComboBox()
        self.combo_format.addItems(["JPEG (*.jpg)", "PNG (*.png)"])
        if HAS_PIL and parent.vue_comparateur.ratios:
            self.combo_format.addItem("GIF Animé (*.gif)" if config.get("language") == "fr" else "Animated GIF (*.gif)")
        h_fmt.addWidget(self.combo_format)
        layout.addLayout(h_fmt)

        btn_box = QHBoxLayout()
        btn_ok = QPushButton(tr("export_btn"))
        btn_ok.setObjectName("PrimaryButton")
        btn_ok.clicked.connect(self.accept)
        btn_box.addStretch()
        btn_box.addWidget(btn_ok)
        layout.addSpacing(20)
        layout.addLayout(btn_box)

    def get_resultats(self):
        fmt = self.combo_format.currentText()
        ext = ".jpg" if "JPEG" in fmt else (".png" if "PNG" in fmt else ".gif")
        return self.cb_labels.isChecked(), self.cb_zoom.isChecked(), ext

class FenetreHeatmap(QWidget):
    def __init__(self, chemin_image, texte_info=None):
        super().__init__() 
        if texte_info is None:
            texte_info = tr("heatmap_info")
            
        self.setWindowTitle(tr("heatmap_title"))
        self.resize(1000, 800)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #161f2e; border-bottom: 1px solid #283750;")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(15, 10, 15, 10)

        lbl_info = QLabel(texte_info)
        lbl_info.setStyleSheet("font-size: 14px; font-weight: bold;")

        btn_fermer = QPushButton(tr("close"))
        btn_fermer.setObjectName("PrimaryButton")
        btn_fermer.clicked.connect(self.close)

        tb_layout.addWidget(lbl_info)
        tb_layout.addStretch()
        tb_layout.addWidget(btn_fermer)

        self.lbl_img = QLabel()
        self.lbl_img.setAlignment(Qt.AlignCenter)
        self.lbl_img.setStyleSheet("background-color: #0f1623;")
        self.pixmap_original = QPixmap(chemin_image)

        layout.addWidget(toolbar)
        layout.addWidget(self.lbl_img, 1)

    def resizeEvent(self, event):
        if hasattr(self, 'pixmap_original') and not self.pixmap_original.isNull():
            self.lbl_img.setPixmap(self.pixmap_original.scaled(
                self.lbl_img.width() - 20, 
                self.lbl_img.height() - 20, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
        super().resizeEvent(event)

class LogicielComparateur(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app_title"))
        self.resize(1200, 800)
        self.chemins_actuels = []
        self.packs = []

        widget_central = QWidget()
        layout_global = QHBoxLayout(widget_central)
        layout_global.setContentsMargins(0, 0, 0, 0)
        layout_global.setSpacing(0)

        self.panneau_gauche = QFrame()
        self.panneau_gauche.setObjectName("Sidebar")
        self.panneau_gauche.setFixedWidth(220)
        layout_gauche = QVBoxLayout(self.panneau_gauche)
        layout_gauche.setContentsMargins(10, 10, 10, 10)
        
        lbl_packs = QLabel(tr("my_comparisons"))
        lbl_packs.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.liste_packs_ui = QListWidget()
        self.liste_packs_ui.setIconSize(QSize(50, 50)) 
        self.liste_packs_ui.currentRowChanged.connect(self.charger_pack_depuis_liste)
        
        btn_nouveau = QPushButton(tr("new_pack"))
        btn_nouveau.setObjectName("PrimaryButton")
        btn_nouveau.clicked.connect(self.parcourir)

        btn_recents = QPushButton(tr("recent_btn"))
        btn_recents.clicked.connect(self.ouvrir_recents)

        btn_supprimer_pack = QPushButton(tr("del_pack"))
        btn_supprimer_pack.clicked.connect(self.supprimer_pack_actuel)

        btn_vider_liste = QPushButton(tr("clear_list"))
        btn_vider_liste.setObjectName("DangerButton")
        btn_vider_liste.clicked.connect(self.vider_liste_packs)
        
        layout_gauche.addWidget(lbl_packs)
        layout_gauche.addWidget(self.liste_packs_ui)
        layout_gauche.addWidget(btn_nouveau)
        layout_gauche.addWidget(btn_recents)
        layout_gauche.addWidget(btn_supprimer_pack)
        layout_gauche.addWidget(btn_vider_liste)

        zone_droite = QWidget()
        layout_principal = QVBoxLayout(zone_droite)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        self.toolbar = QFrame()
        self.toolbar.setObjectName("Toolbar")
        layout_tb = QHBoxLayout(self.toolbar)
        
        self.btn_ori = QPushButton(tr("vertical") if config.get("orientation")=="Vertical" else tr("horizontal"))
        self.btn_ori.clicked.connect(self.toggle_orientation)

        btn_centrer = QPushButton(tr("center"))
        btn_centrer.clicked.connect(self.centrer_vue)

        # Selecteur de mode d'affichage : curseur / cote a cote / difference.
        self.combo_mode = QComboBox()
        self.combo_mode.addItem(tr("view_mode_slider"), "slider")
        self.combo_mode.addItem(tr("view_mode_side"), "side")
        self.combo_mode.addItem(tr("view_mode_diff"), "diff")
        self.combo_mode.currentIndexChanged.connect(self.changer_mode_affichage)

        # Bouton-bascule de la loupe.
        self.btn_loupe = QPushButton(tr("loupe_enable"))
        self.btn_loupe.setCheckable(True)
        self.btn_loupe.toggled.connect(self.basculer_loupe)

        self.btn_reset_align = QPushButton(tr("originals"))
        self.btn_reset_align.clicked.connect(self.annuler_alignement)
        self.btn_reset_align.hide()

        btn_align = QPushButton(tr("auto_align"))
        btn_align.clicked.connect(self.aligner_images)

        btn_heatmap = QPushButton(tr("heatmap_btn"))
        btn_heatmap.clicked.connect(self.generer_heatmap)

        # Bouton mesure de similarite chiffree (SSIM / PSNR / % pixels).
        btn_similarity = QPushButton(tr("similarity_btn"))
        btn_similarity.clicked.connect(self.afficher_similarite)

        btn_copy = QPushButton(tr("copy"))
        btn_copy.clicked.connect(self.copier_presse_papier)

        btn_exp = QPushButton(tr("export"))
        btn_exp.setObjectName("PrimaryButton")
        btn_exp.clicked.connect(self.ouvrir_export)
        
        layout_tb.addWidget(self.btn_ori)
        layout_tb.addWidget(btn_centrer)
        layout_tb.addWidget(self.combo_mode)
        layout_tb.addWidget(self.btn_loupe)
        layout_tb.addStretch()
        layout_tb.addWidget(self.btn_reset_align)
        layout_tb.addWidget(btn_align)
        layout_tb.addWidget(btn_heatmap)
        layout_tb.addWidget(btn_similarity)
        layout_tb.addWidget(btn_copy)
        layout_tb.addWidget(btn_exp)

        self.stack = QStackedWidget()
        
        vue_accueil = QFrame()
        vue_accueil.setObjectName("DropFrame")
        layout_acc = QVBoxLayout(vue_accueil)
        lbl_acc = QLabel(tr("drop_text"))
        lbl_acc.setObjectName("Titre")
        lbl_acc.setAlignment(Qt.AlignCenter)
        layout_acc.addWidget(lbl_acc)
        
        self.vue_comparateur = ComparateurWidget()
        self.stack.addWidget(vue_accueil)
        self.stack.addWidget(self.vue_comparateur)

        self.zone_miniatures_globale = QWidget()
        layout_min_glob = QHBoxLayout(self.zone_miniatures_globale)
        layout_min_glob.setContentsMargins(10, 5, 10, 5)
        
        self.barre_miniatures = BarreMiniatures()
        self.barre_miniatures.reordonne.connect(self.reorganiser_images)
        
        zone_btn_min = QWidget()
        layout_btn_min = QVBoxLayout(zone_btn_min)
        layout_btn_min.setContentsMargins(0, 0, 0, 0)
        
        btn_add_img = QPushButton(tr("add_img"))
        btn_add_img.clicked.connect(self.ajouter_image_au_pack)
        
        btn_del_img = QPushButton(tr("remove_img"))
        btn_del_img.setObjectName("DangerButton")
        btn_del_img.clicked.connect(self.enlever_image_du_pack)
        
        layout_btn_min.addStretch()
        layout_btn_min.addWidget(btn_add_img)
        layout_btn_min.addWidget(btn_del_img)
        layout_btn_min.addStretch()
        
        layout_min_glob.addWidget(self.barre_miniatures, 1)
        layout_min_glob.addWidget(zone_btn_min)

        layout_principal.addWidget(self.toolbar)
        layout_principal.addWidget(self.stack, 1)
        layout_principal.addWidget(self.zone_miniatures_globale)
        self.barre_statut_comparateur = QLabel("")
        self.barre_statut_comparateur.setStyleSheet(
            "QLabel { background-color:#161f2e; color:#8b97a8; "
            "border-top:1px solid #283750; padding:5px 12px; "
            "font-size:12px; }")
        self.barre_statut_comparateur.setMinimumHeight(28)
        layout_principal.addWidget(self.barre_statut_comparateur)
        self._timer_statut_comparateur = QTimer(self)
        self._timer_statut_comparateur.setSingleShot(True)
        self._timer_statut_comparateur.timeout.connect(
            lambda: self.barre_statut_comparateur.setText(""))
        
        layout_global.addWidget(self.panneau_gauche)
        layout_global.addWidget(zone_droite, 1)

        # --- SYSTEME D'ONGLETS : Comparateur / Compilation ---
        # widget_central (tout le comparateur) devient l'onglet 1.
        # Le module de compilation, s'il est present, devient l'onglet 2.
        self.onglets = QTabWidget()
        self.onglets.setObjectName("OngletsPrincipaux")
        self.onglets.addTab(widget_central, "🔍  " + tr("tab_comparateur"))

        if HAS_COMPILATION:
            self.widget_compilation = compilation_module.creer_widget_compilation(self)
            self.onglets.addTab(self.widget_compilation,
                                "🧩  " + tr("tab_compilation"))

        # Bouton Parametres place dans le coin de la barre d'onglets :
        # toujours visible, quel que soit l'onglet actif et meme sans pack.
        self.btn_settings_coin = QPushButton(tr("settings"))
        self.btn_settings_coin.setObjectName("SettingsCorner")
        self.btn_settings_coin.setCursor(Qt.PointingHandCursor)
        self.btn_settings_coin.clicked.connect(self.ouvrir_parametres)
        self.onglets.setCornerWidget(self.btn_settings_coin, Qt.TopRightCorner)

        self.setCentralWidget(self.onglets)
        self.setAcceptDrops(True)
        self.toolbar.hide()
        self.zone_miniatures_globale.hide()

        self.restaurer_session()

    def restaurer_session(self):
        last_packs = config.get("last_packs")
        last_idx = config.get("last_pack_index")
        if last_packs:
            packs_valides = []
            for p in last_packs:
                chemins_valides = [c for c in p["chemins"] if os.path.exists(c)]
                chemins_orig = p.get("chemins_originaux")
                if chemins_orig:
                    chemins_orig = [c for c in chemins_orig if os.path.exists(c)]
                if len(chemins_valides) >= 2:
                    packs_valides.append({
                        "nom": p["nom"], 
                        "chemins": chemins_valides,
                        "chemins_originaux": chemins_orig if chemins_orig and len(chemins_orig) >= 2 else None
                    })
            self.packs = packs_valides
            for p in self.packs:
                item = QListWidgetItem(p["nom"])
                icon = QPixmap(p["chemins"][0]).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item.setIcon(QIcon(icon))
                self.liste_packs_ui.addItem(item)
            if self.packs:
                idx = last_idx if (last_idx is not None and 0 <= last_idx < len(self.packs)) else 0
                self.liste_packs_ui.setCurrentRow(idx)

    def sauvegarder_session(self):
        config.set("last_packs", self.packs)
        config.set("last_pack_index", self.liste_packs_ui.currentRow())

    def closeEvent(self, event):
        if HAS_COMPILATION and hasattr(self, "widget_compilation"):
            widget = self.widget_compilation
            try:
                widget._sauver_pack_courant()
                packs_compilation = getattr(widget, "batch_packs", [])
                if packs_compilation:
                    rep = QMessageBox.question(
                        self, tr("warning"), tr("close_compilation_packs"),
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if rep != QMessageBox.Yes:
                        event.ignore()
                        return
                if hasattr(widget, "sauvegarder_reglages"):
                    widget.sauvegarder_reglages()
            except Exception as e:
                ecrire_log_erreur("Fermeture compilation", e)
        config.set("last_packs", [])
        config.set("last_pack_index", 0)
        super().closeEvent(event)

    def parcourir(self):
        fichiers, _ = QFileDialog.getOpenFileNames(self, "Selection", "", "Images (*.png *.jpg *.jpeg)")
        if len(fichiers) >= 2: 
            self.creer_nouveau_pack(fichiers)

    def creer_nouveau_pack(self, chemins):
        dossier = os.path.basename(os.path.dirname(chemins[0]))
        nom_pack = f"{dossier} ({len(chemins)} {tr('img_word')})"
        self.packs.append({"nom": nom_pack, "chemins": chemins, "chemins_originaux": None})
        item = QListWidgetItem(nom_pack)
        icon = QPixmap(chemins[0]).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        item.setIcon(QIcon(icon))
        self.liste_packs_ui.addItem(item)
        self.liste_packs_ui.setCurrentRow(len(self.packs) - 1)
        self._enregistrer_recent(nom_pack, chemins)

    def _enregistrer_recent(self, nom_pack, chemins):
        """Ajoute une comparaison en tete de l'historique des recents.
        Deduplique sur la liste de chemins, limite a 10 entrees. Cet
        historique persiste (contrairement a last_packs vide a la
        fermeture)."""
        try:
            recents = config.get("recent_packs") or []
            # On retire un eventuel doublon (meme jeu d'images).
            recents = [r for r in recents
                       if r.get("chemins") != list(chemins)]
            recents.insert(0, {
                "nom": nom_pack,
                "chemins": list(chemins),
                "date": time.strftime("%Y-%m-%d %H:%M"),
            })
            config.set("recent_packs", recents[:10])
        except Exception:
            # L'historique est un confort : ne jamais bloquer sur lui.
            pass

    def ouvrir_recents(self):
        """Affiche la fenetre listant les comparaisons recentes."""
        dlg = DialogueRecents(self)
        dlg.exec_()

    def charger_pack_recent(self, chemins):
        """Recharge une comparaison depuis l'historique. Les images
        disparues du disque sont ignorees ; on previent l'utilisateur."""
        existants = [c for c in chemins if os.path.isfile(c)]
        if not existants:
            QMessageBox.warning(self, tr("warning"), tr("recent_gone"))
            return
        if len(existants) != len(chemins):
            QMessageBox.information(self, tr("warning"), tr("recent_missing"))
        if len(existants) < 2:
            QMessageBox.warning(self, tr("warning"), tr("recent_not_enough"))
            return
        self.creer_nouveau_pack(existants)

    def charger_pack_depuis_liste(self, index):
        if index < 0 or index >= len(self.packs):
            self.stack.setCurrentIndex(0)
            self.toolbar.hide()
            self.zone_miniatures_globale.hide()
            self.vue_comparateur.nom_pack = ""
            return
        pack = self.packs[index]
        self.chemins_actuels = pack["chemins"]
        if pack.get("chemins_originaux"):
            self.btn_reset_align.show()
        else:
            self.btn_reset_align.hide()
        self.vue_comparateur.nom_pack = pack.get("nom", "")
        self.vue_comparateur.charger_images(self.chemins_actuels)
        self.barre_miniatures.charger(self.chemins_actuels)
        self.toolbar.show()
        self.zone_miniatures_globale.show()
        self.stack.setCurrentIndex(1)
        self.sauvegarder_session()

    def supprimer_pack_actuel(self):
        idx = self.liste_packs_ui.currentRow()
        if idx >= 0:
            self.packs.pop(idx)
            self.liste_packs_ui.takeItem(idx)
            self.sauvegarder_session()

    def vider_liste_packs(self):
        if self.packs:
            reponse = QMessageBox.question(self, tr("clear_list"), tr("clear_confirm"), QMessageBox.Yes | QMessageBox.No)
            if reponse == QMessageBox.Yes:
                self.packs.clear()
                self.liste_packs_ui.clear()
                self.sauvegarder_session()
                self.stack.setCurrentIndex(0)
                self.toolbar.hide()
                self.zone_miniatures_globale.hide()

    def ajouter_image_au_pack(self):
        if not self.chemins_actuels: return
        dossier_courant = os.path.dirname(self.chemins_actuels[0])
        fichiers, _ = QFileDialog.getOpenFileNames(
            self, "Selection", dossier_courant,
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if fichiers:
            self.chemins_actuels.extend(fichiers)
            self.actualiser_pack_courant()

    def enlever_image_du_pack(self):
        if len(self.chemins_actuels) <= 2:
            QMessageBox.warning(self, tr("warning"), tr("warn_pack_min"))
            return
        items = self.barre_miniatures.selectedItems()
        if not items:
            QMessageBox.information(self, tr("info"), tr("info_sel_img"))
            return
        chemin_a_supprimer = items[0].data(Qt.UserRole)
        self.chemins_actuels.remove(chemin_a_supprimer)
        self.actualiser_pack_courant()

    def reorganiser_images(self, nouveaux_chemins):
        chemins_valides = []
        for chemin in nouveaux_chemins:
            if os.path.exists(chemin) and not QPixmap(chemin).isNull():
                chemins_valides.append(chemin)
            else:
                ecrire_log_erreur(tr("invalid_image_skip", path=chemin),
                                  RuntimeError("Chemin invalide"))
        if len(chemins_valides) < 2:
            QMessageBox.warning(self, tr("warning"), tr("warn_pack_min"))
            self.barre_miniatures.charger(self.chemins_actuels)
            return
        self.chemins_actuels = chemins_valides
        self.actualiser_pack_courant()

    def actualiser_pack_courant(self):
        idx = self.liste_packs_ui.currentRow()
        if idx >= 0:
            dossier = os.path.basename(os.path.dirname(self.chemins_actuels[0]))
            nom_pack = f"{dossier} ({len(self.chemins_actuels)} {tr('img_word')})"
            self.packs[idx]["chemins"] = self.chemins_actuels
            self.packs[idx]["nom"] = nom_pack
            item = self.liste_packs_ui.item(idx)
            item.setText(nom_pack)
            icon = QPixmap(self.chemins_actuels[0]).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            item.setIcon(QIcon(icon))
            self.charger_pack_depuis_liste(idx)

    def toggle_orientation(self):
        actuel = config.get("orientation")
        nouveau = "Horizontal" if actuel == "Vertical" else "Vertical"
        config.set("orientation", nouveau)
        self.btn_ori.setText(tr("vertical") if nouveau=="Vertical" else tr("horizontal"))
        self.vue_comparateur.update()

    def centrer_vue(self):
        self.vue_comparateur.reset_ratios()
        if self.vue_comparateur.mode_affichage == "slider":
            self.vue_comparateur.centrer_vue()
        else:
            self.vue_comparateur.centrer_vue_mode()
            self.vue_comparateur.update()

    def changer_mode_affichage(self, index):
        """Applique le mode d'affichage choisi dans la barre d'outils."""
        mode = self.combo_mode.itemData(index)
        if mode is None:
            mode = "slider"
        self.vue_comparateur.definir_mode(mode)
        if self.vue_comparateur.mode_affichage != mode:
            self.combo_mode.blockSignals(True)
            for i in range(self.combo_mode.count()):
                if self.combo_mode.itemData(i) == self.vue_comparateur.mode_affichage:
                    self.combo_mode.setCurrentIndex(i)
                    break
            self.combo_mode.blockSignals(False)

    def basculer_loupe(self, actif):
        """Active ou desactive la loupe qui suit le curseur."""
        self.vue_comparateur.loupe_active = bool(actif)
        self.vue_comparateur.update()

    def afficher_similarite(self):
        """Calcule SSIM / PSNR / pourcentage de pixels differents entre la
        reference et chaque autre image, puis affiche un recapitulatif."""
        if len(self.chemins_actuels) < 2:
            QMessageBox.warning(self, tr("warning"), tr("similarity_need_two"))
            return
        try:
            import cv2
            import numpy as np
        except ImportError:
            QMessageBox.warning(self, "Erreur / Error", tr("missing_dep"))
            return
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            ref = cv2.imdecode(np.fromfile(self.chemins_actuels[0], dtype=np.uint8),
                               cv2.IMREAD_COLOR)
            ref_gray = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
            lignes = []
            for i in range(1, len(self.chemins_actuels)):
                autre = cv2.imdecode(
                    np.fromfile(self.chemins_actuels[i], dtype=np.uint8),
                    cv2.IMREAD_COLOR)
                if autre.shape != ref.shape:
                    autre = cv2.resize(autre, (ref.shape[1], ref.shape[0]))
                autre_gray = cv2.cvtColor(autre, cv2.COLOR_BGR2GRAY)
                ssim = self._calculer_ssim(ref_gray, autre_gray, np)
                psnr = self._calculer_psnr(ref, autre, np)
                diff = cv2.absdiff(ref, autre)
                pixels_diff = np.count_nonzero(np.any(diff > 8, axis=2))
                total = ref.shape[0] * ref.shape[1]
                pct = 100.0 * pixels_diff / total if total else 0.0
                psnr_txt = "∞" if psnr == float("inf") else "%.2f dB" % psnr
                lignes.append((i + 1, ssim, psnr_txt, pct))
            QApplication.restoreOverrideCursor()
            self._afficher_dialogue_similarite(lignes)
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, tr("error"), tr("err_gen", err=str(e)))

    def _calculer_ssim(self, a, b, np):
        """SSIM global (implementation compacte, sans scikit-image)."""
        a = a.astype(np.float64)
        b = b.astype(np.float64)
        mu_a, mu_b = a.mean(), b.mean()
        var_a, var_b = a.var(), b.var()
        cov = ((a - mu_a) * (b - mu_b)).mean()
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2
        num = (2 * mu_a * mu_b + c1) * (2 * cov + c2)
        den = (mu_a ** 2 + mu_b ** 2 + c1) * (var_a + var_b + c2)
        return num / den if den else 1.0

    def _calculer_psnr(self, a, b, np):
        """PSNR en decibels entre deux images BGR."""
        mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
        if mse == 0:
            return float("inf")
        return 20 * np.log10(255.0) - 10 * np.log10(mse)

    def _afficher_dialogue_similarite(self, lignes):
        """Affiche un dialogue recapitulatif des scores de similarite."""
        dlg = QDialog(self)
        dlg.setWindowTitle(tr("similarity_title"))
        dlg.resize(420, 120 + 90 * len(lignes))
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(18, 18, 18, 18)
        for (idx, ssim, psnr_txt, pct) in lignes:
            bloc = QFrame()
            bloc.setStyleSheet(
                "QFrame { background-color:#161f2e; border:1px solid #283750;"
                " border-radius:8px; }")
            vb = QVBoxLayout(bloc)
            titre = QLabel(tr("similarity_info", idx=idx))
            titre.setStyleSheet("font-weight:bold; color:#ff8c42; border:none;")
            vb.addWidget(titre)
            for libelle, valeur in [
                    (tr("similarity_ssim"), "%.4f" % ssim),
                    (tr("similarity_psnr"), psnr_txt),
                    (tr("similarity_diffpct"), "%.2f %%" % pct)]:
                h = QHBoxLayout()
                lg = QLabel(libelle)
                lg.setStyleSheet("border:none;")
                vl = QLabel(valeur)
                vl.setStyleSheet("font-weight:bold; border:none;")
                h.addWidget(lg)
                h.addStretch()
                h.addWidget(vl)
                vb.addLayout(h)
            if ssim >= 0.9999:
                note = QLabel(tr("similarity_identical"))
                note.setStyleSheet("color:#46cd82; border:none;")
                vb.addWidget(note)
            lay.addWidget(bloc)
        lay.addStretch()
        btn = QPushButton(tr("close"))
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(dlg.accept)
        hb = QHBoxLayout()
        hb.addStretch()
        hb.addWidget(btn)
        lay.addLayout(hb)
        dlg.exec_()

    def aligner_images(self):
        if len(self.chemins_actuels) < 2: return
        try:
            import cv2
            import numpy as np
        except ImportError:
            QMessageBox.warning(self, "Erreur / Error", tr("missing_dep"))
            return
        QMessageBox.information(self, tr("info"), tr("align_start"))
        ref_path = self.chemins_actuels[0]
        nouveaux_chemins = [ref_path]
        try:
            ref_img = cv2.imdecode(np.fromfile(ref_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
            orb = cv2.ORB_create(5000)
            kp_ref, des_ref = orb.detectAndCompute(ref_gray, None)
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            for i in range(1, len(self.chemins_actuels)):
                tgt_path = self.chemins_actuels[i]
                tgt_img = cv2.imdecode(np.fromfile(tgt_path, dtype=np.uint8), cv2.IMREAD_COLOR)
                tgt_gray = cv2.cvtColor(tgt_img, cv2.COLOR_BGR2GRAY)
                kp_tgt, des_tgt = orb.detectAndCompute(tgt_gray, None)
                matches = matcher.match(des_tgt, des_ref)
                matches = sorted(matches, key=lambda x: x.distance)
                num_good_matches = int(len(matches) * 0.15)
                matches = matches[:max(num_good_matches, 10)]
                if len(matches) < 4:
                    raise ValueError(tr("err_sim", idx=i+1))
                points_tgt = np.zeros((len(matches), 2), dtype=np.float32)
                points_ref = np.zeros((len(matches), 2), dtype=np.float32)
                for j, match in enumerate(matches):
                    points_tgt[j, :] = kp_tgt[match.queryIdx].pt
                    points_ref[j, :] = kp_ref[match.trainIdx].pt
                matrix, inliers = cv2.estimateAffinePartial2D(points_tgt, points_ref, method=cv2.RANSAC)
                if matrix is None:
                    raise ValueError(tr("err_trans", idx=i+1))
                height, width = ref_img.shape[:2]
                aligned_img = cv2.warpAffine(tgt_img, matrix, (width, height))
                base, ext = os.path.splitext(tgt_path)
                out_path = f"{base}_aligned{ext}"
                is_success, im_buf_arr = cv2.imencode(ext, aligned_img)
                if is_success:
                    im_buf_arr.tofile(out_path)
                nouveaux_chemins.append(out_path)
            idx = self.liste_packs_ui.currentRow()
            if not self.packs[idx].get("chemins_originaux"):
                self.packs[idx]["chemins_originaux"] = list(self.chemins_actuels)
            self.chemins_actuels = nouveaux_chemins
            self.btn_reset_align.show()
            self.actualiser_pack_courant()
            QMessageBox.information(self, tr("success"), tr("align_success"))
        except Exception as e:
            QMessageBox.critical(self, tr("error"), tr("err_align", err=str(e)))

    def annuler_alignement(self):
        idx = self.liste_packs_ui.currentRow()
        if idx >= 0 and self.packs[idx].get("chemins_originaux"):
            self.chemins_actuels = self.packs[idx]["chemins_originaux"]
            self.packs[idx]["chemins_originaux"] = None
            self.btn_reset_align.hide()
            self.actualiser_pack_courant()

    def generer_heatmap(self):
        if len(self.chemins_actuels) < 2: return
        try:
            import cv2
            import numpy as np
        except ImportError:
            QMessageBox.warning(self, "Erreur / Error", tr("missing_dep"))
            return
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            ref_path = self.chemins_actuels[0]
            img_ref = cv2.imdecode(np.fromfile(ref_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            max_diff = np.zeros_like(img_ref)
            for i in range(1, len(self.chemins_actuels)):
                img_other = cv2.imdecode(np.fromfile(self.chemins_actuels[i], dtype=np.uint8), cv2.IMREAD_COLOR)
                if img_ref.shape != img_other.shape:
                    img_other = cv2.resize(img_other, (img_ref.shape[1], img_ref.shape[0]))
                diff = cv2.absdiff(img_ref, img_other)
                max_diff = cv2.max(max_diff, diff)
            gray = cv2.cvtColor(max_diff, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 3, 255, cv2.THRESH_TOZERO)
            heatmap = cv2.applyColorMap(thresh, cv2.COLORMAP_JET)
            blended = cv2.addWeighted(img_ref, 0.4, heatmap, 0.6, 0)
            base, ext = os.path.splitext(ref_path)
            out_path = f"{base}_heatmap_cumulee{ext}"
            is_success, im_buf_arr = cv2.imencode(ext, blended)
            if is_success: im_buf_arr.tofile(out_path)
            QApplication.restoreOverrideCursor()
            texte = tr("heatmap_global", count=len(self.chemins_actuels))
            self.fenetre_hm = FenetreHeatmap(out_path, texte)
            self.fenetre_hm.show()
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, tr("error"), tr("err_gen", err=str(e)))

    def ouvrir_parametres(self):
        dlg = DialogueParametres(self)
        dlg.exec_() 

    def generer_pixmap_export(self, avec_labels, zoom_actif):
        if not self.vue_comparateur.images_originales:
            return QPixmap()
        if zoom_actif:
            mem_labels = self.vue_comparateur.afficher_labels
            self.vue_comparateur.afficher_labels = avec_labels
            pix = self.vue_comparateur.grab()
            self.vue_comparateur.afficher_labels = mem_labels
            if config.get("watermark_enabled") and config.get("watermark_text"):
                texte_f = config.get("watermark_text")
                painter = QPainter(pix)
                font = QFont("Segoe UI", max(16, pix.height() // 40), QFont.Bold)
                painter.setFont(font)
                painter.setPen(QColor(255, 255, 255, 160))
                rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte_f)
                painter.drawText(pix.width() - rect_text.width() - 20, pix.height() - 20, texte_f)
                painter.end()
            return pix
        if self.vue_comparateur.mode_affichage == "diff":
            pix_diff = self.vue_comparateur.pixmap_diff
            if pix_diff is None or pix_diff.isNull():
                return QPixmap()
            pix = QPixmap(pix_diff)
            if config.get("watermark_enabled") and config.get("watermark_text"):
                texte_f = config.get("watermark_text")
                painter = QPainter(pix)
                font = QFont("Segoe UI", max(16, pix.height() // 40), QFont.Bold)
                painter.setFont(font)
                painter.setPen(QColor(255, 255, 255, 160))
                rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte_f)
                painter.drawText(pix.width() - rect_text.width() - 20, pix.height() - 20, texte_f)
                painter.end()
            return pix
        if self.vue_comparateur.mode_affichage == "side":
            rects, virt_w, virt_h = self.vue_comparateur._disposition_side()
            pix = QPixmap(virt_w, virt_h)
            pix.fill(Qt.transparent)
            painter = QPainter(pix)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            for i, img in enumerate(self.vue_comparateur.images_originales):
                rx, ry, rw, rh = rects[i]
                painter.drawPixmap(QRect(rx, ry, rw, rh), img,
                                   QRect(0, 0, img.width(), img.height()))
            if avec_labels:
                taille_label_base = config.get("label_size")
                opacite = config.get("label_bg_opacity")
                for i, texte in enumerate(self.vue_comparateur.infos_images):
                    rx, ry, rw, rh = rects[i]
                    font = QFont("Segoe UI", taille_label_base, QFont.Bold)
                    painter.setFont(font)
                    rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte)
                    bg_rect = QRect(rx + 5, ry + 5, rect_text.width() + 10,
                                    rect_text.height() + 10)
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor(0, 0, 0, opacite))
                    painter.drawRoundedRect(bg_rect, 5, 5)
                    painter.setPen(Qt.white)
                    painter.drawText(rx + 10, ry + 10, rect_text.width(),
                                     rect_text.height(), Qt.AlignLeft, texte)
            if config.get("watermark_enabled") and config.get("watermark_text"):
                texte_f = config.get("watermark_text")
                font = QFont("Segoe UI", max(16, virt_h // 40), QFont.Bold)
                painter.setFont(font)
                painter.setPen(QColor(255, 255, 255, 160))
                rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte_f)
                painter.drawText(virt_w - rect_text.width() - 20, virt_h - 20, texte_f)
            painter.end()
            return pix
        img_base = self.vue_comparateur.images_originales[0]
        w_orig, h_orig = img_base.width(), img_base.height()
        pix = QPixmap(w_orig, h_orig)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        orientation = config.get("orientation")
        is_vert = orientation == "Vertical"
        dim_max = w_orig if is_vert else h_orig
        curseurs_px = [int(dim_max * r) for r in self.vue_comparateur.ratios]
        for i in range(len(self.vue_comparateur.images_originales)):
            c_gauche = 0 if i == 0 else curseurs_px[i-1]
            c_droite = dim_max if i == len(self.vue_comparateur.images_originales)-1 else curseurs_px[i]
            if is_vert:
                rect = QRect(c_gauche, 0, c_droite - c_gauche, h_orig)
                painter.drawPixmap(rect, self.vue_comparateur.images_originales[i], rect)
            else:
                rect = QRect(0, c_gauche, w_orig, c_droite - c_gauche)
                painter.drawPixmap(rect, self.vue_comparateur.images_originales[i], rect)
        couleur = QColor(config.get("cursor_color"))
        epaisseur = config.get("cursor_thickness")
        stylo = QPen(couleur, epaisseur)
        painter.setPen(stylo)
        painter.setBrush(couleur)
        for c in curseurs_px:
            if is_vert:
                painter.drawLine(c, 0, c, h_orig)
                painter.drawEllipse(c - 5, h_orig//2 - 15, 10, 30)
            else:
                painter.drawLine(0, c, w_orig, c)
                painter.drawEllipse(w_orig//2 - 15, c - 5, 30, 10)
        if avec_labels:
            taille_label_base = config.get("label_size")
            opacite = config.get("label_bg_opacity")
            for i in range(len(self.vue_comparateur.infos_images)):
                c_gauche = 0 if i == 0 else curseurs_px[i-1]
                c_droite = dim_max if i == len(self.vue_comparateur.images_originales)-1 else curseurs_px[i]
                texte = self.vue_comparateur.infos_images[i]
                font = QFont("Segoe UI", taille_label_base, QFont.Bold)
                painter.setFont(font)
                rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte)
                if is_vert:
                    largeur_tranche = c_droite - c_gauche
                    if largeur_tranche > 40:
                        painter.save()
                        painter.setClipRect(QRect(c_gauche, 0, largeur_tranche, h_orig))
                        bg_rect = QRect(c_gauche + 5, 5, rect_text.width() + 10, rect_text.height() + 10)
                        painter.setPen(Qt.NoPen)
                        painter.setBrush(QColor(0, 0, 0, opacite))
                        painter.drawRoundedRect(bg_rect, 5, 5)
                        painter.setPen(Qt.white)
                        painter.drawText(c_gauche + 10, 10, rect_text.width(), rect_text.height(), Qt.AlignLeft, texte)
                        painter.restore()
                else:
                    hauteur_tranche = c_droite - c_gauche
                    if hauteur_tranche > 40:
                        painter.save()
                        painter.setClipRect(QRect(0, c_gauche, w_orig, hauteur_tranche))
                        bg_rect = QRect(5, c_gauche + 5, rect_text.width() + 10, rect_text.height() + 10)
                        painter.setPen(Qt.NoPen)
                        painter.setBrush(QColor(0, 0, 0, opacite))
                        painter.drawRoundedRect(bg_rect, 5, 5)
                        painter.setPen(Qt.white)
                        painter.drawText(10, c_gauche + 10, rect_text.width(), rect_text.height(), Qt.AlignLeft, texte)
                        painter.restore()
        if config.get("watermark_enabled") and config.get("watermark_text"):
            texte_f = config.get("watermark_text")
            font = QFont("Segoe UI", max(16, h_orig // 40), QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255, 160))
            rect_text = painter.fontMetrics().boundingRect(QRect(0,0,0,0), Qt.AlignLeft, texte_f)
            painter.drawText(w_orig - rect_text.width() - 20, h_orig - 20, texte_f)
        painter.end()
        return pix

    def copier_presse_papier(self):
        if not self.chemins_actuels: return
        pix = self.generer_pixmap_export(avec_labels=True, zoom_actif=self.vue_comparateur.total_zoom != 1.0)
        QApplication.clipboard().setPixmap(pix)
        QMessageBox.information(self, tr("info"), tr("copied"))

    def ouvrir_export(self):
        if not self.chemins_actuels: return
        est_zoome = abs(self.vue_comparateur.total_zoom - 1.0) > 0.01
        dlg = DialogueExport(self, est_zoome)
        if dlg.exec_():
            avec_labels, avec_zoom, ext = dlg.get_resultats()
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            dossier_courant = os.path.dirname(self.chemins_actuels[0])
            nom_fichier = f"Comparatif_{timestamp}{ext}"
            chemin_sav = os.path.join(dossier_courant, nom_fichier)
            compteur = 1
            while os.path.exists(chemin_sav):
                chemin_sav = os.path.join(dossier_courant, f"Comparatif_{timestamp}_{compteur}{ext}")
                compteur += 1
            if ext == ".gif":
                self.exporter_gif(chemin_sav, avec_labels, avec_zoom)
            else:
                pix = self.generer_pixmap_export(avec_labels, avec_zoom)
                if pix.isNull():
                    QMessageBox.critical(self, tr("error"), tr("err_gen", err="Export vide"))
                    return
                pix.save(chemin_sav, quality=95)
                QMessageBox.information(self, tr("success"), tr("exp_success", path=chemin_sav))

    def exporter_gif(self, chemin, avec_labels, avec_zoom):
        frames = []
        mem_ratios = list(self.vue_comparateur.ratios)
        try:
            for i in range(30):
                self.vue_comparateur.ratios = [i / 29.0] * len(self.vue_comparateur.ratios)
                pix = self.generer_pixmap_export(avec_labels, avec_zoom)
                buffer = QBuffer()
                buffer.open(QIODevice.ReadWrite)
                pix.save(buffer, "PNG")
                pil_img = Image.open(io.BytesIO(buffer.data()))
                frames.append(pil_img)
            frames[0].save(chemin, save_all=True, append_images=frames[1:], duration=60, loop=0)
            QMessageBox.information(self, tr("success"), tr("gif_success"))
        except Exception as e:
            QMessageBox.critical(self, tr("error"), tr("err_gif", err=str(e)))
        finally:
            self.vue_comparateur.ratios = mem_ratios

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        # Si l'onglet Compilation est actif, on laisse les cellules de
        # compilation gerer elles-memes le glisser-deposer.
        if HAS_COMPILATION and self.onglets.currentIndex() != 0:
            event.ignore()
            return
        urls = event.mimeData().urls()
        chemins = [u.toLocalFile() for u in urls
                   if u.toLocalFile().lower().endswith(
                       ('.png', '.jpg', '.jpeg', '.webp', '.bmp'))]
        if not chemins: return
        if self.stack.currentIndex() == 0 or event.pos().x() < self.panneau_gauche.width():
            if len(chemins) >= 2: 
                self.creer_nouveau_pack(chemins)
            else:
                QMessageBox.warning(self, tr("warning"), tr("warn_min_images"))
        else:
            self.chemins_actuels.extend(chemins)
            self.actualiser_pack_courant()

    def _statut_comparateur(self, message, succes=True, duree_ms=5000):
        couleur = "#46cd82" if succes else "#e0483a"
        self.barre_statut_comparateur.setStyleSheet(
            "QLabel { background-color:#161f2e; color:%s; "
            "border-top:1px solid #283750; padding:5px 12px; "
            "font-size:12px; font-weight:bold; }" % couleur)
        self.barre_statut_comparateur.setText(message)
        if duree_ms > 0:
            self._timer_statut_comparateur.start(duree_ms)

    def export_rapide_comparateur(self):
        if not self.chemins_actuels:
            return
        pix = self.generer_pixmap_export(avec_labels=True, zoom_actif=False)
        if pix.isNull():
            self._statut_comparateur(tr("err_gen", err="Export vide"), succes=False)
            return
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        dossier = os.path.dirname(self.chemins_actuels[0])
        chemin = os.path.join(dossier, "Comparatif_rapide_%s.jpg" % timestamp)
        compteur = 1
        while os.path.exists(chemin):
            chemin = os.path.join(
                dossier, "Comparatif_rapide_%s_%d.jpg" % (timestamp, compteur))
            compteur += 1
        if pix.save(chemin, "JPG", quality=95):
            self._statut_comparateur(tr("export_rapide_status", path=chemin),
                                     succes=True)
        else:
            self._statut_comparateur(tr("err_gen", err=chemin), succes=False)

    def naviguer_pack(self, delta):
        total = self.liste_packs_ui.count()
        if total < 2:
            return
        idx = self.liste_packs_ui.currentRow()
        self.liste_packs_ui.setCurrentRow((idx + delta) % total)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Tab and
                event.modifiers() == Qt.ControlModifier and
                self.onglets.count() > 1):
            self.onglets.setCurrentIndex(
                (self.onglets.currentIndex() + 1) % self.onglets.count())
            return
        # Si l'onglet Compilation est actif, on ne capture pas Ctrl+S /
        # Ctrl+C ni Suppr : le widget de compilation gere ses propres
        # raccourcis (export, vidage de case...).
        compil_actif = (HAS_COMPILATION and
                        self.onglets.currentIndex() != 0)
        if compil_actif:
            super().keyPressEvent(event)
            return
        if (event.key() in (Qt.Key_Tab, Qt.Key_Backtab) and
                self.liste_packs_ui.count() >= 2):
            if event.key() == Qt.Key_Backtab or event.modifiers() == Qt.ShiftModifier:
                self.naviguer_pack(-1)
            else:
                self.naviguer_pack(1)
            return
        if event.key() == Qt.Key_Delete:
            if self.liste_packs_ui.hasFocus():
                self.supprimer_pack_actuel()
            elif (self.barre_miniatures.hasFocus() or
                  self.barre_miniatures.selectedItems()):
                self.enlever_image_du_pack()
        elif event.key() == Qt.Key_F:
            if self.isFullScreen(): self.showNormal()
            else: self.showFullScreen()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.copier_presse_papier()
        elif (event.key() == Qt.Key_S and
              event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier)):
            self.export_rapide_comparateur()
        elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            self.ouvrir_export()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    
    args = sys.argv[1:]
    mode_export = "--export-rapide" in args or "--batch" in args
    chemins_finaux = []
    
    if not args:
        logiciel = LogicielComparateur()
        logiciel.show()
        sys.exit(app.exec_())
        
    elif any(os.path.isdir(a) for a in args):
        dossier = next(a for a in args if os.path.isdir(a))
        extensions = ('*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG')
        images = []
        for ext in extensions:
            images.extend(glob.glob(os.path.join(dossier, ext)))
        chemins_finaux = sorted(list(set(images)))
        
    else:
        fichiers_args = [f for f in args if os.path.isfile(f) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp'))]
        if len(fichiers_args) >= 2:
            # Cas simple : Windows a transmis plusieurs fichiers d'un coup.
            chemins_finaux = fichiers_args
        elif len(fichiers_args) == 1:
            # Cas du clic droit sur une SELECTION : Windows lance une
            # instance par image, chacune avec un seul fichier. On les
            # regroupe via un fichier-cache partage.
            #
            # Strategie fiabilisee :
            #  - La 1ere instance cree le cache : elle devient "collecteur"
            #    et attend un court instant que les autres s'inscrivent.
            #  - Les instances suivantes voient un cache recent : elles
            #    ajoutent leur ligne puis se terminent (sys.exit).
            #  - Le collecteur relit le cache complet et lance le logiciel.
            fichier_cache = os.path.join(tempfile.gettempdir(),
                                         "comparateur_pro_cache.txt")
            fichier_lock = fichier_cache + ".lock"
            suffixe = "--export-rapide" if mode_export else "--ouvrir"
            try:
                # Le cache est considere obsolete au-dela de 4 secondes.
                cache_recent = (os.path.exists(fichier_cache) and
                                time.time() - os.path.getmtime(fichier_cache) < 4.0)
                if not cache_recent:
                    # On purge un eventuel cache perime.
                    for f in (fichier_cache, fichier_lock):
                        try:
                            if os.path.exists(f):
                                os.remove(f)
                        except Exception:
                            pass

                # Tentative de devenir collecteur : creation exclusive du lock.
                est_collecteur = False
                if not cache_recent:
                    try:
                        fd = os.open(fichier_lock,
                                     os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                        os.close(fd)
                        est_collecteur = True
                    except FileExistsError:
                        est_collecteur = False
                    except Exception:
                        est_collecteur = False

                # Toutes les instances inscrivent leur image dans le cache.
                with open(fichier_cache, 'a', encoding='utf-8') as f:
                    f.write("%s\t%s\n" % (suffixe, fichiers_args[0]))

                if est_collecteur:
                    # Le collecteur laisse aux autres le temps de s'inscrire.
                    time.sleep(0.9)
                    try:
                        with open(fichier_cache, 'r', encoding='utf-8') as f:
                            brut = [l.strip() for l in f.read().split('\n')
                                    if l.strip()]
                    except Exception:
                        brut = []
                    # Nettoyage du cache et du lock.
                    for f in (fichier_cache, fichier_lock):
                        try:
                            if os.path.exists(f):
                                os.remove(f)
                        except Exception:
                            pass
                    # Extraction des chemins (on ignore le prefixe de mode).
                    chemins = []
                    for ligne in brut:
                        parts = ligne.split('\t', 1)
                        chemins.append(parts[1] if len(parts) == 2 else parts[0])
                    chemins_finaux = list(dict.fromkeys(chemins))
                else:
                    # Instance secondaire : sa contribution est enregistree,
                    # le collecteur s'occupe du reste. On se termine.
                    sys.exit(0)
            except SystemExit:
                raise
            except Exception:
                # En cas de souci, on ouvre au moins l'image transmise.
                chemins_finaux = fichiers_args

    logiciel = LogicielComparateur()
    if len(chemins_finaux) >= 2:
        if mode_export:
            logiciel.creer_nouveau_pack(chemins_finaux)
            pix = logiciel.generer_pixmap_export(avec_labels=True, zoom_actif=False)
            if pix.isNull():
                sys.exit(1)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            dossier = os.path.dirname(chemins_finaux[0])
            chemin_sav = os.path.join(dossier, f"Export_Rapide_{len(chemins_finaux)}_{timestamp}.jpg")
            pix.save(chemin_sav, quality=95)
            sys.exit(0)
        else:
            logiciel.creer_nouveau_pack(chemins_finaux)
            logiciel.show()
            sys.exit(app.exec_())
    else:
        logiciel.show()
        sys.exit(app.exec_())

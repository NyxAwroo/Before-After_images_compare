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
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QStackedWidget, QFrame, QMessageBox, QListWidget, 
                             QListWidgetItem, QAbstractItemView, QDialog, QSpinBox, 
                             QSlider, QColorDialog, QCheckBox, QComboBox, QLineEdit)
from PyQt5.QtGui import (QPainter, QPixmap, QPen, QFont, QColor, QCursor, QImage, QIcon)
from PyQt5.QtCore import Qt, QRect, QSize, QBuffer, QIODevice, pyqtSignal

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
        "restart_lang": "Please restart the application to apply the language change.",
        "img_word": "img",
        "warning": "Warning",
        "info": "Information",
        "success": "Success",
        "error": "Error"
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
        "restart_lang": "Veuillez redémarrer l'application pour appliquer le changement de langue.",
        "img_word": "img",
        "warning": "Attention",
        "info": "Info",
        "success": "Succès",
        "error": "Erreur"
    }
}

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
            "last_packs": [],
            "last_pack_index": 0
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
    lang = config.get("language")
    if lang not in LANGUAGES:
        lang = "en"
    text = LANGUAGES[lang].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

STYLE_SHEET = """
QMainWindow, QDialog { background-color: #1e1e1e; color: #ffffff; }
QLabel { color: #ffffff; }
QLabel#Titre { font-size: 24px; font-weight: bold; }
QLabel#SousTitre { color: #aaaaaa; font-size: 14px; }
QFrame#DropFrame { border: 3px dashed #555555; border-radius: 15px; background-color: #252526; }
QFrame#DropFrame[hover="true"] { border: 3px dashed #00a8ff; background-color: #2d2d30; }
QPushButton { background-color: #333333; color: white; border: 1px solid #555555; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
QPushButton:hover { background-color: #444444; border: 1px solid #888888; }
QPushButton#PrimaryButton { background-color: #007acc; border: none; }
QPushButton#PrimaryButton:hover { background-color: #0098ff; }
QPushButton#DangerButton { background-color: #8b0000; border: none; }
QPushButton#DangerButton:hover { background-color: #b30000; }
QFrame#Toolbar, QFrame#Sidebar { background-color: #252526; }
QFrame#Toolbar { border-bottom: 1px solid #333333; }
QFrame#Sidebar { border-right: 1px solid #333333; }
QListWidget { background-color: #252526; border: 1px solid #333333; border-radius: 5px; outline: 0; }
QListWidget::item { border: 2px solid transparent; border-radius: 5px; padding: 5px; }
QListWidget::item:selected { border: 2px solid #00a8ff; background-color: #333333; }
QSpinBox, QSlider, QComboBox, QLineEdit { background-color: #333333; color: white; border: 1px solid #555555; border-radius: 4px; padding: 4px; }
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
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def charger_images(self, chemins):
        self.images_originales = []
        self.infos_images = []
        for c in chemins:
            pixmap = QPixmap(c)
            self.images_originales.append(pixmap)
            taille_mo = os.path.getsize(c) / (1024 * 1024)
            nom = os.path.basename(c)
            info = f"{nom}\n{pixmap.width()} x {pixmap.height()} px\n{taille_mo:.1f} Mo"
            self.infos_images.append(info)
        self.reset_ratios()
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
        self.centrer_vue()
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

        if getattr(self, 'blink_mode', False):
            rect_dest = QRect(int(self.pan_x), int(self.pan_y), int(w_aff), int(h_aff))
            rect_source = QRect(0, 0, w_orig, h_orig)
            painter.drawPixmap(rect_dest, img_base, rect_source)
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

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return
        if event.button() == Qt.LeftButton and self.ratios:
            self.historique_ratios.append(list(self.ratios))
            if len(self.historique_ratios) > 20: self.historique_ratios.pop(0)
            is_vert = config.get("orientation") == "Vertical"
            pos_relative = (event.x() - self.pan_x) if is_vert else (event.y() - self.pan_y)
            dim_max = (self.images_originales[0].width() * self.total_zoom) if is_vert else (self.images_originales[0].height() * self.total_zoom)
            curseurs_px = [dim_max * r for r in self.ratios]
            distances = [abs(c - pos_relative) for c in curseurs_px]
            if distances:
                min_dist = min(distances)
                if min_dist < 30:
                    self.curseur_actif = distances.index(min_dist)
                    self.update_curseur(pos_relative, dim_max)

    def mouseMoveEvent(self, event):
        is_vert = config.get("orientation") == "Vertical"
        if self.panning and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()
            return
        if self.curseur_actif is not None:
            pos_relative = (event.x() - self.pan_x) if is_vert else (event.y() - self.pan_y)
            dim_max = (self.images_originales[0].width() * self.total_zoom) if is_vert else (self.images_originales[0].height() * self.total_zoom)
            self.update_curseur(pos_relative, dim_max)
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

class BarreMiniatures(QListWidget):
    reordonne = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
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

class DialogueParametres(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle(tr("settings_title"))
        self.resize(320, 280)
        layout = QVBoxLayout(self)

        h_lang = QHBoxLayout()
        h_lang.addWidget(QLabel(tr("language")))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Français", "English"])
        self.combo_lang.setCurrentText("Français" if config.get("language") == "fr" else "English")
        h_lang.addWidget(self.combo_lang)
        layout.addLayout(h_lang)
        layout.addSpacing(10)

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

        btn_box = QHBoxLayout()
        btn_ok = QPushButton(tr("close"))
        btn_ok.setObjectName("PrimaryButton")
        btn_ok.clicked.connect(self.accept)
        btn_box.addStretch()
        btn_box.addWidget(btn_ok)
        layout.addSpacing(20)
        layout.addLayout(btn_box)

        self.spin_ep.valueChanged.connect(self.sauvegarder_live)
        self.spin_taille.valueChanged.connect(self.sauvegarder_live)
        self.slider_op.valueChanged.connect(self.sauvegarder_live)
        self.cb_watermark.stateChanged.connect(self.sauvegarder_live)
        self.edit_wm.textChanged.connect(self.sauvegarder_live)
        self.combo_lang.currentTextChanged.connect(self.changer_langue)

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
        if self.main_window: self.main_window.vue_comparateur.update()

    def changer_langue(self, text):
        new_lang = "fr" if text == "Français" else "en"
        if new_lang != config.get("language"):
            config.set("language", new_lang)
            QMessageBox.information(self, "Information", tr("restart_lang"))

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
        toolbar.setStyleSheet("background-color: #252526; border-bottom: 1px solid #333333;")
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
        self.lbl_img.setStyleSheet("background-color: #1e1e1e;")
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
        
        btn_supprimer_pack = QPushButton(tr("del_pack"))
        btn_supprimer_pack.clicked.connect(self.supprimer_pack_actuel)

        btn_vider_liste = QPushButton(tr("clear_list"))
        btn_vider_liste.setObjectName("DangerButton")
        btn_vider_liste.clicked.connect(self.vider_liste_packs)
        
        layout_gauche.addWidget(lbl_packs)
        layout_gauche.addWidget(self.liste_packs_ui)
        layout_gauche.addWidget(btn_nouveau)
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

        self.btn_reset_align = QPushButton(tr("originals"))
        self.btn_reset_align.clicked.connect(self.annuler_alignement)
        self.btn_reset_align.hide()

        btn_align = QPushButton(tr("auto_align"))
        btn_align.clicked.connect(self.aligner_images)

        btn_heatmap = QPushButton(tr("heatmap_btn"))
        btn_heatmap.clicked.connect(self.generer_heatmap)

        btn_copy = QPushButton(tr("copy"))
        btn_copy.clicked.connect(self.copier_presse_papier)

        btn_param = QPushButton(tr("settings"))
        btn_param.clicked.connect(self.ouvrir_parametres)

        btn_exp = QPushButton(tr("export"))
        btn_exp.setObjectName("PrimaryButton")
        btn_exp.clicked.connect(self.ouvrir_export)
        
        layout_tb.addWidget(self.btn_ori)
        layout_tb.addWidget(btn_centrer)
        layout_tb.addStretch()
        layout_tb.addWidget(self.btn_reset_align)
        layout_tb.addWidget(btn_align)
        layout_tb.addWidget(btn_heatmap)
        layout_tb.addWidget(btn_copy)
        layout_tb.addWidget(btn_param)
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
        
        layout_global.addWidget(self.panneau_gauche)
        layout_global.addWidget(zone_droite, 1)
        
        self.setCentralWidget(widget_central)
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

    def charger_pack_depuis_liste(self, index):
        if index < 0 or index >= len(self.packs):
            self.stack.setCurrentIndex(0)
            self.toolbar.hide()
            self.zone_miniatures_globale.hide()
            return
        pack = self.packs[index]
        self.chemins_actuels = pack["chemins"]
        if pack.get("chemins_originaux"):
            self.btn_reset_align.show()
        else:
            self.btn_reset_align.hide()
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
        fichiers, _ = QFileDialog.getOpenFileNames(self, "Selection", dossier_courant, "Images (*.png *.jpg *.jpeg)")
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
        self.chemins_actuels = nouveaux_chemins
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
        self.vue_comparateur.centrer_vue()

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
        est_zoome = self.vue_comparateur.total_zoom != 1.0 and abs(self.vue_comparateur.pan_x) > 1
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
        urls = event.mimeData().urls()
        chemins = [u.toLocalFile() for u in urls if u.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not chemins: return
        if self.stack.currentIndex() == 0 or event.pos().x() < self.panneau_gauche.width():
            if len(chemins) >= 2: 
                self.creer_nouveau_pack(chemins)
            else:
                QMessageBox.warning(self, tr("warning"), tr("warn_min_images"))
        else:
            self.chemins_actuels.extend(chemins)
            self.actualiser_pack_courant()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if self.liste_packs_ui.hasFocus():
                self.supprimer_pack_actuel()
            elif self.barre_miniatures.hasFocus():
                self.enlever_image_du_pack()
        elif event.key() == Qt.Key_F:
            if self.isFullScreen(): self.showNormal()
            else: self.showFullScreen()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.copier_presse_papier()
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
        fichiers_args = [f for f in args if os.path.isfile(f) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if len(fichiers_args) >= 2:
            chemins_finaux = fichiers_args
        elif len(fichiers_args) == 1:
            fichier_cache = os.path.join(tempfile.gettempdir(), "comparateur_pro_cache.txt")
            try:
                if os.path.exists(fichier_cache):
                    try:
                        if time.time() - os.path.getmtime(fichier_cache) > 2.0:
                            os.remove(fichier_cache)
                    except: pass
                with open(fichier_cache, 'a', encoding='utf-8') as f:
                    f.write(fichiers_args[0] + '\n')
                time.sleep(0.5)
                with open(fichier_cache, 'r', encoding='utf-8') as f:
                    lignes = [l.strip() for l in f.read().split('\n') if l.strip()]
                if lignes and lignes[-1] == fichiers_args[0]:
                    try: os.remove(fichier_cache)
                    except: pass
                    chemins_finaux = list(dict.fromkeys(lignes))
                else:
                    sys.exit(0)
            except Exception as e:
                chemins_finaux = fichiers_args

    logiciel = LogicielComparateur()
    if len(chemins_finaux) >= 2:
        if mode_export:
            logiciel.creer_nouveau_pack(chemins_finaux)
            pix = logiciel.generer_pixmap_export(avec_labels=True, zoom_actif=False)
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
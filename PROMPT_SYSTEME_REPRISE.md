# Prompt système — Reprise du projet « Comparateur Pro »

> **Comment utiliser ce fichier :** au début d'une nouvelle conversation,
> copiez-collez l'intégralité de ce document, puis joignez les fichiers
> indiqués dans la section « Fichiers à importer ». Cela permet de reprendre
> le développement exactement là où il s'est arrêté.

---

## Fichiers à importer dans la nouvelle conversation

À joindre **obligatoirement** (les fichiers de code en cours) :
- `comparateur_app.py` — application principale
- `compilation_module.py` — module de l'outil de compilation
- `compilation_templates.json` — *seulement s'il existe* ; contient vos
  gabarits et noms favoris personnels. Facultatif mais utile pour tester.

À joindre **si la modification les concerne** :
- `comparateur_config.json` — réglages UI persistants
- `langues/fr.json`, `langues/en.json` — fichiers de traduction (à joindre
  pour toute modification touchant aux textes ou à l'internationalisation)
- `Menu_Comparateur_FR.reg` / `Menu_Comparateur_EN.reg` — intégration clic droit
- `install_raccourcis.bat` — installateur des raccourcis Windows
- `README.md`, `CHANGELOG.md` — pour toute mise à jour de documentation

Le plus simple : zipper tout le dossier du projet et le joindre.

---

## Identité du projet

**Comparateur Pro** est un logiciel de comparaison d'images professionnel
pour Windows, écrit en **Python 3** avec **PyQt5**, **OpenCV** et **Pillow**.
Localisation de référence du projet sur la machine de l'auteur :
`D:\Documents\Python Scripts\comparaison image AVANT-APRES\`.

Le projet est publié en open source sur GitHub (compte `NyxAwroo`,
dépôt `Before-After_images_compare`).

---

## Architecture des fichiers

| Fichier | Rôle |
|---|---|
| `comparateur_app.py` | Application principale : fenêtre, onglets, comparateur, heatmap, export, réglages, i18n. C'est le point d'entrée (`python comparateur_app.py`). |
| `compilation_module.py` | Module additionnel de l'outil de compilation. Importé de façon optionnelle par l'app principale. |
| `comparateur_config.json` | Réglages UI persistants (langue, couleurs curseur, etc.). |
| `compilation_templates.json` | Gabarits de grille et noms favoris de l'utilisateur (généré à l'usage). |
| `Menu_Comparateur_FR.reg` / `_EN.reg` | Clés de registre pour le menu clic droit Windows. |
| `install_raccourcis.bat` | Installe les raccourcis en détectant automatiquement le chemin. |

### Comment les deux modules communiquent

`comparateur_app.py` importe `compilation_module` dans un bloc `try/except` :
si le fichier est absent, `HAS_COMPILATION` passe à `False` et le logiciel
fonctionne sans l'onglet Compilation (fail-safe).

Au démarrage, l'app appelle `compilation_module.init_compilation(config, tr,
LANGUAGES)` pour injecter dans le module : l'objet de config, la fonction de
traduction `tr`, et le dictionnaire `LANGUAGES`. Le module fusionne alors ses
propres traductions (clés préfixées `comp_`) dans `LANGUAGES`.

L'onglet Compilation est créé via `compilation_module.creer_widget_compilation()`
qui retourne un `WidgetCompilation` (hérite de `QWidget`).

---

## Classes principales

### Dans `comparateur_app.py`
- `ConfigManager` — lecture/écriture de `comparateur_config.json`.
- `ComparateurWidget` — moteur de rendu de la comparaison (curseurs, zoom/pan).
- `BarreMiniatures` — bande de miniatures.
- `DialogueRaccourcis` — fenêtre récapitulative des raccourcis clavier.
- `DialogueParametres` — fenêtre de réglages (langue, import/export de langue,
  accès aux raccourcis).
- `DialogueExport` — dialogue d'export du comparateur.
- `FenetreHeatmap` — fenêtre indépendante de carte thermique.
- `LogicielComparateur` — fenêtre principale (`QMainWindow`), gère les onglets.

### Dans `compilation_module.py`
- `CelluleImage` — une case de la grille. Gère le drop de fichier, le glisser
  d'ajustement, le Ctrl+glisser d'interversion, la sélection, le zoom molette,
  et dessine **elle-même son étiquette** (visible en aperçu).
- `GrilleCompilation` — conteneur de la grille : placement des cases, fond,
  séparateur facultatif entre les cases.
- `DialogueLabelCase` — popup de choix du texte d'étiquette d'une case
  (auto / favori / manuel / aucune).
- `WidgetCompilation` — panneau complet de l'outil (réglages à gauche dans une
  zone défilante, aperçu à droite).
- Fonctions de rendu partagées : `peindre_image_dans_rect`, `dessiner_label`,
  `generer_pixmap_compilation` (moteur d'export 1:1).

---

## État actuel — Version 3.0.0 (terminée)

Tout ce qui suit est **implémenté et validé** :

**Comparateur** (depuis la V1, inchangé) : comparaison multi-images, curseurs,
zoom/pan synchronisé, mode Blink, sticky labels, snapping, auto-alignement 2D,
multi-heatmap, export 1:1, intégration clic droit Windows, i18n FR/EN.

**Compilation** (V2) : gabarits intégrés + éditeur, glisser-déposer par case,
formats de sortie (presets + libre + inversion L/H + verrou ratio), ajustement
des images (glisser + molette), interversion Ctrl+glisser, sélection + Suppr,
nouvelle planche vierge, orientation verticale/horizontale, séparateur
facultatif (couleur + épaisseur), étiquettes par case éditables au clic et
visibles en aperçu, export automatique horodaté.

**Réglages** (V2) : onglets Comparateur/Compilation, bouton ⚙ permanent dans le
coin de la barre d'onglets, fenêtre de réglages, récap des raccourcis, système
de traduction communautaire (export/import de fichiers de langue).

**Nouveautés V3** :
- Refonte du thème (« Midnight Blue ») : fonds bleu nuit, accents orange. Les
  couleurs du module compilation sont centralisées dans des constantes
  `COL_*` en haut de `compilation_module.py`.
- Annuler/Rétablir dans la compilation (Ctrl+Z / Ctrl+Y), historique de 50
  états. Méthodes : `_enregistrer_historique`, `_annuler`, `_retablir`,
  `_restaurer_historique`. Le signal `CelluleImage.ajustement_termine` crée un
  point d'annulation en fin de recadrage/zoom.
- Projets de compilation `.comproj` : `_sauver_projet`, `_ouvrir_projet`,
  `_etat_projet`, `_appliquer_projet`.
- Dossier `langues/` avec `fr.json`, `en.json` et un guide traducteur. Chargé
  au démarrage par `charger_langues_externes()`.

**Suggestions non encore traitées** (voir `SUGGESTIONS.md`) : cellules de
tailles inégales (3), bordure par image (4), filigrane global (7), rotation
d'image (8), reset recadrage (9), presets format perso (10), modes du
comparateur (11-15), batch de compilations (17), fichiers récents (18), drag
depuis le web (19), raccourcis personnalisables (21), profils de réglages
(23), mise à jour intégrée (24).

---

## Conventions et contraintes à respecter

- **Thème sombre Premium** : conserver l'esthétique sombre (`#1e1e1e`, accents
  bleus `#00a8ff` / `#007acc`).
- **Pas de dépendances lourdes** hors PyQt5, OpenCV, Pillow, NumPy.
- **Fichiers `.reg`** : toujours échapper les guillemets internes (`\"`) et
  doubler les antislashs des chemins (`\\`).
- **Fail-safe** : le correctif `pyw` (bypass de `stdout`/`stderr` via
  `io.StringIO()`) et l'intercepteur de crash (`sys.excepthook`) doivent rester.
- **Gestion de session** : les réglages persistent, mais la liste des packs est
  vidée à la fermeture (`closeEvent`).
- **i18n** : tout texte visible passe par `tr(...)`. Les nouvelles clés du
  module compilation sont préfixées `comp_`.
- **Module compilation** : ne jamais casser l'import optionnel ni le contrat
  `init_compilation` / `creer_widget_compilation`.
- **Style sombre des sous-widgets** : utiliser des `QFrame` (pas des `QWidget`
  nus) quand on veut hériter du style `QFrame#Sidebar`, sinon le fond reste
  clair.

---

## Limite connue de l'environnement de développement assisté

L'assistant qui développe ce projet n'a pas PyQt5 installé : il ne peut pas
lancer l'interface graphique réelle. Il valide la syntaxe, le chargement des
modules (avec un PyQt5 simulé) et la logique métier. **Un test sur la machine
Windows de l'auteur reste donc nécessaire après chaque modification.**

---

## Pour la prochaine session

Indiquez simplement ce que vous voulez ajouter ou corriger. Si vous avez une
liste de fonctionnalités envisagées, le fichier `SUGGESTIONS.md` (livré avec
la V2) en contient une vingtaine, prêtes à être priorisées.

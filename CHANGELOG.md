# Changelog — Comparateur Pro

Toutes les évolutions notables du projet sont consignées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/).

---

## [3.3.0] — 2026-06-08

Version de stabilisation et d'ergonomie : correction des bugs relevés dans la
roadmap 3.2.0, renforcement du module Compilation et ajout de raccourcis /
outils de productivité.

### Corrigé

**Comparateur**
- Les comparaisons récentes affichent désormais le bon avertissement si une
  partie seulement des images est introuvable, et distinguent clairement le
  cas où il ne reste plus assez d'images valides.
- Le chargement d'images filtre les pixmaps illisibles au lieu de les conserver
  dans la session, évitant des exports vides ou des erreurs de rendu.
- L'export rapide en ligne de commande (`--export-rapide`) ne plante plus si
  certaines images transmises sont illisibles ou non prises en charge.
- Le mode Différence revient proprement au mode curseur avec message de statut
  si le calcul de différence échoue.
- Le curseur visuel du mode « curseur en direct » ne reste plus bloqué en mode
  Split pendant un déplacement au clic droit.
- La loupe en mode Côte à côte affiche l'image la plus proche lorsque le
  curseur se trouve dans l'espace entre deux images.
- L'export respecte maintenant le mode affiché : Côte à côte et Différence ont
  chacun un rendu dédié au lieu de produire systématiquement un export à
  curseurs.
- Le test d'export de zone zoomée se base désormais uniquement sur le zoom réel.
- La touche Suppr fonctionne plus naturellement avec la barre de miniatures
  grâce à une meilleure gestion du focus et de la sélection.
- Les chemins invalides issus d'un réordonnancement de miniatures sont filtrés
  avant de recharger le pack.
- Les erreurs de chargement de fichiers de langue externes sont journalisées
  dans `comparateur_crash.log` au lieu d'être ignorées silencieusement.

**Compilation**
- Les restaurations d'historique/projet bloquent les signaux intermédiaires :
  les offsets, zooms, rotations et étiquettes sont restaurés avant tout
  enregistrement d'historique.
- Les timers de zoom des cellules sont stoppés avant reconstruction de grille,
  évitant les erreurs PyQt sur objets supprimés lors de Ctrl+Z rapides.
- Les projets et états d'historique signalent dans la barre de statut les
  images devenues introuvables au lieu de vider les cases silencieusement.
- Les gabarits créés avec `+ Nouveau gabarit` enregistrent maintenant tous les
  réglages du volet, comme `Sauver la grille actuelle`.
- Le changement de position d'étiquette pendant une restauration bloque ses
  signaux, évitant les rafraîchissements intermédiaires incohérents.
- Le verrouillage du ratio de sortie utilise un ratio mémorisé cohérent, même
  pendant la modification directe des dimensions.
- Le premier pack de compilation peut récupérer automatiquement les images déjà
  présentes dans la grille.
- Le pack courant est sauvegardé à la fermeture ; si des packs de compilation
  existent encore, une confirmation évite une perte silencieuse.
- Un fichier `compilation_templates.json` corrompu est sauvegardé en `.bak` et
  signalé à l'utilisateur.
- Le repli de différence sans OpenCV utilise Pillow de façon vectorisée, ou
  affiche un message au lieu de bloquer l'interface avec une boucle pixel par
  pixel.
- La superposition de filigrane se resynchronise aussi sur suppression de
  widgets enfants.
- La clé française `sc_comp_export` manquante a été ajoutée.

### Ajouté

**Comparateur**
- Support `.webp` et `.bmp` dans le glisser-déposer principal et dans
  l'ajout d'images à un pack.
- Barre de statut en bas du comparateur pour les actions non bloquantes.
- Export JPEG 1:1 rapide via `Ctrl+Shift+S`, sans dialogue, avec confirmation
  dans la barre de statut.
- Overlay discret du nom du pack en haut à droite de la vue image, activable
  ou désactivable dans les Paramètres.
- Navigation entre packs avec `Tab` / `Shift+Tab`.
- Bascule entre onglets avec `Ctrl+Tab`.
- Le récapitulatif des raccourcis inclut les nouveaux raccourcis du comparateur
  et de la compilation.

**Compilation**
- Mode d'import par glisser-déposer dans le volet Packs :
  `Par gabarit` regroupe les images selon la grille courante, tandis que
  `Planche unique` crée un seul pack et redimensionne la grille pour accueillir
  les images déposées.
- Le mode d'import des packs est persistant via `compilation_import_mode`.
- Glisser-déposer d'un lot d'images directement sur le volet ou la liste des
  packs, avec création automatique des packs et message de statut.
- Menu contextuel par clic droit sur un pack : renommer, dupliquer, vider les
  images ou supprimer.
- Navigation entre cases de la grille avec `Tab` / `Shift+Tab`.
- Filtre textuel des gabarits, sans casser la correspondance avec les gabarits
  internes.
- Les réglages du volet Compilation (format, séparateur, bordure, labels,
  filigrane, etc.) sont sauvegardés à la fermeture et restaurés au démarrage.

### Modifié

- `+ Nouveau gabarit` utilise maintenant une seule fenêtre de saisie
  (nom + lignes + colonnes), avec valeurs actuelles en défaut.
- `Sauver la grille actuelle` et `+ Nouveau gabarit` partagent le même moteur
  de sauvegarde de gabarit complet.
- La zone cliquable des étiquettes de cellule suit désormais la position réelle
  du badge affiché, au lieu de rester en bas de la case.

---

## [3.2.0] — 2026-05-18

### Corrigé

- **Menu clic droit Windows réparé** : le menu pointait vers un chemin
  obsolète lorsque le dossier du projet était déplacé ou renommé, ce qui
  empêchait tout lancement (« Ouvrir » et « Export Rapide » sans effet).
  Les fichiers `.reg` figés ont été retirés du dépôt : seul
  `install_raccourcis.bat`, qui détecte automatiquement le chemin réel,
  doit désormais être utilisé.

### Ajouté

- **Historique des comparaisons récentes** (suggestion 18) : un bouton
  « 🕘 Récents » dans le panneau gauche ouvre la liste des dernières
  comparaisons ouvertes (10 max, avec vignette et date). Double-clic pour
  recharger. L'historique persiste entre les sessions ; les images
  disparues du disque sont ignorées avec un avertissement.
- **Désinstallateur** : `desinstaller_raccourcis.bat` retire proprement le
  menu clic droit.
- **Installateur fiabilisé** : `install_raccourcis.bat` vérifie désormais
  la présence de `comparateur_app.py` et de la commande `pyw` avant
  d'écrire dans le registre, et prévient l'utilisateur en cas de problème.
- **Traitement par lot de compilations** (suggestion 17) : un volet
  « Packs de compilation » dans l'onglet Compilation permet de préparer
  plusieurs planches partageant le même gabarit et les mêmes réglages.
  On crée des packs un par un (bouton « + Pack »), on sélectionne un pack
  pour l'éditer dans la grille centrale (glisser-déposer et interversion
  des images entre cases, comme une planche normale), et le bouton
  « Générer toutes les planches » exporte chaque pack en une planche PNG.
  Chaque pack conserve l'ajustement complet de ses cases (cadrage, zoom,
  rotation, étiquettes) quand on passe de l'un à l'autre.

---

## [3.1.1] — 2026-05-17

Version corrective : résolution de régressions de la 3.1.0 et améliorations
d'ergonomie demandées.

### Corrigé

- **Curseur de comparaison de nouveau déplaçable** : une régression de la
  3.1.0 avait supprimé la gestion du clic gauche dans le comparateur. Le
  curseur se déplace à nouveau (tolérance de saisie élargie à 40 px).
- **Loupe ne fait plus planter le logiciel** : la loupe ne capture plus le
  widget (`grab()` pendant un rendu était instable) ; elle redessine
  directement la portion grossie à partir des images sources.
- **Sélection multiple via le clic droit Windows** : la logique de
  regroupement des images (une instance lancée par image) a été fiabilisée
  par un système de verrou ; la sélection complète est désormais bien
  importée dans le comparateur.

### Ajouté

**Comparateur**
- Option **« curseur en direct au survol »** dans les Paramètres : le curseur
  suit la souris sans qu'il faille cliquer (le mode clic-maintenu reste
  disponible).
- Niveau de **zoom de la loupe** réglable dans les Paramètres.

**Compilation**
- Les **gabarits de grille** enregistrent désormais l'intégralité des réglages
  du volet (disposition, format de sortie, séparateur, bordure, filigrane,
  étiquettes), et pas seulement le nombre de cases.
- **Gestion des presets de format de sortie** : ajout, modification et
  suppression de presets personnalisés (enregistrés dans
  `compilation_templates.json` ; les presets fournis restent protégés).
- **Export rapide par `Ctrl+S`** dans l'onglet Compilation, sans fenêtre de
  confirmation.
- **Pied de page de statut** (façon Photoshop) : les messages d'export
  réussi/échoué s'affichent en bas de l'interface au lieu d'une fenêtre
  bloquante.

---

## [3.1.0] — 2026-05-17

Version axée sur les outils d'analyse du comparateur et l'enrichissement des
compilations.

### Ajouté

**Comparateur — nouveaux modes d'affichage**
- Mode **Côte à côte** : les images sont alignées les unes à côté des autres
  (sans curseur), avec zoom et déplacement synchronisés.
- Mode **Différence de pixels** : affiche directement l'image de soustraction
  entre la référence et la 2ᵉ image (utile pour le contrôle qualité).
- Sélecteur de mode dans la barre d'outils (Curseur / Côte à côte / Différence).

**Comparateur — loupe et mesures**
- **Loupe** : une fenêtre grossissante circulaire suit le curseur pour
  inspecter un détail sans zoomer toute la vue (bouton-bascule).
- **Score de similarité** : calcul SSIM, PSNR et pourcentage de pixels
  différents entre la référence et chaque autre image, présenté dans un
  récapitulatif.

**Compilation — enrichissement des planches**
- **Bordure par image** : liseré optionnel (couleur + épaisseur) autour de
  chaque image, distinct du séparateur entre cases.
- **Filigrane global** : texte de filigrane appliqué à toute la compilation
  (texte, position, taille, opacité), visible en direct dans l'aperçu.
- **Rotation d'une image dans sa case** : 90° gauche/droite ou 180° via le
  menu clic droit d'une case.
- **Réinitialiser le cadrage de toutes les cases** : recentre et dézoome
  toutes les images de la planche en un clic.

### Modifié
- Les projets `.comproj` enregistrent désormais la rotation des cases, la
  bordure par image et le filigrane (format porté en version 4 ; les anciens
  projets restent lisibles).


projets de compilation, annuler/rétablir et internationalisation facilitée.

### Ajouté

**Annuler / Rétablir dans la compilation**
- Historique des actions de la planche (ajout d'image, vidage, interversion,
  recadrage, zoom de case, changement d'étiquette).
- Raccourcis Ctrl+Z (annuler) et Ctrl+Y (rétablir), jusqu'à 50 états mémorisés.
- Les enchaînements de molette sont regroupés en un seul point d'annulation.

**Projets de compilation**
- Sauvegarde d'une planche complète dans un fichier `.comproj` (grille, format
  de sortie, séparateur, étiquettes, contenu et recadrage de chaque case).
- Réouverture d'un projet pour reprendre un montage en cours.

**Internationalisation facilitée**
- Dossier `langues/` livré avec les fichiers `fr.json` et `en.json`.
- Guide `LISEZ-MOI_README.txt` expliquant comment créer une traduction.
- Les imports/exports de fichiers de langue pointent désormais vers ce dossier.

### Modifié
- **Refonte complète du thème** : nouvelle identité visuelle « Midnight Blue »,
  fonds bleu nuit et boutons orange, pour un rendu plus moderne et premium
  (remplace l'ancien thème gris / cyan). Sliders, cases à cocher, menus,
  barres de défilement et onglets sont restylés.
- Le récapitulatif des raccourcis clavier inclut Ctrl+Z / Ctrl+Y.

---

## [2.0.0] — 2026-05-17

Version majeure : ajout d'un outil complet de **compilation d'images** et
d'un système de **réglages** repensé.

### Ajouté

**Outil de compilation d'images (nouvel onglet 🧩)**
- Création de compilations / grilles d'images (couvertures CivitAI, planches
  comparatives, etc.) sans passer par un logiciel externe.
- Gabarits de grille : 7 dispositions intégrées (2, 3, 4, 6, 9 cases) plus un
  éditeur pour créer, sauver et supprimer ses propres gabarits. Les gabarits
  personnels et les noms favoris sont stockés dans `compilation_templates.json`.
- Importation des images par glisser-déposer directement dans une case précise.
- Format de sortie paramétrable : 9 presets prêts (dont *CivitAI couverture
  1600×900* et *CivitAI large 1920×1080*) ou pixels libres, avec verrouillage
  de ratio et bouton d'inversion largeur ↔ hauteur.
- Ajustement de l'image dans sa case : repositionnement par glisser simple,
  zoom par molette.
- Interversion du contenu de deux cases par Ctrl + glisser.
- Sélection d'une case par clic, vidage par la touche Suppr.
- Bouton « Nouvelle planche vierge » pour repartir de zéro.
- Disposition verticale ou horizontale (échange lignes ↔ colonnes).
- Séparateur facultatif entre les cases : couleur et épaisseur réglables, sans
  bordure systématique autour des images.
- Étiquette texte par case : un clic sur l'étiquette ouvre une fenêtre de choix
  du texte (automatique d'après le nom de fichier / liste de noms favoris /
  saisie manuelle / aucune). Le rendu des étiquettes est visible en direct dans
  l'aperçu.
- Export 1:1 propre via QPainter : sauvegarde automatique dans le dossier de la
  première image importée, nom horodaté, anti-collision. Copie presse-papier
  également disponible.

**Interface**
- Système d'onglets en haut de la fenêtre principale : « 🔍 Comparateur » et
  « 🧩 Compilation ».
- Bouton de réglages « ⚙ Paramètres » placé dans le coin de la barre d'onglets,
  donc toujours accessible quel que soit l'onglet actif.

**Réglages et internationalisation**
- Fenêtre de réglages : choix de la langue et accès au récapitulatif des
  raccourcis clavier.
- Fenêtre dédiée listant tous les raccourcis clavier (utile aux nouveaux
  utilisateurs découvrant le logiciel).
- Système de traduction communautaire : export d'un fichier de langue modèle,
  édition libre des textes, puis réimport dans le logiciel.

### Modifié
- Le glisser-déposer de la fenêtre principale est neutralisé lorsque l'onglet
  Compilation est actif (les cases gèrent leur propre dépôt).

### Notes techniques
- Le module de compilation vit dans un fichier séparé `compilation_module.py`,
  importé de façon optionnelle : si le fichier est absent, le logiciel
  fonctionne normalement sans l'onglet Compilation (fail-safe).
- Aucune dépendance nouvelle introduite : toujours PyQt5, OpenCV, Pillow, NumPy.

---

## [1.0.0] — 2026-05-06

Première version publique du comparateur d'images.

### Ajouté
- Comparaison multi-images avec curseurs mobiles et zoom/pan synchronisé.
- Mode Blink (touche Espace) pour alterner référence / vue actuelle.
- Sticky labels : informations épinglées aux bords, redimensionnées
  dynamiquement.
- Snapping des curseurs à 25 %, 50 % et 75 %.
- Auto-alignement 2D (algorithme affine partiel) pour caler des images
  décalées.
- Multi-heatmap : carte thermique cumulative dans une fenêtre indépendante.
- Exportation 1:1 (JPEG, PNG, GIF animé) avec labels et filigrane.
- Intégration Windows : fichiers `.reg` FR/EN pour le lancement via clic droit.
- Support multilingue interne français / anglais avec détection automatique de
  la langue système.
- Stabilité : correctif `pyw` (bypass stdout/stderr), intercepteur de crash via
  `sys.excepthook`.

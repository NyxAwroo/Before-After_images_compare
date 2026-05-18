# Outil de Compilation d'images — Note technique

## Fichiers

| Fichier | Statut | Action |
|---|---|---|
| `compilation_module.py` | **NOUVEAU** | À placer dans le même dossier que `comparateur_app.py` |
| `comparateur_app.py` | **MODIFIÉ** | Remplace l'ancien |
| `.gitignore` | **MODIFIÉ** | Ajoute `compilation_templates.json` |

Tout le reste (fonctions du comparateur, .reg, config) est inchangé.

## Accès à l'outil — système d'onglets

Pour un accès intuitif / ergonomique / instinctif, la compilation est un
**onglet** en haut de la fenêtre principale :

    [ 🔍 Comparateur ]   [ 🧩 Compilation ]

On bascule d'un clic, dans la même fenêtre — pas de fenêtre flottante à gérer.
L'onglet Comparateur contient tout votre outil existant, intact. L'onglet
Compilation n'apparaît que si `compilation_module.py` est présent (sinon le
logiciel tourne normalement sans cet onglet — fail-safe).

Le style des onglets suit le thème sombre Premium (bleu #00a8ff sur l'actif).

## Architecture

Le code de compilation vit dans un module séparé. Le widget de compilation
hérite de `QWidget` (`WidgetCompilation`), ce qui permet de l'insérer comme
onglet. Une fonction `ouvrir_fenetre_compilation()` reste disponible si vous
vouliez un jour un mode fenêtre indépendante.

Intégration dans `comparateur_app.py` :
1. Import + `init_compilation(...)` après la création de `config`.
2. `QTabWidget` enveloppant l'interface ; onglet 2 = compilation.
3. `dropEvent` principal neutralisé quand l'onglet Compilation est actif
   (les cellules de compilation gèrent leur propre glisser-déposer).

## Fonctionnalités

- **Gabarits** : 7 gabarits intégrés (2/3/4/6/9 cases) + éditeur pour créer,
  sauver et supprimer ses propres dispositions
  (`+ Nouveau gabarit` / `Sauver la grille actuelle`). Stockés dans
  `compilation_templates.json`.
- **Glisser-déposer direct dans une case** précise.
- **Format de sortie** : 9 presets (dont *CivitAI couverture 1600x900* et
  *CivitAI large 1920x1080*) — pas de calcul de ratio à faire. Mode *Libre*
  pour pixels exacts, avec *Verrouiller le ratio*.
- **Ajustement image dans la case** : repositionnement par glisser, molette
  pour zoomer dans la case.
- **Disposition** verticale / horizontale (échange lignes ↔ colonnes).
- **Sticker label** : fond + opacité réglables, 6 positions ; texte en mode
  Auto (nom fichier) / Favoris (liste modifiable) / Manuel / Global ;
  applicable à toutes les cases ou à la première.
- **Export** : sauvegarde **automatique** dans le dossier de la 1ère image
  importée, nom horodaté `Compilation_AAAAMMJJ_HHMMSS.png`, avec
  anti-collision — exactement le comportement de l'export du comparateur.
  Copie presse-papier également disponible.
- **Apparence** : espacement, marge extérieure et couleur de fond réglables.

## Multilingue

Textes FR / EN fusionnés dans le dictionnaire `LANGUAGES` (clés `comp_`,
plus `tab_comparateur` / `tab_compilation`).

## Dépendances

Aucune dépendance nouvelle (PyQt5 uniquement).

## Limite de validation

PyQt5 n'étant pas disponible dans mon environnement, je n'ai pas pu lancer
l'interface graphique réelle. Validé : syntaxe, chargement complet des deux
modules (PyQt5 simulé), intégration des onglets, persistance JSON, et
l'algorithme de rendu (reproduit avec Pillow → image de sortie correcte).
Un test sur votre machine Windows reste recommandé.

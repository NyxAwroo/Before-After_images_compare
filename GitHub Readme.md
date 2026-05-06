# **Comparateur Pro 📸**

**Comparateur Pro** est un outil de comparaison d'images léger, rapide et professionnel conçu pour Windows. Il permet de comparer plusieurs images simultanément avec une synchronisation parfaite du zoom et du déplacement.

## **✨ Fonctionnalités**

* **Comparaison Multi-images :** Gérez des tranches d'images fluides avec des curseurs mobiles.  
* **Synchronisation Totale :** Le zoom (Ctrl+Molette) et le déplacement (Clic droit) sont appliqués à toutes les images en même temps.  
* **Mode Blink :** Maintenez la touche **Espace** pour alterner instantanément avec l'image de référence.  
* **Auto-Alignement :** Algorithme intelligent pour caler parfaitement des images légèrement décalées.  
* **Analyse Heatmap :** Générez une carte thermique des différences entre vos images.  
* **Exportation Pro :** Exportation propre en JPEG, PNG ou GIF animé, incluant labels et filigranes.  
* **Intégration Windows :** Lancez une comparaison directement depuis l'explorateur de fichiers via le clic droit.  
* **Multilingue :** Support natif du Français et de l'Anglais.

## **🚀 Installation**

### **1\. Prérequis**

Assurez-vous d'avoir Python 3 installé. Ensuite, installez les dépendances nécessaires :  
pip install \-r requirements.txt

### **2\. Intégration au Clic Droit (Optionnel)**

Pour intégrer l'outil à Windows :

1. Ouvrez le fichier install\_menu\_fr.reg (ou en.reg) avec un éditeur de texte.  
2. Modifiez le chemin D:\\\\Documents\\\\Python Scripts\\\\... pour qu'il pointe vers l'emplacement réel de votre script.  
3. Double-cliquez sur le fichier pour l'ajouter au registre.

## **🛠️ Utilisation**

* **Glisser-Déposer :** Déposez des images ou des dossiers directement dans l'interface.  
* **Raccourcis Clavier :**  
  * Espace : Mode Blink (vue référence).  
  * Ctrl \+ Molette : Zoom.  
  * Clic Droit (Maintenir) : Déplacement (Pan).  
  * Suppr : Enlever un pack ou une image.  
  * Ctrl \+ C : Copier la comparaison actuelle.  
  * Ctrl \+ S : Exporter.

## **📝 Licence**

Ce projet est sous licence MIT. Libre à vous de l'utiliser et de le modifier \!
**Comparateur Pro** is designed to streamline the workflow of comparing multiple images simultaneously. With perfect synchronization of zoom and pan operations, intelligent auto-alignment, and heatmap analysis, it's the ideal tool for photographers, designers, and anyone who needs precise visual comparisons.

## **✨ Features**

* **Multi-Image Comparison:** Effortlessly manage and compare smooth image slices with movable sliders.  
* **Total Synchronization:** Zoom (Ctrl \+ Scroll) and pan (Right-Click) actions are applied simultaneously across all images.  
* **Blink Mode:** Hold the Spacebar to instantly toggle between the reference image and the current view.  
* **Intelligent Auto-Alignment:** Automatically aligns slightly shifted images using an advanced 2D affine algorithm.  
* **Heatmap Analysis:** Generate cumulative thermal maps to visualize differences across your image sets.  
* **Professional Exporting:** Export clean, 1:1 ratio images in JPEG, PNG, or animated GIF formats, complete with customizable labels and watermarks.  
* **Seamless Windows Integration:** Launch comparisons or batch exports directly from the Windows File Explorer via the right-click context menu.  
* **Multilingual Support:** Natively supports both English and French, automatically detecting your system language.

## **🚀 Installation**

### **1\. Prerequisites**

Ensure you have Python 3 installed. Then, install the required dependencies using pip:  
pip install \-r requirements.txt

### **2\. Windows Context Menu Integration (Optional but Recommended)**

To integrate Comparateur Pro into your right-click menu:

1. Open install\_menu\_en.reg (or install\_menu\_fr.reg) in a text editor.  
2. Update the path (D:\\\\Documents\\\\Python Scripts\\\\...) to point to the actual location of comparateur\_app.py on your machine.  
3. Double-click the updated .reg file to add the entries to your Windows Registry.

## **🛠️ Usage**

* **Drag & Drop:** Simply drop images or folders directly into the interface to create a new comparison pack.  
* **Shortcuts:**  
  * Spacebar (Hold): Blink Mode (shows reference image).  
  * Ctrl \+ Scroll: Zoom in/out.  
  * Right-Click (Hold & Drag): Pan the view.  
  * Delete: Remove the selected image or pack.  
  * Ctrl \+ C: Copy the current comparison view to the clipboard.  
  * Ctrl \+ S: Open the Export dialog.

## **📝 License**

This project is licensed under the [MIT License](http://docs.google.com/LICENSE). Feel free to use, modify, and distribute it\!
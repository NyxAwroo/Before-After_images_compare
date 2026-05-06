**Comparateur Pro** is designed to streamline the workflow of comparing multiple images simultaneously. With perfect synchronization of zoom and pan operations, intelligent auto-alignment, and heatmap analysis, it's the ideal tool for photographers, designers, and anyone who needs precise visual comparisons.

## **✨ Features**

* **Multi-Image Comparison:** Effortlessly manage and compare smooth image slices with movable sliders.  
* **Total Synchronization:** Zoom (Ctrl \+ Scroll) and pan (Right-Click) actions are applied simultaneously across all images.  
* **Blink Mode:** Hold the Spacebar to instantly toggle between the reference image and the current view.  
* **Intelligent Auto-Alignment:** Automatically aligns slightly shifted images using an advanced 2D affine algorithm.  
* **Heatmap Analysis:** Generate cumulative thermal maps to visualize differences across your image sets.  
* **Professional Exporting:** Export clean, 1:1 ratio images in JPEG, PNG, or animated GIF formats, complete with customizable labels and watermarks.  
* **Quick Right-Click Functions:** Execute fast tasks directly from Windows Explorer without opening the UI (e.g., *Generate Quick Export* for images or *Batch Export* for folders).  
* **Multilingual Support:** Natively supports both English and French, automatically detecting your system language.

## **🚀 Installation**

### **1\. Prerequisites**

Ensure you have Python 3 installed. Then, install the required dependencies using pip:  
pip install \-r requirements.txt

### **2\. Windows Context Menu Integration (Optional but Recommended)**

To integrate Comparateur Pro into your right-click menu, choose the file that matches your preferred language:

1. Choose either **Menu\_Comparateur\_EN.reg** (for English) or **Menu\_Comparateur\_FR.reg** (for French) and open it in a text editor.  
2. Update the path (D:\\\\Documents\\\\Python Scripts\\\\...) to point to the actual location of comparateur\_app.py on your machine.  
3. Double-click the updated .reg file to add the entries to your Windows Registry.

## **🛠️ Usage**

* **Drag & Drop:** Simply drop images or folders directly into the interface to create a new comparison pack.  
* **Windows Explorer Context Menu:**  
  * **On Images:** Select multiple images, right-click, and choose to either open them in the tool or generate an instant "Quick Export" in the background.  
  * **On Folders:** Right-click a folder to compare all its images, or use the "Batch Export" function to process the entire folder seamlessly.  
* **Shortcuts:**  
  * Spacebar (Hold): Blink Mode (shows reference image).  
  * Ctrl \+ Scroll: Zoom in/out.  
  * Right-Click (Hold & Drag): Pan the view.  
  * Delete: Remove the selected image or pack.  
  * Ctrl \+ C: Copy the current comparison view to the clipboard.  
  * Ctrl \+ S: Open the Export dialog.

## **📝 License**

This project is licensed under the [MIT License](http://docs.google.com/LICENSE). Feel free to use, modify, and distribute it\!
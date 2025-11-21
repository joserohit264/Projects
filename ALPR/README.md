#  Automatic License Plate Recognition (ALPR)

An end-to-end **Automatic License Plate Recognition (ALPR)** system built using **Python, OpenCV, TensorFlow, and Tesseract OCR**.  
This project detects license plates from images, preprocesses them, extracts characters, and outputs the final plate number.

---

## Tech Stack

- **Python 3.10**
- **OpenCV** – image preprocessing & plate detection
- **TensorFlow (CPU 2.12)** – character recognition
- **Tesseract OCR** – text extraction
- **NumPy / Pandas / Imutils** – utilities and helper functions
- **Ubuntu / WSL** – runtime environment

---

##  Features

- Automatic license plate detection  
- Preprocessing: grayscale, blur, thresholding  
- Contour filtering to locate plate region  
- Plate cropping and image enhancement  
- Character recognition using TensorFlow  
- OCR using Tesseract  
- Fully working on Ubuntu/WSL  

## Commands
``` bash
# Create Python 3.10 virtual environment
python3.10 -m venv alpr-py10

# Activate virtual environment
source alpr-py10/bin/activate

# Install correct NumPy (TensorFlow compatible)
pip install numpy==1.23.5

# Install OpenCV compatible with NumPy < 1.24
pip install opencv-python==4.7.0.72

# Install TensorFlow CPU (Python 3.10 compatible)
pip install tensorflow-cpu==2.12

# Install required OCR + utilities
pip install pytesseract
pip install imutils
pip install pandas
pip install matplotlib
pip install scikit-learn
pip install pillow

# Install Tesseract OCR for Ubuntu / WSL
sudo apt update
sudo apt install tesseract-ocr libtesseract-dev

# Verify full environment
python3 - <<EOF
import tensorflow as tf
import cv2, numpy, pytesseract
print("TF:", tf.__version__)
print("NumPy:", numpy.__version__)
print("OpenCV:", cv2.__version__)
print("Tesseract:", pytesseract.get_tesseract_version())
print("Environment OK")
EOF

# Run ALPR script
python License_Plate_Recognition.py
```


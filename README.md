# leaf-disease-detection
An AI-powered web application that uses CNN-based deep learning to detect plant leaf diseases from uploaded images and provide remedies, prevention measures, and treatment recommendations.
## Introduction:-
### Problem:- Agriculture plays a vital role in global food production and supports over 2.6 billion people worldwide. However, plant diseases significantly impact crop health and productivity, causing annual losses estimated at over $220 billion and reducing yields by up to 30%. Traditional disease detection methods rely on manual inspection and expert knowledge, which can be time-consuming, costly, and inaccessible to many farmers, especially in rural areas.
### Solution:- This project presents an AI-powered Leaf Disease Detection System that uses Convolutional Neural Networks (CNN) and deep learning techniques to identify plant diseases from leaf images. The system provides accurate disease predictions along with remedies, prevention measures, and treatment recommendations, enabling early intervention and improved crop management.

## Features:-
- User Login and Registration
- Upload/Scan Leaf Images for Analysis
- AI-Based Disease Detection using CNN
- Detection of Multiple Leaf Diseases
- Disease Prediction Results
- Remedies and Treatment Suggestions
- Prevention and Precaution Guidelines
- Scan History Management
- User-Friendly Web Interface

## Technologies Used

### 1. Frontend (User Interface)
Provides login page, image upload, and scan interface. Handles user interaction and displays prediction results.
- HTML
- CSS
- JavaScript
### 2. Backend (Server & API)
Built using Flask (Python) to manage requests and responses.
**APIs Implemented:**
- Login – User Authentication
- Predict – Disease Prediction
- History – Fetch Scan Records
### 3. Machine Learning Model
CNN (Convolutional Neural Network) model built using PyTorch for disease classification.
- Input: Leaf Image (224 × 224)
- Output: Disease Type and Recommended Treatment
### 4. Image Processing
Used for preprocessing and preparing images before prediction.
- PIL (Pillow)
- Torchvision
**Functions:**
- Image Resizing
- Image Normalization
- Tensor Conversion
### 5. Database
SQLite Database (`leafcare.db`)
**Stores:**
- User Details
- Scan History
- Prediction Results
### 6. System Optimization
- Fast Image Processing
- Real-Time Disease Prediction
- Efficient Resource Utilization
### 7. Data Management
- Secure Storage of User Data
- Quick Retrieval of Scan History
- Efficient Database Operations
## Technology Stack (Short Summary)
### Frontend
- HTML
- CSS
- JavaScript
### Backend
- Python
- Flask
### Deep Learning
- Convolutional Neural Network (CNN)
- PyTorch
### Libraries
- NumPy
- OpenCV
- Pillow
- Torchvision
### Database
- SQLite

## Diseases Supported
1. Healthy Leaf
2. Early Blight
3. Late Blight
4. Leaf Spot
5. Powdery Mildew
6. Rust
7. Bacterial Spot
8. Leaf Curl
9. Mosaic Virus
10. Septoria Leaf Spot

## Workflow
1. User uploads a leaf image.
2. Image is resized and preprocessed.
3. CNN extracts important features.
4. Model predicts the disease class.
5. System displays:
   - Disease Name
   - Precautions
   - Remedies
   - Prevention Measures
### Simple Workflow

User Uploads/Scans Leaf Image
↓
Image Preprocessing
↓
CNN Analysis
↓
Disease Prediction
↓
Result with Remedies & Prevention Measures

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/rohitpachghare2808/leaf-disease-detection.git
```

### 2. Navigate to Project Folder

```bash
cd leaf-disease-detection
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run Application

```bash
python app.py
```

## Model Performance

- CNN-Based Deep Learning Model
- Trained on Multiple Disease Classes
- Validation Accuracy: ~75% (20 Epochs)
- Fast and Efficient Disease Prediction

## 📸 Screenshots

### 🔐 Login Page
![Login](screenshots/login.png)

### 🏠 Home Page
![Home](screenshots/home.png)

### 📤 Scan & Upload
![Upload](screenshots/scan_upload.png)

### 🌿 Disease Prediction Result
![Result](screenshots/result.png)

### 📜 Precautions, New Scan & History
![History](screenshots/precaution_new_scan_history.png)

## 👨‍💻 Author

**Rohit Kailas Pachghare**
[Email](rohitpachghare2808@gmail.com)
[LinkedIn](https://www.linkedin.com/in/Rohit-Pachghare/) | [GitHub](https://github.com/rohitpachghare2808)



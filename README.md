   #  MediStore AI - Diabetic Prediction System

  **A Clinical-Grade Machine Learning Tool for Diabetes Risk Assessment**
  
  [![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
  [![React](https://img.shields.io/badge/React-18.0%2B-61DAFB?logo=react&logoColor=black)](https://react.dev)
  [![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
</div>

<br>

## 🚀 Overview

**MediStore AI** is a professional, beautifully designed web application built to predict the likelihood of diabetes in patients using clinical biomarkers. Powered by an upgraded XGBoost Ensemble model and Explainable AI (SHAP), it provides instant, highly accurate risk probabilities, detailed clinical analysis, and personalised health recommendations.
=======
**MediStore AI Diabetic Prediction System** is a professional web application built to predict the likelihood of diabetes in patients using clinical biomarkers. Powered by a Support Vector Machine (SVM) algorithm, it provides instant, highly accurate risk probabilities, detailed clinical analysis, and personalised health recommendations.

Designed with a modern **Glassmorphism UI** aesthetic, the application seamlessly bridges the gap between powerful machine learning inference and an intuitive, pharmacist-friendly user experience.

---

## ✨ Key Features

- **🎨 Professional Glassmorphism UI:** Stunning, responsive React interface featuring transparent frosted-glass cards, dynamic full-screen backgrounds, and smooth animations.
- **⚡ Instant AI Prediction:** Real-time inference using a trained XGBoost Ensemble model (~85%+ accuracy).
- **🧠 Explainable AI (SHAP):** Visualise exactly how each biomarker influenced the AI's decision.
- **🔬 Clinical Biomarker Evaluation:** Dynamic identification of specific positive indicators and risk factors based on the patient's inputted data.
- **💡 Actionable Recommendations:** Tailored clinical and lifestyle recommendations based on the final prediction outcome.
- **🔒 100% Private & Local:** All inference runs locally. No patient data is sent to external APIs.

---

## 🏗️ System Architecture

The application has been upgraded to a robust modern web stack: a **Python/FastAPI** backend for heavy machine learning inference and a **React (Vite)** frontend for a seamless, interactive user experience.

```mermaid
graph TD
    classDef frontend fill:#003366,stroke:#00c8be,stroke-width:2px,color:#fff;
    classDef backend fill:#001a33,stroke:#7fffd4,stroke-width:2px,color:#fff;
    classDef model fill:#004d40,stroke:#00ffcc,stroke-width:2px,color:#fff;
    classDef user fill:#333,stroke:#fff,stroke-width:2px,color:#fff;

    User([👤 User / Pharmacist]):::user

    subgraph Frontend ["🖥️ React + Vite UI Layer"]
        LandingPage[Full-Screen Landing Page]:::frontend
        Dashboard[Prediction Dashboard]:::frontend
        Sidebar[Patient Data Input Form]:::frontend
    end

    subgraph Backend ["⚙️ FastAPI Inference Server"]
        API[POST /predict Endpoint]:::backend
        Eng[Feature Engineering (16 Features)]:::backend
        XGB[[XGBoost Ensemble Model]]:::model
        SHAP[[SHAP Explainer]]:::model
    end

    User -->|Visits Web App| LandingPage
    LandingPage -->|Clicks Get Started| Dashboard
    User -->|Enters Biomarkers| Sidebar
    Sidebar -->|JSON Payload| API
    API --> Eng
    Eng --> XGB
    Eng --> SHAP
    XGB -->|Prediction & Probs| API
    SHAP -->|Base64 Plot Image| API
    API -->|JSON Response| Dashboard
```

---

## 🛠️ Tech Stack

- **Frontend:** React, Vite, Lucide-React, CSS (Custom Glassmorphism)
- **Backend:** FastAPI, Uvicorn, Python
- **Machine Learning:** XGBoost, Scikit-Learn
- **Explainable AI:** SHAP, Matplotlib
- **Data Manipulation:** NumPy, Pandas

---

## 💻 Local Setup & Installation

Follow these steps to run the new dual-architecture MediStore AI locally on your machine.

### 1. Start the Python Backend (FastAPI)
The backend handles the machine learning inference and runs on port `8000`.

Open your terminal and run:
```bash
# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install any missing backend dependencies (if needed)
pip install fastapi uvicorn xgboost shap matplotlib

# Start the FastAPI server
uvicorn server:app --reload --port 8000
```
The API is now running at `http://localhost:8000`.

### 2. Start the React Frontend (Vite)
The frontend serves the UI and runs on port `5173`.

Open a **new, separate terminal** and run:
```bash
# Navigate to the frontend directory
cd frontend

# Install Node modules (first time only)
npm install

# Start the development server
npm run dev
```

The application will now be live in your browser at **`http://localhost:5173`**.

---

## 🩺 Dataset & Model Details

The upgraded model was trained using a custom engineered pipeline with SMOTE balancing. It expands the original 8 biomarkers into **16 engineered features** for higher precision:
1. **Base Features:** Pregnancies, Glucose, Blood Pressure, Skin Thickness, Insulin, BMI, Diabetes Pedigree Function, Age
2. **Engineered Features:** Glucose_BMI_Ratio, Insulin_Resistance, Age_BMI_Interaction, BP_Age_Risk, Glucose_Category, BMI_Category, Age_Category, Metabolic_Syndrome_Risk

**Model Performance:** ~85%+ Accuracy (XGBoost Ensemble).

---

> **⚠️ Medical Disclaimer**  
> *This software is for educational and demonstrative purposes only. It is not intended to be a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified health provider with any questions regarding a medical condition.*

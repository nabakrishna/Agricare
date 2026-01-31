# 🌱 AgriCare Assistant

> **AI-Powered Plant Disease Diagnosis & Remedy System**
> *Helping farmers identify crop diseases through natural language conversations.*

![Version](https://img.shields.io/badge/version-1.2.0-blue) ![Python](https://img.shields.io/badge/Python-3.8+-yellow) ![Flask](https://img.shields.io/badge/Backend-Flask-green) ![Status](https://img.shields.io/badge/Status-Beta-orange) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Overview

**AgriCare** is an intelligent agricultural assistant designed to bridge the gap between farmers and expert agricultural knowledge. Unlike standard search engines, AgriCare uses **Context-Aware Logic** and **Fuzzy String Matching** to understand imperfect user descriptions (e.g., "red spot" instead of "Brown Spot Disease") and provides immediate organic and chemical remedies.


---

## ✨ Key Features

* **🧠 Context-Aware Memory:** The bot "remembers" the conversation. If you say *"Rice"* and then later say *"red spots"*, it intelligently combines them to form a diagnosis.
* **🔍 Fuzzy Logic Engine:** Powered by `RapidFuzz`, the system handles typos and vague descriptions (e.g., matching "yellowing leaf" to "Rice Tungro Disease").
* **💾 Automatic Report Saving:** Every successful diagnosis is automatically logged into a SQLite database (`reports` table) for future reference.
* **💊 Dual Remedy System:** Provides both **Organic** (home-made) and **Chemical** treatment options for every disease.
* **⚡ Zero-Training Deployment:** Uses a lightweight, rule-based knowledge graph instead of heavy Deep Learning models, ensuring instant startup and low resource usage.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python (Flask) | REST API & Core Logic |
| **Frontend** | HTML5, CSS3, JS | Responsive Chat Interface |
| **Database** | SQLite3 | Stores Knowledge Base & User Reports |
| **AI Logic** | RapidFuzz | Fuzzy String Matching & Token Ratios |
| **Memory** | SessionStorage | Frontend-side context management |

---

## 📂 Project Structure

```bash
AgriCare/
├── .gitignore                 # Specifies files for Git to ignore
├── LICENSE                    # MIT License details
├── README.md                  # Project documentation
├── agricare.db                # SQLite Database (Auto-generated)
├── app.py                     # Main Flask Application (Server)
├── index.html                 # Main Chatbot Interface (Frontend)
├── plant_diseases_data.json   # Backup/Source data for diseases
├── requirement.txt            # Python Dependencies list
├── script.js                  # Frontend Logic & API Calls
├── seed_database.py           # Script to reset/populate the database
├── styles.css                 # Styling for the chat interface
└── version_details.json       # Project Metadata and Version info
```

## 🛠 Installation & Setup

Follow these steps to run AgriCare on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/nabakrishna/agricare.git
cd agricare
```

## 2. Install Dependencies
You need Python installed. Run the following command to install the required libraries:

```bash
pip install flask flask-cors rapidfuzz
```
### 3. Initialize the Database
You do not need to create the database manually. The application automatically checks for agricare.db on startup and creates it with the latest schema if missing.

### 4. Run the Server
```bash
python app.py
```
### You should see:
``` bash
🚀 STARTING SERVER ON PORT 5000...
```
### 5. Access the App
Open your browser and go to: 
```bash
http://127.0.0.1:5000
```

## 💡 How to Use

* **Start a Chat** — Say "Hello" or name a crop (e.g., "Wheat").
* **Describe Symptoms** — Type symptoms like "brown spots", "yellow leaves", or "white streaks".
* **Context Test** — Multi-turn conversation flow:
    * **User:** "Red spots"
    * **Bot:** "Which plant is this for?"
    * **User:** "Rice"
    * **Bot:** (Combines inputs) -> "Diagnosis: Brown Spot Disease..."
* **View Reports** — Check your terminal or database to see saved reports.

## 📡 API Documentation

* **`POST /api/analyze-symptoms`** — Accepts user input and returns diagnosis:
    * **Request Body (Standard):**
        ```json
        {
          "symptoms": "rice with brown spots"
        }
        ```
    * **Request Body (Context-Aware):**
        ```json
        {
          "plant": "Rice",
          "symptom": "brown spots"
        }
        ```
    * **Response (Success):**
        ```json
        {
          "disease": "Brown Spot",
          "organic": "Spray neem oil.",
          "chemical": "Apply Mancozeb.",
          "source": "AgriCare Database (Match: 85%)",
          "is_casual": false
        }
        ```

## 🔮 Future Roadmap

* **Image Recognition** — Integrate TensorFlow/CNN for leaf photo uploads.
* **Voice Support** — Add Speech-to-Text for farmer accessibility.
* **Local Dialect Support** — Hindi/Regional languages via Google Translate API.

## 👨‍💻 Author

* **Naba Krishna Hazarika**
* **Department:** Integrated M.Tech (CSE - Computational and Data Science)








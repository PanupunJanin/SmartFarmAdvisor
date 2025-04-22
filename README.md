# 🌱 Smart Farm Advisor

## 👥 Team Members

- **Panupun Janin** 6410545568 – Department of Software and Knowledge, Faculty of Engineering, Kasetsart University
- **Oak Soe Htet** 6610546312 – Department of Software and Knowledge, Faculty of Engineering, Kasetsart University  
- *(Add or remove members as needed)*

## 🧠 Project Overview

**Smart Farm Advisor** is an intelligent decision-support system designed to assist farmers in selecting optimal crops based on real-time environmental conditions. The system utilizes IoT sensors to gather data on:

- Soil moisture  
- Ambient humidity  
- Temperature  
- Light intensity  

This local sensor data is then compared with crop-specific optimal growth requirements sourced from the [EcoCrop Database](https://github.com/OpenCLIM/ecocrop/blob/main/EcoCrop_DB.csv). The system provides users with:

- A list of suitable crops for their current conditions  
- Feedback and suggestions for environmental adjustments  
- Detailed sensor statistics and crop matching scores  

## 🔧 Features

- Real-time environmental monitoring via IoT sensors  
- Crop suitability analysis with ranking based on compatibility  
- Suggestions for improving growing conditions  
- Search by crop name to view detailed suitability and stats  
- Score-based recommendation system with percentage match  

## 📦 Sensor Modules Used

- **Soil Moisture Sensor:** ZX-SOIL x1  
- **Light Sensor:** KY-018 x1  
- **Temperature & Humidity Sensor:** KY-015 x1  

## 🛠 Required Libraries and Tools

- Python 3.10+  
- Django 4.x  
- SQLite or other Django-supported DB  
- Sensor interfacing using MicroPython and Node-Red
- Frontend: HTML/CSS with Django templating  
- Data source: [EcoCrop_DB.csv](https://github.com/OpenCLIM/ecocrop/blob/main/EcoCrop_DB.csv)

## 🖥️ How to Run

1. **Clone the repository:**
    ```bash
    git clone https://github.com/PanupunJanin/SmartFarm.git
    cd smart-farm-advisor
    ```

2. **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run Django server:**
    ```bash
    python manage.py migrate
    python manage.py loaddata data/smartfarm_data.json
    python manage.py runserver
    ```

5. **Import crops data(only once):**
    ```
    http://127.0.0.1:8000/smartfarm/import-crops
    ```

6. **Access the web app:**
    ```
    http://127.0.0.1:8000/smartfarm
    ```

## 🔗 GitHub Repository

[https://github.com/PanupunJanin/SmartFarm](https://github.com/PanupunJanin/SmartFarm)

---

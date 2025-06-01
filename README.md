# 🌍 World Cup Players Analysis

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/pandas-1.0+-brightgreen.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.0+-orange.svg)
![Seaborn](https://img.shields.io/badge/Seaborn-0.11+-lightblue.svg)

This project provides a statistical and visual analysis of player and match data from the FIFA World Cup. It includes interactive visualizations and comparisons to explore player performance and physical characteristics across different tournament editions.

## 📌 Key Features

- 📊 Visualization of player statistics: age, height, and position
- ⚽ In-depth goal analysis: by minute, tournament stage, and shot type
- 🌎 Comparisons between federations and national teams
- 📈 Historical evolution of physical metrics
- 🏆 Performance analysis by tournament phase

## 📦 Requirements

- Python 3.8 or higher  
- pandas >= 1.0  
- matplotlib >= 3.0  
- seaborn >= 0.11  
- Jupyter Notebook (optional but recommended)

Install dependencies with:

```bash
pip install -r requirements.txt


🚀 How to Run
The project is structured in different stages:

1. 📥 Data Extraction
Scripts located in src/api_extract/ are used to retrieve data from the worldfootball.net API.
a) These scripts save raw data into the data/json.
b) _json_to_excel.py transforms this JSON data into Excel files.


2. 📊 Data Analysis
All analysis scripts are located in the analysis/ folder.
Each script is independent and focuses on a specific aspect of the data.
You can run them separately if you need to.

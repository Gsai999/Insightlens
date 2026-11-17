Markdown
# InsightLens: A Low-Code Automated Data Analytics Platform

[![Python Version](https://img.shields.io/badge/Python-3.10%252B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**InsightLens** is a robust, web-native, low-code exploratory data analysis (EDA) and automated visualization platform built using Python and Streamlit. It bridges the gap between raw data storage and actionable intelligence by automating schema profiling, missing value imputation, statistical summary generation, and interactive Plotly charting.

---

## 🚀 Key Features

* **Multi-Format Ingestion:** Seamlessly upload CSV, TSV, Excel (`.xlsx`, .xlsm, .xls), Parquet, and JSON files, or fetch datasets directly via public URLs.
* **High-Performance Parsing:** Integrates the Rust-backed **Calamine** engine to achieve near-instantaneous parsing of large spreadsheet structures.
* **Automated Data Profiling:** Automatically infers column data types (numerical, categorical, temporal, geographical, and identifier) and computes missing value metrics.
* **Data Hygiene & Cleansing:** Configurable rule-based routines for automated whitespace trimming, duplicate record elimination, and missing value imputation.
* **Interactive Visualization Suite:** Real-time Plotly chart generation including distribution histograms, box plots, category bar charts, and correlation heatmaps.
* **Standalone Reporting:** Export cleaned datasets and responsive HTML analytical dashboard reports effortlessly.

---

## 🛠️ Tech Stack

* **Frontend & Framework:** Streamlit (Python-based reactive web application)
* **Data Processing & Analysis:** Pandas, NumPy
* **High-Performance Parsing:** Python-Calamine (Rust backend)
* **Data Visualization:** Plotly Express & Graph Objects

---

## ⚙️ Installation & Local Setup

Follow these steps to set up and run InsightLens locally on your machine:

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/Gsai999/Insightlens.git](https://github.com/Gsai999/Insightlens.git)
   cd Insightlens
Create and Activate a Virtual Environment:

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install Dependencies:

Bash
pip install --upgrade pip
pip install -r requirements.txt
Run the Application:

Bash
streamlit run app.py
📂 Project Directory Structure
Plaintext
InsightLens/
│
├── app.py                  # Main Streamlit application entry point
├── requirements.txt        # Project dependencies & package versions
├── modules/
│   ├── __init__.py
│   ├── analysis.py         # Automated profiling, quality checks & statistics
│   ├── cleaning.py         # High-performance file loaders & data cleaning
│   └── visualization.py    # Dynamic Plotly chart generators
└── README.md               # Project documentation
📖 Usage Guide
Launch the Web App: Open your terminal, run streamlit run app.py, and open the local URL (http://localhost:8501) in your browser.

Load Data: Use the sidebar panel to upload your dataset file (.csv, .xlsx, .json) or paste a public CSV/Excel link.

Explore Quality & Statistics: Navigate through tabs to view dataset dimensions, missing cell counts, and descriptive statistics.

Generate Visualizations: Select specific columns to instantly render interactive charts and correlation matrices.

👨‍💻 Author
Ganpa Sai Baba (Reg. No. 094255510205)

Program: Master of Computer Applications (M.C.A) - III Semester

Institution: Prof. G. Ram Reddy Centre for Distance Education, Osmania University, Hyderabad

📄 License
This project is developed for academic purposes as part of the MCA curriculum under Osmania University.


---

### How to add this to your GitHub repository:
1. In your local project folder (`InsightLens`), create a new file named `README.md`.
2. Paste the text above into `README.md` and save it.
3. Push the new file to GitHub by running these commands in your terminal:
   ```bash
   git add README.md
   git commit -m "Add professional project README.md"

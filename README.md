# Automated Insight Generation

## Project Overview

Automated Insight Generation is a Streamlit-based data analytics application that automatically analyzes healthcare data and generates human-readable insights.

The application detects:

- Trends
- Outliers
- Correlations
- Severity levels

It also provides interactive filters, visualizations and downloadable CSV reports.

## Features

### 1. Data Input
- Upload healthcare CSV files
- Preview uploaded data
- Validate required columns
- Display missing-value information

### 2. Interactive Filters
Users can filter the dataset by:

- District
- Month
- Indicator

### 3. Trend Detection
The application compares the current value with the previous period and calculates percentage change.

Trend severity is determined using a configurable threshold.

### 4. Outlier Detection
The application supports outlier detection using:

- IQR method
- Z-score method

### 5. Correlation Analysis
Pearson correlation is calculated between numeric healthcare indicators.

A configurable threshold is used to identify strong correlations.

### 6. Visualizations
The dashboard provides:

- District trend line chart
- Pearson correlation heatmap
- Severity summary chart
- Correlation matrix

### 7. Generated Insights
Each insight contains:

- Insight ID
- Type
- Indicator
- Entity
- Period
- Metric
- Change
- Severity
- Explanation

### 8. Downloads
Users can download:

- Insights CSV
- Correlation Matrix CSV

## Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- SciPy
- Plotly

## Project Structure

```text
Automated-Insight-Generation/
│
├── app.py
├── dataset.csv
├── requirements.txt
├── README.md
└── venv/
<h1 align="center">Airbnb Analysis Dashboard for Montreal</h1>
This repository contains the Power BI dashboard and the Python data transformation script for analyzing Airbnb listings in Montreal 2024. 
The goal of this project is to provide insights into key metrics such as revenue, host performance, property types, seasonal trends, and review scores

<h2 align="center">Data Source</h2>

The data used in this project was obtained from [Inside Airbnb](https://insideairbnb.com/get-the-data/), which provides detailed Airbnb datasets for various locations worldwide. The data used was from **2024 Listings in Montreal**. The data can be downloaded via this link:  
[Download Data](https://drive.google.com/drive/folders/1UHhhEAsn-Z8-y3s1z8xJzPM90eBDdnMd?usp=sharing)

<h2 align="center">Data Cleaning and Transformation</h2>

Tool Used: Python
Multiple data files, including CSV and GeoJSON files, were combined and processed for analysis. 
The data cleaning and transformation processes were performed in **Python** and include the following steps:

### 1. Calendar Data

The calendar data (`calendar_data_cleaned.csv`) was prepared using the following steps:

- **Data Importation:** Multiple calendar CSV files for different time periods were concatenated into a single DataFrame.
- **Duplicate Handling:** Duplicated rows were identified and removed, keeping the first occurrence.
- **Data Type Conversion:** 
  - Price columns were cleaned to remove symbols (e.g., $, commas) and converted into numeric data types. 
  - Dates were converted to a consistent datetime format.
- **Missing Value Handling:** 
  - Columns such as `minimum_nights` and `maximum_nights` were checked for missing or placeholder values. 
  - Rows with missing data in critical fields were removed.
- **Column Validation:** The `adjusted_price` column was analyzed and found redundant (identical to the `price` column). It was subsequently dropped.
- **Export:** The cleaned dataset was saved as `calendar_data_cleaned.csv` for further use.

### 2. GEO Data

The GEO data (`GEO_data.csv`) was prepared using **GeoPandas** for handling spatial information:

- **Data Importation:** GeoJSON files representing different geographical slices were concatenated into a GeoDataFrame.
- **Column Cleanup:** Unnecessary columns, such as `neighbourhood_group`, were dropped.
- **Duplicate Handling:** Duplicate rows were identified and removed, keeping the first occurrence.
- **Export:** The cleaned GeoDataFrame was saved as `GEO_data.csv` for mapping and spatial analysis.

### 3. Listings Data

The listings data involved similar cleaning processes:

- **Data Concatenation:** Data files were merged into a single dataset.
- **Duplicate Handling:** Duplicated rows were removed to ensure no listing was counted multiple times.
- **Data Type Adjustments:** Numeric and categorical data were validated, and placeholder values were addressed.
- **Export:** The cleaned listings data was saved for use in the Power BI dashboards.

### 4. Neighbourhood Data

The neighbourhood data file was processed to ensure consistency:

- **Concatenation and Cleanup:** Neighbourhood data from multiple sources was combined and validated for duplicates and missing values.
- **Export:** The cleaned neighbourhood data was prepared for integrating neighborhood-level insights into the dashboards.

### 5. Reviews Data

The reviews data underwent structured cleaning and transformation, involving:

- **Data Concatenation:** Review datasets from different time periods were combined into a single DataFrame.
- **Missing Value Handling:** Missing entries were replaced with "missing," and rows with incomplete comments were removed.
- **Duplicate Handling:** Duplicated rows were removed to retain only unique reviews.
- **Data Type Adjustments:** The date column was converted to a datetime format, and text fields were normalized for consistency.

<h2 align="center">Data Modeling and Preparation in Power BI</h2>

### Data Scope:
The dataset was filtered to include only data from January 1, 2024, to December 31, 2024, ensuring that the analysis focused on the most relevant and recent period. This decision was made to optimize computational efficiency, as the dataset size was already substantial with just the 2024 data, making it more manageable for processing and analysis.

### Data Import:
Cleaned datasets were imported into Power BI, including:
- **Calendar Data** (filtered for 2024 availability)
- **Listings Data**
- **Review Scores**
- **Neighborhood and Geographic Data**

### Initial Structuring Challenges:
Upon importing the datasets, the data was not well-structured for analysis. To address this:
- The datasets were logically divided into **separate tables** based on their role in the analysis (e.g., Host, DateTable, Listing).
- This division ensured **better organization** and supported scalable relationships in the data model.

### Data Modeling:
A **star schema approach** was adopted for simplicity and performance optimization. The relationships between the tables were established as follows:
- **Listing Table**: Served as the central fact table, connecting with:
  - **GEO_data**: For spatial analysis by neighborhoods.
  - **Host Table**: For host-level metrics such as tenure, acceptance rate, and response times.
  - **Calendar_data_filtered**: For detailed metrics on revenue, occupancy, and availability.
  - **Listing_Quarter Table**: For quarterly summaries of key listing metrics.
  - **DateTable**: To support time-based analysis.
- Primary and foreign key relationships (e.g., `listing_id`, `host_id`) were validated to ensure accuracy.

### Calculated Columns and Measures:

1. **Calculated Columns**:
   Additional fields were created to enhance the analysis, such as:
   - Revenue categories
   - Availability metrics
   - Host tenure calculations

2. **Measures**:
   Dynamic calculations were defined to support visualizations, such as:
   - **Total Revenue**
   - **Average Revenue Per Listing**
   - **Occupancy Rate**
   - **Average Review Scores**
   - **Host Response Rate**
   - **Monthly Revenue Trends**

<h2 align="center">Power BI Dashboard</h2>

The Power BI dashboard for this project is available for download at the following link:  
[Download Dashboard](https://drive.google.com/file/d/1TJDliFiozIpZRHtysFEW8XTgbaNTTS3T/view?usp=sharing)

---

### Key Features:

- **Comprehensive Insights**:  
  The dashboard provides an in-depth analysis of Airbnb listings in Montreal for the year 2024, offering key metrics and trends.

- **Interactive Visualizations**:  
  Users can explore data through filters, slicers, and dynamic visualizations, including:
  - Total revenue, revenue per listing, and revenue by property type.
  - Seasonal availability and occupancy rates.

- **Host Performance**:  
  Metrics such as host tenure, superhost status, and response times.

- **Review Analysis**:  
  Average review scores, review frequency, and their relationship with revenue.

- **Property Type and Availability**:  
  Insights into property types, seasonal availability, and occupancy rates.

- **Neighborhood Insights**:  
  Metrics and visualizations at the neighborhood level using spatial data.

---

This dashboard was designed to provide actionable insights into revenue generation, host behaviors, seasonal trends, and review dynamics for Airbnb listings in Montreal.
![image](https://github.com/user-attachments/assets/3e3a4f8b-ebe3-421f-9072-c52f0717b83d)
![image](https://github.com/user-attachments/assets/ccadf4bb-61db-47cf-ac57-88fcab0cc52e)
![image](https://github.com/user-attachments/assets/c2bbe3c0-cf0b-45d1-99e5-af3f4a934343)
![image](https://github.com/user-attachments/assets/e65dfca9-3fd9-4b3b-919f-d73778acb008)

<h2 align="center">Challenges</h2>
This project faced several challenges during its development:  

- **Data Size and Scope**:  
  The dataset was large, even when filtered to include data from 2024. This choice was made to ensure the analysis remained manageable and efficient while focusing on the most relevant and recent period.  

- **Data Cleaning Complexities**:  
  Handling duplicate records, missing values, and inconsistent formatting required significant effort to ensure accuracy in the final analysis.  

- **Structuring the Data Model**:  
  The initial dataset lacked proper structure, which required separating it into logically defined tables (e.g., Host, Listing, Calendar, Reviews) and establishing clear relationships to support analysis in Power BI.  

- **Sentiment Analysis of Customer Reviews**:  
  An attempt was made to analyze customer sentiment based on review text. However, the dataset contained over 13 million reviews in multiple languages, and translation required significant computational resources. This limitation prevented immediate progress, but efforts are ongoing to implement a solution, such as batch translation over time. Please look at the Python_Code_For_Review_Translation.py to review the translation attempt to make the customer sentiment Analysis (In progress)  

---
<h2 align="center">Contact Information</h2>

For questions, feedback, or collaboration opportunities, feel free to reach out:  

- **GitHub Profile**: [Your GitHub Profile Link](https://github.com/MJohnsonConstantin)
- **Email**: MJohnsonConstantin@hotmail.com  
- **LinkedIn**: [Your LinkedIn Profile Link](https://www.linkedin.com/in/matthieu-johnson-constantin-5932b7161/)   

I’d also be happy to assist with any issues or discuss potential improvements to the analysis and dashboard.  

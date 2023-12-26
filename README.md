# Webmotors Price Scraper
## Overview
This Python script is designed to extract and compare car prices from the Webmotors website based on a provided dealership inventory in XLSX format. It utilizes the Streamlit library for the user interface and performs web scraping using the Webmotors API.

## Features
- Extracts car information from the provided XLSX file.
- Cleans and processes the data for accurate comparison.
- Queries the Webmotors API to obtain price information for each car.
- Calculates an average price based on the matching car models.
- Outputs the processed data to a new XLSX file.

## Installation

1. Clone the repository:

```
git clone https://github.com/guinacio/webmotorsScrapper.git
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```
3. Run the script:
```
streamlit run webmotors_scraper.py
```

## Usage
- Open your browser and navigate to the provided Streamlit URL (usually http://localhost:8501).
- Upload the dealership's XLSX file through the Streamlit interface. (Accepted file is based on DealerNet's export)
- Click the "Processar Arquivo" button to initiate the price comparison.
- View the results, including the matched car models and their average prices.
- The processed data is saved in the specified output XLSX file.

### Configuration
- Adjust the KM_OFFSET variable to set the kilometer offset for the Webmotors search.
- Change the LOCATION variable to your desired city or state.
- Modify the OUTPUT_FILE variable to set the output filename.
- Toggle the SHOW_SEARCH_RESULTS flag to display detailed search results in the Streamlit interface.

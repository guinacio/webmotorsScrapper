import streamlit as st
import pandas as pd
import requests
import numpy as np
from fuzzywuzzy import fuzz
import time
import re
import locale
from random import randint

# Headers for Webmotors API request
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.69'}

KM_OFFSET = 10000 #Offset in KM for the ODOMETER Webmortors search
LOCATION = 'Santa Catarina' #Change it to your CITY or STATE
OUTPUT_FILE = 'ListaProcessada.xlsx' #Defines output filename
SHOW_SEARCH_RESULTS = False #Flag to show results for each search on Webmotors

def load_data(file_path):
    data = pd.read_excel(file_path)
    return data

def write_data(newTableCars):
    try:
        newTableCars.to_excel(OUTPUT_FILE, index=False)
    except Exception as e:
        st.error(f"An error occurred while writing to Excel file: {str(e)}")

def clean_data(df):
    filteredDf = df[~df['Veiculo Cod'].str.contains('Contagem')]
    filteredDf = filteredDf[filteredDf['Marca'].notna() & (filteredDf['Marca'] != ' ')]
    filteredDf = filteredDf[filteredDf['Familia'].notna() & (filteredDf['Familia'] != ' ')]
    filteredDf['KM'] = filteredDf['KM'].apply(lambda x: locale.format_string('%d', x, grouping=True))
    filteredDf['Fipe'] = filteredDf['Fipe'].apply(lambda x: locale.currency(x, grouping=True))
    filteredDf['Webmotors'] = filteredDf['Webmotors'].apply(lambda x: locale.currency(x, grouping=True))
    filteredDf = filteredDf.reset_index()
    return filteredDf

def replace_abbrev(row):
    #Dealing with common abbreviations on model names
    patternEnd = r'\s(\d{2}/\d{2})$'
    model = re.sub(patternEnd, '', row['Modelo'])
    patternAUT = r'(\s[Aa][Uu][Tt]\.?$)'
    model = re.sub(patternAUT, ' AUTOMÁTICO', model)
    model = model.replace(' DSL ',' DIESEL ').replace('A/T','AUTOMÁTICO').replace('M/T','MANUAL').replace('FFV','FLEX').replace(' HIGH.',' HIGHLINE ').replace(' TDI ',' TURBO INTERCOOLER DIESEL ').replace(' CON ','CONNECT MULTIDRIVE')
    return model

def main():
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    st.set_page_config(page_title='Cotações Webmotors', page_icon='🚘', layout='wide', initial_sidebar_state='auto', menu_items=None)
    st.sidebar.title("Automação Cotações Webmotors")
    
    uploadedFile = st.sidebar.file_uploader("Selecione o arquivo Excel", type=["xlsx"], accept_multiple_files=False)

    if not uploadedFile:
        st.stop()

    if uploadedFile is not None:
        st.sidebar.success(f"Arquivo selecionado: {uploadedFile.name}")
        run = st.sidebar.button('Processar Arquivo',type='primary')
    
    tableCars = load_data(uploadedFile)
    
    tableCars = clean_data(tableCars)

    columnsDisplay = ['Veiculo Cod', 'Empresa', 'Placa', 'Modelo', 'KM', 'Fab/Modelo', 'Fipe', 'Webmotors', 'WebmotorsBOT']

    st.dataframe(tableCars, column_order=columnsDisplay)
    nRows, nCols = tableCars.shape
    if run:
        progBar = st.progress(0, text='Processando arquivo. Aguarde, leva cerca de 8s para cada carro consultado.')
        for index, row in tableCars.iterrows():
            brand = row['Marca']
            family = row['Familia']
            
            model = replace_abbrev(row)
            
            modelAux = model.split()
            if 'SEMINOVOS' in family:
                family = modelAux[0]
            modelClean = ' '.join(modelAux[1:])
            if SHOW_SEARCH_RESULTS:
                st.write(brand)
                st.write(family)
                st.write(modelClean)
            km = int(row['KM'].replace('.',''))
            kmUp = km+KM_OFFSET
            kmDown = km-KM_OFFSET
            yearParts = row['Fab/Modelo'].split('/')
            yearMake = int(yearParts[0])
            yearModel = int(yearParts[1])
            
            webmotorsURL = f'https://www.webmotors.com.br/api/search/car?url=https://www.webmotors.com.br/carros%2F%3Festadocidade%3D{LOCATION}%26tipoveiculo%3Dcarros%26anoate%3D{yearModel}%26anode%3D{yearMake}%26kmate%3D{kmUp}%26kmde%3D{kmDown}%26marca1%3D{brand}%26modelo1%3D{family}'
            response = requests.get(webmotorsURL,headers=HEADERS)
            if response.status_code == 200:
                data = response.json()

                car_data = []
                for car in data["SearchResults"]:
                    carInfo = {
                        "Make": car["Specification"]["Make"]["Value"],
                        "Model": car["Specification"]["Model"]["Value"],
                        "Version": car["Specification"]["Version"]["Value"],
                        "Price": car["Prices"]["Price"],
                        "Year": f"{car['Specification']['YearFabrication']}/{int(car['Specification']['YearModel'])}",
                        "Odometer (km)": car["Specification"]["Odometer"],
                        "Transmission": car["Specification"]["Transmission"]
                    }
                    car_data.append(carInfo)

                df = pd.DataFrame(car_data)
                
                for index2, row2 in df.iterrows():
                    similarity = fuzz.token_set_ratio(modelClean, row2['Version'])
                    if similarity >= 90:
                        df.loc[index2,'match'] = True
                        df.loc[index2,'simil'] = similarity
                    else:
                        df.loc[index2,'match'] = False
                        df.loc[index2,'simil'] = similarity
                
                if SHOW_SEARCH_RESULTS:
                    st.dataframe(df)
                    
                df = df[df['match'] == True]
                averagePrice = df['Price'].mean()

                tableCars.loc[index,'WebmotorsBOT'] = averagePrice

                time.sleep(randint(8,10))
            else:
                st.write("Failed to retrieve data from the URL.")
        
            progBar.progress(round((index+1)*100/nRows), text='Processando arquivo. Aguarde, leva cerca de 8s para cada carro consultado (limitação do Webmotors).')
        
        tableCars['WebmotorsBOT'] = tableCars['WebmotorsBOT'].apply(lambda x: locale.currency(x, grouping=True))

        st.dataframe(tableCars, column_order=columnsDisplay)
        write_data(tableCars)

if __name__ == '__main__':
    main()
"""Main module for the Streamlit app"""
import requests
import streamlit as st
import random
import json
import pandas as pd
import altair as alt
import plotly.express as px

from datetime import datetime


NAGER_API_BASE = 'https://date.nager.at/api/v2'

HELLO_SALUT_API_BASE = "https://fourtonfish.com/hellosalut"

@st.cache
def load_country_codes():
    """Loads country codes available from the Nager.Date API

    Returns:
        A list of country codes. Each country code is
        a two character string.

    Raises:
        requests.exceptions.RequestException: If the
            request to the Nager.Date API fails.
    """


    url = '/'.join([NAGER_API_BASE, 'AvailableCountries'])
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    #### TODO - Process the response ####

    country_codes = response.json()
    codes = []
    for code in country_codes:
        codes.append(code["key"])
    

    #####################################

    return codes

@st.cache
def load_decade_holidays(country_code):
    url = '/'.join([NAGER_API_BASE, 'PublicHolidays'])
     
    current_year = datetime.now().year
    num_holidays_dict = {}
    num_holidays_dict['YEAR'] = []
    num_holidays_dict['ANNUAL_HOLIDAYS']=[]

    for i in range(1, 11):
        year = current_year - i;
        num_holidays_dict['YEAR'].append(str(year))
        year_url = '/'.join([url, str(year), country_code])
        try:

            response = requests.get(year_url)
            #st.markdown(response.json())
            num_holidays = len(response.json())
            num_holidays_dict['ANNUAL_HOLIDAYS'].append(num_holidays)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        #num_holidays_dict[year] = [num_holidays]
    
    return num_holidays_dict 
    


def main():

    url = '/'.join([HELLO_SALUT_API_BASE, '?ip='])
    ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    
    try: 
        response = requests.get(url+ip)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


    greeting = json.loads(response.text)

    st.markdown(greeting["hello"])

    country_codes = load_country_codes()

    country_code = st.selectbox('Select a country code',
                                country_codes)

    st.write('You selected country code -', country_code)

    holidays_dict = {}
    holidays_dict = load_decade_holidays(country_code)
    holidays_df = pd.DataFrame(holidays_dict)
    

    basic_chart = alt.Chart(holidays_df).mark_line().encode(
    x='YEAR',
    y='ANNUAL_HOLIDAYS')
    st.altair_chart(basic_chart)

if __name__ == '__main__':
    main()


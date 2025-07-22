import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
import os
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet

# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

# Load config file with user credentials.
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initiate authentication.
authenticator = stauth.Authenticate(
    config['credentials'],
)

# Call user login form.
result_auth = authenticator.login("main")
    
# If login successful, continue to aitam page.
if st.session_state.get('authentication_status'):
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state.get('name')}* !')

    # Model list, Vector store ID, assistant IDs (one for initial upload eval, 
    # the second for follow-up user questions).
    MODEL_LIST = ["gpt-4.1-nano"] #, "gpt-4o-mini", "gpt-4.1", "o4-mini"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    INSTRUCTION_ENCRYPTED = b'gAAAAABofv6BAB4UieVOatIoFezecObEEYePQt5iCgPiH2IdVA2eNPS8DZLEwXmHsrx5CxyCdj5Rt-O_EK8-K6gp6dTO-N933nSw4gJd-zbzpTPTNi1Q7Sb2vXw69rZHfAdTTDBuF-t66HnOER_fnDWTrNfqUqLGRJXFw4USaa11IUirulg--G8Q1zW9yiIwVxJfmw-tIS16TtMid0leIbpyB3NK37dhKZ2h66CTBLj-w3XjaYSvSCXaklEcial2OImp6DjO2u9qg3N6UYxmgcXrb4aNuABnb2rAa5WuwaOSX0UKfX7YTdHMcNyGjMOUo6d4w7wOkvwhZnr1s2JCgIbK4pW1YLobHJPhRnfleYULGgB9nBNFWlA3b3FmI3Nwuv-Mn7VnZJU_vImZLu1gL5vXzwAkIEcPdm4zqBfCdHBqZnXN3RoNjfmI9u0TOpFJFUObTy6_-Pyjmp0vmIMeUTZWCAEC71EY18afaCg_nHRkaf7sTwNCDriMhyEfsN59MpkeUbGyWe-9IYo4UvL-ZP0rvZmOsW-YuhpjlAnoBorkVUjoRpBs6O-NmvaG6v_5IZC5eqUMysuIu9apDQ8bhwQNm9H_BfW5uAnsIe8QA46QAjjGUnKpSh7aJe4wjy2fOeQAgR9Xh59TZMWgvDb_htmeI6cmz7liwhV646H13SEKRsQHucO0pYsD7Sl3qy9sljYe0b154mFrPXu62Fx7kLDf3RF_CLybKNycNwXt8w6gVxgY_OMkQqyO5vvcKodt_O5zLidH_PxEaONVpFHD1QkjT_0VS_uFsl9RgR81VR0RWhVcQfOJWmRdVJplkNmsrpLcXgiG8QfUQnn4WpNJmY2y92BqkIbv_JhVz8lsViR8LA3p8eqqXUtaWbrx0OPRZ00PGRDf1dVzg1HtQlU6ZG-tcEsA8lKSD09L37jCXJ8sRpAVN1QxAT_VOxbXCOlx6DaYUMtJ-zNt1Rn9C0LKhcMJFyGPsiC7VJ7DCehs1ZRaGVKJBbAVh3a8T4WOItpK5F8CRt-MGcfU6a1x7vHBgbZ8HRKd70_NqGOoZDXcdMZXkx1BjzCK0NgpQrcGFVFnRlpbE51Q2aY_Rp0vgiqbuTQujKd0nl6VK1dvgBqKHaTETSqySb12rY4Y7Y2TUCr8zizqwqW7D3ugV2OGUSPiuB0MCP_m8clwVqaJkRH74SFjBSSoSiEhAorMicoPpyLNSozEfqTEcxWkgrigmpPCexNcBdOJEexV6vMlx9yH-auGYExsN-bpMs_RHy6AhV1zW7vpcDKjmHbQMFO-X5Wtcj7hihh7FI2g8zvGTsi6326lVoLsw2K-zGgCLmuELdSge77uYhJYNh6wanwL6hcP5TokfhVDofaQnKQ2d-xi_lcyyuxgnYitMvhAJDQ1h9hVme1VdeTA1MUqN6rPnOLc4bCuii6_UogTvB1dZOQbyN-gwRhFyvPlYGiCH82LbZ7Bnb6VGog08AuwgIgKVK61DFwVFbY-j-ISkcJXucT88e1sguw2KIY-ry2I2cUexWZ4pEgPBtLQsUQGHBSmQYYIrx6YqyfZFh2GABRUGDj-zygxxsc2FPpoAWPa2NKCBbcMnCWnh39Ctp9bpRADFy69CZXWV_f7Jabm-78_eTbxiJKYFPY00MA9bsTD5t5rfFG3GrdTMhTgzVtfssjWT7S8gITHmXiXs1njP6tHty7H5wJNmQVfbApD9UpmF2OFE_SjWqG7e7md1e9Zk3mYfA6-l9fwxnHABG6M5E5HKQCgXdlkSqj-AogR1dNufO_kmlfkZwvDJOQoBuCcalvOEdBVEX9HkgWVhP3UuIcQ06SzbtwoQC_3Uaehbd9ja57hGHZd3EQI2ZKp9MvzwvvcYhY5lyF8k_UHUzc_Dc0hSUp_nZ0KTtwDmT5vSHjGqcSV_EwcXG0NsECmS7GhvfYYLW0dMxuoE0UkAtIYD6WliKo1gk2KOtKgFsvMzuUtg7l9t9jhVp9lQsMBWsKq7_Kz6joIGqZMPDCJ8lgWtYdksX4U2SnglvDmcRj51nYWil8temCfB6zuke1wCkYWovmG1H02pX1UKO4ICQk3mjZuQ38hnocLU_NR9sXGfqTZh763gOg0o7_pdbChSI8gSeMpCi6vNVtaTPZAyRCNXeSFZXHoiT48ElfGUQVnJ706fTXZo868Kx3BgRyj9z1iOy0DD0JfczQj36TfT_QspcF0wxOVF2zsVTfAn8JIpLIQLdaOKe5iLFjup16e7Ixc6TwA7jDIfxFbVv0ST7_Tpy1FZxzeWl5oeyckzB4QjFtAttuKFHelunYgnQey8BWkRfN9c0eI57YITATsaX433GVUnqnD5B6rnURX8CPNblDfnaIC6-XdOY7uoBEF3yLPg2JHQe3oDb22edDN6QZkbWDWtFDy5gzYgoPqr6VTLIGce6g3HFEA-Q24aV4qd8JgBIu6hFC9v-kvJZvtT243PzE9d9lVKl6Y-WbqvzU45FFB4788JGokUkHmFPIhSO2rJQlXoXSdtIdKqBEXEz7bJLOHeshvRk65Wb__5pznUfR0nHAoiHhN0CJcS8_jI87A4GQgsW_A6by_7MD8UC6NDP21YkFbLgrJ1PHYDoVlOPlcZc8nXtLrjihOmCSqc6vxbQE8B3QDPgUDVsgE0IjfNbH4ie-yK6FGMOPQN-tSrdz_480FWPm0BWIdcvHzRT3CufhHb5AN6uofCmZWkuSQE0sM5azmuKPQE0hT5tVswFNuX73EhKquBu5VhIDz0z6kGaW8WUaIkoRXr8UePIKWZIsuOWghoDL8unNg7PRxNrc='    

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="overnight", page_icon="📖", layout="wide")
    st.header("overnight")
    
    # Field for OpenAI API key.
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)

    # Retrieve user-selected openai model.
    model: str = st.selectbox("Model", options=MODEL_LIST)
        
    # If there's no openai api key, stop.
    if not openai_api_key:
        st.error("Please enter your OpenAI API key!")
        st.stop()
    
    # Create new form to search aitam library vector store.    
    with st.form(key="qa_form", clear_on_submit=False):
        query = st.text_area("**Query SDSURF Travel Policy 2024**")
        submit = st.form_submit_button("Query")
    # If submit button is clicked, query the aitam library.            
    if submit:
        # If form is submitted without a query, stop.
        if not query:
            st.error("Enter a question to search the library!")
            st.stop()            
        # Setup output columns to display results.
        answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        with st.spinner('Searching...'):
            response2 = client2.responses.create(
                instructions = INSTRUCTION,
                input = query,
                model = model,
                temperature = 0.6,
                tools = [{
                            "type": "file_search",
                            "vector_store_ids": [VECTOR_STORE_ID],
                }],
                include=["output[*].file_search_call.search_results"]
            )
        # Write response to the answer column.    
        with answer_col:
            st.markdown("#### Response")
            st.markdown(response2.output[1].content[0].text)
        # Write files used to generate the answer.
        with sources_col:
            st.markdown("#### Sources")
            # Extract annotations from the response
            annotations = response2.output[1].content[0].annotations
            # Get top-k retrieved filenames
            retrieved_files = set([response2.filename for response2 in annotations])   
            st.markdown(retrieved_files)
            st.markdown("#### Token Usage")
            st.markdown(response2.usage)

            response3 = response2.json()
            cost = response3['usage']['input_tokens'] * .1 / 10^6 + response3['usage']['output_tokens'] * .4 / 10^6
            formatted_cost = "${:,.4f}".format(cost)
            st.markdown(formatted_cost)
            
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')

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
import re

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
    INSTRUCTION_ENCRYPTED = b'gAAAAABof6jC28FjozJLLNjUdgMS5loA3arE9kWxx6wOYzudCPJC7kkMom8zayYcWZE7GvdfF3rLpm6oSBloBY0Udd-MdSekFwDkjoEfamzIzpHlB7OeCWR6xPTfXZsFdzsZpaEjItc0D2AUI_sXFtwSY8FJJXtOCEDul1wqP7n-x8CjDyrudtOGTUdsk0zreVdnjFRayc7e1stbUyLrOwGWxbXu7guUnBz9QMg4z860bjTnbmPim38yDyD3sCabHKoV6i1XpirRd_bnwobPHs1Fz5ZP7u4MxrJ26JmRARBhY2plN-swuabi7eg-hlHKVV8accXgBD0cAYlJ4POVBcDtL6Gx3hA1i-Hv6cI_jjn6ini-cBCQEXImm1Cl1BQx34nAAhgRmEvoae9SDKU5SE2hbkG_iP0Ju9igjogJ3zX97OGKvKdM3v-f-6BiFBQnkd_O0MrESYp8w1UO7T6Qyc8HOwCL6DmSv7vyf9xMCcyE6iuc6hqs3RpqsVvVrxCuGHhs-z-uc9MWZZ4iq23haO-uoA6-HuuzUy10G9mp2G_qkZl9fM6LnYlZ87gDulnLCOJX3hlPR3f4KYyCFYK_r8e8IwS_6m-S2tn0bgcYJhfC9uyqW6Ee6OsBZSryB0UtmMYlnxYxGPFZNRC_yI_hAkPESViBsR5hmrSZM3Rt0sif-u8kK_0RfdZkvsBIQDGh-oo6WOnYhHYvmGCtKWcTDVq3sYPsT6GtsnUR9EmCypHjGKV1FlZqgfqv75S9Fi20-WyQCc8TrvPrAmO0rIUs7C1xH8ZvNxQ-x6Jen7-0AXjTpQP_PoBCiGNWxa5mTVdDD6UYWetVw_XlMkdd6d1jIWrAolcS2ThhoiaTR-KS9XPEErw-Uvq4iOknFJRhTHmhpKAuxKsZ8CtqCTxfig3GsgriZJ59qkdxOJsLTCFWxTSTSGFahd1ZmNH2xY1KhjyYmMutL35ZKZxUTz5x9PNnpalC9h00u1rxRXsd7UE-GwGwzqgFPPzMhfg7oxq9K4M-bqWS9jK9tGCchQjAIu9wqYm2_1mmglDCkrzhqgDXz_0JwmuYyvjILnOxF_r_QY3NBNfivvexRsBHB5d4_yOGGRZ6wPx-y_huNCUlQgfP5NfzM4T4t5j5J81LpTfnytxGSc58g1Yup2foQRWEkF-IJL3oDf3MwTCSlvEwagpuF-ZnIW6ZbOzOcI5urrwWZ3vIupzfstqyO2qUxB4m-J3Iwkx_2X0vuZbbcK7W5Uwxh7uIWfQDTpIqBrJ27WtYWUxcunOocoq7FFUyG2euAcjlI0_m38kjQ-jU2YwP4h41sNEwjfZ7g0Hhm4k9UpzUtLLlP9aQ9lH_AmbeXCselnok8lQkMyXfXt5_3XbT5FH5VVn8TYjZcBGGPF2GQ0fxo0YaRhNMMYPjiI3j-BmI7ihhfgH-Vh7sSSy-wgd0dOZug7RRhOOz24e2KeHeDXAcLC1fO6dHkaAQ5CX3SNhjFoSilBeWHSFJDpQXl8JY5y4i1WgerbjQL2AivFR0pd2sigGUirUEjmvknQXtNnLXU2KyjnQbfAoNViizsRxM-hvrkoKXx0IX8psk1Hxp1cUm24cz7OJQrhmcVwCWcmVA4KR9mvp6zqg02oeNpXwzLleGfqUxyKjKjTZ0_O3SK8B91QwoRRxk0zktdMn-nlTHGVpvhuvEFodursp_h_c9OUNMFsOW41zyrDOM9IzG4maJMmnRcaXgBLzhOMpBGYBRwsUEG4spLcn1zR9sDcLariJex65JQ6kT8xJvuuGsHQhcWq9THNzePiAI-Rrgwb5UiIb-wGVnLIDfZqcQbBU3b_L1raGEfkXJ2iPYyee5VpPci259MVFrb4zG3r4utZltnMcItzjXxV1ZmPYT9he9Izqdc5D65FREdQOICKn4qOKOuayhvDgivswt9Pmpcu6_yOl_OM1d4tIkTuOwuL8xTrv8HgsV5vlFMf67H0Y67PRTt5ejkbD_iUKfOmrdLQUeCOI7i7tEbTMPf8GSeApbloQruerLruIowWfxAd8ugCcYLH51FhCX-7NUSAxREiElToBFdSdLORirXPScP4RB8itUSQ1-XQGYD9eT7pGmnB9dtKhPP6rKMmNIq_HHqGIknHGvPhyKG6nrwAscrzXST-xgO9db6hjzA759nHaNZPJn8BRNa8Lz9dWlPwVbqMHFihQyWFujZUnfM8CwYWmWQTqsVYp-MZMwAzn9Ku_Bs6Kh31xZtWT8yXtgtVNqGLP6nQsUmRA-TBtVtdscZucv9UKjOJM0LnuBfGHWXnL_iMgHbrFJEMSkJGoRRNvqstOkKoCvjn7FF8DFBS73WiwTkewSRTfKNZlnDZfUhQPJg13lzG1i6kNwc4iVfQJ5FjTrhg8ydmhRkta10xOOTqNOFi3QOzHwblkMMbUhu-7QlncjaWPIaxrfJwMKO9krj4_oKkvHaPWjXXG9aY3bF3kJtfZ5FCqm2RF5J6tgOgyB-TpE797n6Py4ghlhvFmqzEgU0xHgx0iEUVTj_82SfCXOVPhVZVEtvKIoof6-zml4bTWwVDGR2n6F65DjxGLy8v_-d00irzsKbf8ARlMeNo4AhVtcHyY4cMQNMihZEHOCSVuiv6PFl62FLrTrcTMyg1T8rFnjNU8hA3eD_Mgm-bVbITf8uA9tXYVTFPMtJC_mCIXnq4FkSr9wLwli7G-goscRc9GvZxG29NVeifQxHIo7DnKB-gVtMTaX_wR2FimtUUJokg3doGWmt-o_ffFyFP4faIrjQWZoZ2ja7067XZFnOqCmfi9qHVLwSo54VCigPia3_T_ojCY43wOIpUdMoxDcZ6wrXSbX9iWZt40zYCUWQrQlH9spMdRoCmkpP4deTEXN7QOmMcjWtZKGU_vN'    

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
            cleaned_response = re.sub('【.*?†source】', '', response2.output[1].content[0].text)
            st.markdown("#### Response")
            st.markdown(cleaned_response)
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

            # response3 = response2.json()
            # cost = response3['usage']['input_tokens'] * .1 / 10^6 + response3['usage']['output_tokens'] * .4 / 10^6
            # cost = response2.usage[0].input_tokens[0] * .1 / 10^6 + response2.usage[0].output_tokens[0] * .4 / 10^6
            # formatted_cost = "${:,.4f}".format(cost)
            # st.markdown(cost)
            
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')

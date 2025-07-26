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
    MODEL_LIST = ["gpt-4o-mini"] #, "gpt-4.1-nano", "gpt-4.1", "o4-mini"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    INSTRUCTION_ENCRYPTED = b'gAAAAABohSaD2pyUx5M4O1_woDT3Qht2OERqL2B91taCTlBewXfGK83Gx37iKaSAbfSrTHxAtBsXpo4tFqfJkxWDC-o56PMZvWZS-l-h8JJlOHb-lM_SjQsp8fBgHPH6fQwErwPA5CHQAvrROeCVtPECUynAqqAvrmHAa7GCW3MBfxUZhAlbHDHZxvtJ0DhJTbISF_yijkvM0jTO_v05A0z0WVAf35yCu8pK1WmzdjpNFX_RStuFHjHgF2mAODklcO1yh15Q3Ub0tXoS6jjUD5c6VCalY3DY8rqDpiBxSvy5dODY0eD6bmavKYOexdPrStF2vtJx6dPag4zUphchWw3kDuNTl88UMreQpWCCTJRhSpiS-_h2sUfni6iwyq5Bmhtr_qOMcCCNHV6CQnnj6ttA15c_Zbq8qTOkWuJXY0LPMI_mzAet07o8dH5w1b4wMKXNFKZqXVUNN3SveJRJNZ9q8p7ELLoKg1X-iFYkl7LwTQSTOo57gUTrZX-ejy95Jd8_fh4oPSoGtzDBPGud5DdMVemlKojO0xdZ6iS9x0cvPIpQMKjM6BluukcGKl38mTHFZaW_yIU1Jdf6FaAwpzNSQH2ys97WPdySWcd3-_k-dZ7o_9zbfb1uXeVyKi78zawwjfNtgTTC6VWgB3cdeq4w84IpL7KLdUaFgTFYH4LoYFSxLkxlYkV9K00lXks3pTV61Q4ZrDBxd9f3U9cXi2p_Pw_kac5ErkzMCtNWmBHsucLn_dZV8KBJW3nUTwGSorVrcorOLYaoL2jL8TBS3rHCnSIP_hgXf-YuBqmzQYgbSjeB-zdr4WNJ0JJTNkmaysDuOhhJ1mgJ48-kD7DUDI7gHAXh-tLbvXPK-WllX2xX0NN8jYfVpuS9RCjKHDRaq10ybYibvProihpzxlhRP1rJaJMhcJrKVsqzlsno0SWu-w_76ApNkNi39wt6egMTN1_XJqjFkGOLzIBV0UFv0w8sLEtOj9CZCwoR0NTfYFKYcnTpzaT204Wgp8iNux80_px7tMmhUzsptVXbGK7nXK2UJXFUSKDGvZCoJHjWqlGzopJAoh0FDIsCYVf9TGukwf8m-jxMQmpherRN4CMJ195S1sNwNs7IOemHO28n-5fo9TCDWl5M_4l8OOUcCzQIgEgYH_D6rb75bBoYbFWjx5y_8m4lWUc3hTHtZ6BBIsKghQzTVUdSc1P5XQjuaMFEGro7hdyvTmErewQqrF2nH7I2_5KL1nVW_t_ff2JddShI9AwNFGepSzx7pQeQnHtST0Uv5pqFl4iC66UZSemUie1-5sHfvXipOCkFzOF1LTtMPNogM5jw_Tja85oMjmc8krMx-GDaoz3YgchkZHGGvQI1xYkjX8fqUmEHk_6COjXiaUsS1PmTHv0soizXv-fzVMvrHbWDYcHD5ck1yrhlOm81pwraWiuCpRCXvCQTEBhav7nxNimeI-V0_gDeVaIsltUhHZ77D_qWrCVB_CJjUajAzF55H0YYkoZQxFeIlSaKjGaRbSDIKZIMzzar1fbHvPajmSPdRYM6ert8QSbydwlM4mNEaH3xGnGOT_nbNEy4aArZ1w_QALQ7ta-zMUEcBxYeUEJNt-nLz90J18YB7OnhapxsAC4PuKuE475BbgEKKOZsnkRUzBAe_hHtUFJM6LOS0Dpg05pKWAKqPfTjteYvNrcFW_I5_dwl9v3crG9EeggbHDzY4LbwsWaLfbUvQRMbjZNrfUnBqYpG9VOTPC-bDONXS3nhgsPrPQ6A8SH_ApIFEOP99irT4mhT69Z-KnHTfoQG4Ydw3BqrMBW9X8r1Ny139SJ2D-RaRjqtsrhthfJopXDdV48W1ycoIhPzJN5OqpGIWD_o_y2MkQZiYKyGd4zGawDiB9Ch63-gqJ4WFrMpLA6TxmyIIkofoe9-ZffON9YhEgBhFxd3KvgkQOOfUh9ekTy40xzCbQ6yLHXRbFaMeDAdRQMm3ujxvDTLqJwV886qlTDRrbdiw5hLl3I239BD96ddpFo9MzV3XUIGYNm4zxFwA25GpPIKSCS2kjndXcA3udm0bmpW9iHlmOfz0imm_gCGotE416mL6WO9DNH4CwtRDYea9QCz-8lI9FBsqVHcjg1Nmr32oA5zTSdJ4QkwGTpDY6S_X9miN8jaWDQoqlPr3zXp9akYHEfXp66BgtiB7DRiYp8BySS9gGx1BskUWupEZ5DthahxLXWuPAl_mHaBO7JGMVip9ujgzfOnnV7Tt9Biro6YDvAUPixgNDe4sQq3EIi5mqD71IEk-nqm7A-UNb4OOFpaXGRkx_wE9dZq2qjb6RpkGYluuhBahGR5aZ85YHgFhDd0RW5bmhfK11zXgS2jo00R8HhL8x61Xwd7MNR4KEvrAP5EWXif6Sj2_jAA-7KmtMy3OzbXswDcirsF835YCKWzYBRTUDRewfBEC1q-y1_gFt_cmvj5KJ0_C08OnTXeCBWdvGef_VKW3S0rTw6ufsQYdngnD6SIxmIlGN-wht2IuGa_kmZRLMRrNkjOOmqN6518tP92wBWXL3uS0jPUQpvDXSBLEdz3nueYBjesxJp2Yh-Bvm1uNl5nLnlvdcqAhgOh1X2OpsOLyDpYHgM-YL6lrwQF0NmzH5g9fYOgf3IYYhfGJAvkNX7eTPz7ZEzcG35NqbWsJ3QuIueoYrJmwUotsR7eQyr0R-Bx53olXKyoaHNnQcrgfsZqpKZevWvBMs9z-Zmy5dkOv1cj1raojclvtQeGzw9TPcPejicutlDBPIj1XpHAMc3_qvYvnbowR-p9mpHYeY1xix5qNxkIPddXT35UdpjKCDGbqawoLfhoHSYovoGHiqDnWR2CDPxFLlhvQjFpCsS2sq9yC6tlcMS8PXMxguKtSRZFckKBMFaxZQ_RlAvzE9W_pPy356e5xlPTrl2DVSjBMlTcY5-eT1rgJsaoRr06yrAVOp_f2emaPDM7hLEQ5dxHuLG7zepGcTRWOxoN9_tMzyMoKmSI2782qn1gAnDkE4kedjClmmWRRxMcK7XXx_pbrBXbRKHRgoXie97_eMDGtqtuAqG0UFd2JurssiE4adS9F301qXHQfULGodPHjey34OfTeXi2qb3fJtIvtMB6QDmSWEDraC_yZx3wnQuYqk9HBPGY2-t2l_TgBZMthbKLBfnvpQ=='

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
    with st.form(key="qa_form", clear_on_submit=False, height=300):
        query = st.text_area("**Query SDSURF Travel Policy 2024**", height="stretch")
        submit = st.form_submit_button("Query")
    # If submit button is clicked, query the aitam library.            
    if submit:
        # If form is submitted without a query, stop.
        if not query:
            st.error("Enter a question to search travel policies!")
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
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output[1].content[0].text)
            st.markdown("#### Response")
            st.markdown(cleaned_response)
        # Write files used to generate the answer.
        with sources_col:
            st.markdown("#### Sources")
            # Extract annotations from the response, and print source files.
            annotations = response2.output[1].content[0].annotations
            retrieved_files = set([response2.filename for response2 in annotations])
            file_list_str = ", ".join(retrieved_files)
            st.markdown(f"**File(s):** {file_list_str}")

            st.markdown("#### Token Usage")
            input_tokens = response2.usage.input_tokens
            output_tokens = response2.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            input_tokens_str = f"{input_tokens:,}"
            output_tokens_str = f"{output_tokens:,}"
            total_tokens_str = f"{total_tokens:,}"

            st.markdown(
                f"""
                <p style="margin-bottom:0;">Input Tokens: {input_tokens_str}</p>
                <p style="margin-bottom:0;">Output Tokens: {output_tokens_str}</p>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"Total Tokens: {total_tokens_str}")

            if model == "gpt-4.1-nano":
                input_token_cost = .1/1000000
                output_token_cost = .4/1000000
            elif model == "gpt-4o-mini":
                input_token_cost = .15/1000000
                output_token_cost = .6/1000000
            elif model == "gpt-4.1":
                input_token_cost = 2.00/1000000
                output_token_cost = 8.00/1000000
            elif model == "o4-mini":
                input_token_cost = 1.10/1000000
                output_token_cost = 4.40/1000000

            cost = input_tokens*input_token_cost + output_tokens*output_token_cost
            formatted_cost = "${:,.4f}".format(cost)
            
            st.markdown(f"**Total Cost:** {formatted_cost}")
            
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')

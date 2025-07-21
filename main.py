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
    INSTRUCTION_ENCRYPTED = b'gAAAAABofk51ITzUXBBnTqAnvxVOuIo-vMayvLO7r3KgKrymkIOQNrRoUkBzjnq4__mVgWrzRNMcSqnDJ9hbUdeIcN9-YH0IGzKtVPfa9yPmRBXE_TIGFr0eEE1Ub4hMvvjGrKeaTXymw8UEtJvmCQAxT5sffthrfm8kqQiTcNDuqSQT_9lSHYKQxOtRxEWf7ZmItQp8jTNFxikV2SnlUYPVRy-v3IVY5horMwiE_nqXJ7k9Jthzob1j2kHkAhxSXGe-3gtsqxto6McoZ447b78g9Wr5eqTA6bCC_EmOV8mvzAjdD7XFiuKcXKqlS2wX4a74N4yOsma-_vThGzEHRvAZXPCAQa-gFvvoBl61YEQPfwzF7Gf23hWe1Pv8K3iKUJPOj2I5JQDFYrOLOQmB3nuSPelV7jMFy9tOyP-jPUyiKiB9Ew8EiI08cVxNK4UNzwqQeKXJmriGapKdUE1xcdanNYmNgWoFJUISYMdOh6ZSEnJRVB7mZ7L6Q_xsI7QrGSalUGBNm_3gGqHudwg5fnbS7t2ocFYs7k3sSIGr5qRAG4E4a16lIj7MAuW5V1FcAEl5nwmIQNeANHlOR-3sYgC6pEl4UtDMfGtwNnpnK5YeaO-pthWz7dpoms9aA7NoY_sTR4spCV_z2YBvo-dFYp43OHAm4to5GKAnY2VU9D8Xa9Ge-QUllB70G3YOFxEH0kuWIfINbRhyDNJijwzMx4bgImuXaPRgJOwRzir-GHlkSl30uLqhQbXixsjFoyVefujOLSQMebKcsBpsRXqrLJjTESXnawxTUoH3FD0PRdFH_nC9olBDjfq0xZbniGeSOgGx5b94ZD14AfR2qE6vRriYXDUj_2sLnux50t_QhE10e_rDxVE31rmsSb_ai1f76q7FCg6MdLSe3RNjR9GEDVAh9wAiL7uOUQGHhnJ30fnui7Do1iMv8ObNACdSqjAZfnTvuR9g058koBYOPuOLIKLQZT4O0IE-uhxtu5YwqJviEkasiXvlEyBapnLqRRxk61Arvc1c_haOecPlGLl0UbNEhmpDr_sSNUAbOgNtMgrZf-SppiqC9v-LBELymc2WCIbAou9gsYvEmT2XF2vb1giylE4Ca_pyy3nYpbY6I9R3DvmE2aU2w_b1t3T9JQmWps89BrkwqpqwzFq1mi0E4VHL4JQcZ08MqDnMBTI6FC0T5S-NKpCUxJVnooD5avotU2dbH5b6pjTI_tGSzxmUNc57QxOVW0PRPivniOb5QVi6JldQ68cIQ8whPjrBqCYAGKdwIleVvoJ1KEU61Dek1XWMc5KIs4HScSvApEH7nTdSTIIMX-m-Mb09Wrd2ZbDYtXHDQKzLFUli-4_XA-pKbAyz8eXMPzXIJw4Pnu3xNm3FRsb_03du1Uxpvgd_ThU1QaSAICWooJOWF30YTVYVhWQlqcQijd_0R5tc17GzjzKvkp-w9SZ0UfbmY4Z1y7zlNTbOXYJf4_gjiqw8w48ZQLUbbB72nejbeXZr6AnxrP9jniyOVAdB9g5BhfO1YFzJpZ3hpR8KbLoEOu1ecxNEatdIRE7D4_gLIXY-qED0OMulD5ITuCMVCt0f6QFxQ3AdZ5VrHKmFjiGa9rMrC0IVgvs3fgxErVXOdcg8VicVsFlKBAr5qiSWuYQKfJDSzgl6zPCRRPxxKK3lxJKlB5v1W4wqtNfkRSi5uy3dN2NpXRA29rie7Id9Noh_wAsZ2Yh9M4264utzrY0Rhl4KzZZcrsoAEuwOBa55cba9bw32QbX0OUVp5_dDThUjAkrRWZPDwBCpLmGmO_3mGNKHizPjaoJUFOI8q6dooBTR6AZwtcUbKOcxEICvQudwlbEabikgThMzP3IPsh6Uzv0dRaqGi0XiMOg3F_G5Y9AHEODV4GzrBWyx9XQMvnJLkHtioPzQU59oxRLH69o4Td8IlPc6MMjJ3ng9uGOB3W3Jz9remrW0X6rBI8EkHAVEAuCWSC5uQQdQdaHX60lNHyVuDMA0-tGSh-zCg47IwOuUWF8VQdaP0uHkFG-i7nPATKffdz8p51S6iBdv7kxOV6iGxx_RE8MTKwwth46rAoN_yNoNNjQ7HJwWfCxo4wOj12SLhNlnL0UnQb29VYnzL2NMXqbVPwLaXgNwjlA9kAfn3qAL1vnYC-jqnQbhOqKswhvwg8le2XL_k78NX24g0uH8J23wOBLkwGpOhvij_onbA_DrDY3KH2xa-UsW37h4g3aA6Zi-mehExp5EKyZpB7mAcQw8Y0ACmHr2V7aUlM2HDbY4pypfU0LVyIWBHq5eqLw7cr3dT6TBCwu6ZmhiU9Hyo9e98SWHXitOl1CghMPv32GMEbUdL1whT2C_hC_nt_z7YlS10B9mD4Rsd9GvMkz_tqTidNLZDg59RRAtjFolgo8ouiUtVtuCMvk-RtSxIpL4tTFE7S08-fru-9ppZ6BAApUmwHLyS93oUt_97kUZyq3dKtc2zHZ1HOOd1WdjCBizIEfEmt2yxI8qK0yj3V4A9P37kAQe2-BnoiweisAgqJSgo_-_Ig21H5Jt0XdU4-PjlVGzZddlHZgEHlP4v8jTZMmAI3uyCh2sg_7VUjzKoudGt8RJyOJAC69euZFIJGVtJ5R3i3Z5QymLkvGPVyyE-Mi1AZO1SbRD9GAQtlKiqttiaPXgpORIszb2JkM='    

    key = st.secrets('INSTRUCTION_KEY')
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
                temperature = 0.3,
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

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')

import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
import os
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
    
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
    MODEL_LIST = ["gpt-4.1-nano", "gpt-4o-mini", "gpt-4.1", "o4-mini"]
    VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    INSTRUCTION = INSTRUCTION = """
    
    #Primary Purpose

    The chatbot is designed to assist users by answering questions specifically about the company’s travel policy. All responses must be derived from the travel policy document stored in the vector database to ensure accuracy and consistency.

    #Response Guidelines

    ##Source-Based Answers Only

    All answers about the travel policy must be grounded in the content of the vector store.

    If the answer is not found in the document, the chatbot should respond with:
    "I'm not able to find that information in the company's travel policy."

    ##Uncertain or Incomplete Information

    If the chatbot is unsure or the information is ambiguous, it should say:
    "I'm not completely certain about that based on the available information. You may want to confirm with the appropriate department."

    #Answer Format

    Responses should be concise but complete, written in paragraph form, and easy to understand.

    #Other Company Topics

    The chatbot may respond to questions about other company-related topics (e.g., HR, IT, Legal, Payroll, Accounts Payable), but: Responses must be measured and cautious; and, The chatbot should consider the perspectives of multiple departments and avoid making assumptions.

    If the topic is outside the chatbot’s scope or lacks sufficient information, it should respond with:
    "That may involve multiple departments. I recommend reaching out to the appropriate team for a more complete answer."

    #External or Non-Company Topics

    The chatbot should politely decline to answer questions unrelated to the company or its policies.

    Example response:
    "I’m here to help with questions about the company and its policies. I’m not able to provide information on that topic."
    
    """
    
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
        with st.spinner('Calculating...'):
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

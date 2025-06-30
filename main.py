import streamlit as st
import openai
from openai import OpenAI
import os
import pandas as pd
import openpyxl
import tiktoken
import json
import time

def wait_on_run(client, run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def get_response(client, thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def generate_response(filename, openai_api_key, model, query_text):    
    # Load document if file is uploaded
    if filename is not None:
        client = OpenAI(api_key=openai_api_key)
        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=query_text
        )
        
        file = client.files.create(
            file=open(filename, "rb"),
            purpose="assistants"
        )

        vector_store = client.vector_stores.create(
            name="matia"
        )
        
        TMP_VECTOR_STORE_ID = str(vector_store.id)
        TMP_FILE_ID = str(file.id)
                        
        batch_add = client.vector_stores.file_batches.create(
            vector_store_id=TMP_VECTOR_STORE_ID,
            file_ids=[TMP_FILE_ID]
        )

        # Update Assistant
        assistant = client.beta.assistants.update(
            MATH_ASSISTANT_ID,
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search":{
                    "vector_store_ids": [TMP_VECTOR_STORE_ID]
                }
            }
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        run = wait_on_run(client, run, thread)
        messages = get_response(client, thread)
        
    return messages, TMP_FILE_ID, TMP_VECTOR_STORE_ID, client, run, thread

def delete_vectors(client, TMP_FILE_ID, TMP_VECTOR_STORE_ID):
    # Delete the file and vector store
    deleted_vector_store_file = client.vector_stores.files.delete(
        vector_store_id=TMP_VECTOR_STORE_ID,
        file_id=TMP_FILE_ID
    )

    deleted_vector_store = client.vector_stores.delete(
        vector_store_id=TMP_VECTOR_STORE_ID
    )

def disable_button():
    st.session_state.disabled = True        

# Model list, Vector store ID
MODEL_LIST = ["gpt-4.1-nano", "gpt-4o-mini", "gpt-4.1", "o4-mini"]
VECTOR_STORE_ID = "vs_6858ab8cb9e881919572b5b2f09669df"
MATH_ASSISTANT_ID = "asst_CE2FhokCAd4uD9uQhybDGFoX"

st.set_page_config(page_title="matia1", page_icon="📖", layout="wide")
st.header("matia1")

api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="Paste your OpenAI API key here (sk-...)",
        help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
        value=os.environ.get("OPENAI_API_KEY", None) or st.session_state.get("OPENAI_API_KEY", "")
    )

st.session_state["OPENAI_API_KEY"] = api_key_input

openai_api_key = st.session_state.get("OPENAI_API_KEY")
model: str = st.selectbox("Model", options=MODEL_LIST)

with st.expander("Advanced Options"):
    doc_ex = st.checkbox("Upload Excel file for examination")

if doc_ex:
    # File uploader for Excel files
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"], key="uploaded_file")

    if uploaded_file:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df['combined_text'] = df.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
        json_string = df.to_json(path_or_buf=None)
        serialized_data = json.dumps(json_string, indent=4)
        
        with open("temp.txt", "w") as file:
            file.write(serialized_data)
        file.close()

        if not openai_api_key:
            st.error("Please enter your OpenAI API key!")
            st.stop()
    
        # Form input and query
        with st.form("doc_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                submit_doc_ex = st.form_submit_button("Submit File", on_click=disable_button)
            with col2:
                delete_file = st.form_submit_button("Delete Vectors", on_click=disable_button)
            query_doc_ex = st.text_area("**Document Examination**")
            submit_doc_ex_form = st.form_submit_button("Doc-Ex Submit")
            
            if not openai_api_key:
                st.error("Please enter your OpenAI API key!")
                st.stop()
            
            if submit_doc_ex and doc_ex:
                query_text = "I need your help analyzing the document temp.txt."
                
                with st.spinner('Calculating...'):
                    (response, TMP_FILE_ID, TMP_VECTOR_STORE_ID, client, run, thread) = generate_response("temp.txt", openai_api_key, model, query_text)
                
                st.write("*Matia is an AI-driven platform designed to review and analyze documents. The system continues to be refined. Users should review the original file and verify the summary for reliability and relevance.*")
                st.write("#### Summary")
                i = 0
                for m in response:
                    if i > 0:
                        st.markdown(m.content[0].text.value)
                    i += 1

                submit_doc_ex = False
                delete_vectors(client, TMP_FILE_ID, TMP_VECTOR_STORE_ID)

if submit_doc_ex_form and not delete_file:                    
    with st.spinner('Calculating...'):
        (response, TMP_FILE_ID, TMP_VECTOR_STORE_ID, client, run, thread) = generate_response("temp.txt", openai_api_key, model, query_doc_ex)

    st.write("*Matia is an AI-driven platform designed to review and analyze documents. The system continues to be refined. Users should review the original file and verify the summary for reliability and relevance.*")
    # st.write("#### Summary")
    for m in response:
        st.markdown(m.content[0].text.value)

    submit_doc_ex_form = False
    delete_vectors(client, TMP_FILE_ID, TMP_VECTOR_STORE_ID)
                                
    # st.write(response.output_text)
    # st.write(response.output[1].content[0].text)

if not openai_api_key:
    st.error("Please enter your OpenAI API key!")
    st.stop()
    
with st.form(key="qa_form", clear_on_submit=False):
    query = st.text_area("**Matia Library**")
    submit = st.form_submit_button("Library Submission")
            
if submit:
    if not query:
        st.error("Enter a query!")
        st.stop()
            
    # Output Columns
    answer_col, sources_col = st.columns(2)

    client2 = OpenAI(api_key=openai_api_key)
    with st.spinner('Calculating...'):
        response2 = client2.responses.create(
            input = query,
            model = model,
            temperature = 0.3,
            tools = [{
                        "type": "file_search",
                        "vector_store_ids": [VECTOR_STORE_ID],
            }],
            include=["output[*].file_search_call.search_results"]
        )
    
    with answer_col:
        st.markdown("#### Response")
        st.markdown(response2.output[1].content[0].text)

    with sources_col:
        st.markdown("#### Sources")
        
        # Extract annotations from the response
        annotations = response2.output[1].content[0].annotations
        
        # Get top-k retrieved filenames
        retrieved_files = set([response2.filename for response2 in annotations])   
        
        st.markdown(f'Files used: {retrieved_files}')    

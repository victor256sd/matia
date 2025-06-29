import streamlit as st
import os
import pandas as pd
import openpyxl
import tiktoken
import openai
from openai import OpenAI
import json
import requests


MATH_ASSISTANT_ID = assistant.id  # or a hard-coded ID like "asst-..."

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<your OpenAI API key if not set as env var>"))

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

assistant = client.beta.assistants.update(
    MATH_ASSISTANT_ID,
    tools=[{"type": "code_interpreter"}],
)
show_json(assistant)

thread, run = create_thread_and_run(
    "Generate the first 20 fibbonaci numbers with code."
)
run = wait_on_run(run, thread)
pretty_print(get_response(thread))

run_steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id, run_id=run.id, order="asc"
)

# Update Assistant
assistant = client.beta.assistants.update(
    MATH_ASSISTANT_ID,
    tools=[{"type": "code_interpreter"}, {"type": "file_search"}],
    tool_resources={
        "file_search":{
            "vector_store_ids": [vector_store.id]
        },
        "code_interpreter": {
            "file_ids": [file.id]
        }
    },
)



def generate_response(filename, openai_api_key, model, query_text):
    # Load document if file is uploaded
    if filename is not None:
        client = OpenAI(api_key=openai_api_key)

        # MAX_CHUNK_SIZE = 200
        # CHUNK_OVERLAP = 100
        # st.write("Chunk Size/Overlap: ",MAX_CHUNK_SIZE,"/",CHUNK_OVERLAP)
        
        file = client.files.create(
            file=open(filename, "rb"),
            purpose="user_data"
        )

        vector_store = client.vector_stores.create(
            name="matia"
        )
        
        TMP_VECTOR_STORE_ID = str(vector_store.id)
        TMP_FILE_ID = str(file.id)
                        
        batch_add = client.vector_stores.file_batches.create(
            vector_store_id=TMP_VECTOR_STORE_ID,
            file_ids=[TMP_FILE_ID],
            # chunking_strategy=[{
            #     "type": "static",
            #     "static": {
            #         "max_chunk_size_tokens": MAX_CHUNK_SIZE,
            #         "chunk_overlap_tokens": CHUNK_OVERLAP
            #     }
            # }]
        )
            
        #     {
        #     "vector_store_id": TMP_VECTOR_STORE_ID,
        #     "file_ids": TMP_FILE_ID,
        #     "chunking_strategy": {
        #         "type": "static",
        #         "static": {
        #             "max_chunk_size_tokens": MAX_CHUNK_SIZE,
        #             "chunk_overlap_tokens": CHUNK_OVERLAP
        #         }
        #     }
        # })
        
        response = client.responses.create(
            input = query_text,
            model = model,
            temperature = 1,
            tools = [{
                "type": "file_search",
                "vector_store_ids": [TMP_VECTOR_STORE_ID],
            }]
        )

        # Delete the file and vector store
        deleted_vector_store_file = client.vector_stores.files.delete(
            vector_store_id=TMP_VECTOR_STORE_ID,
            file_id=TMP_FILE_ID
        )

        deleted_vector_store = client.vector_stores.delete(
            vector_store_id=TMP_VECTOR_STORE_ID
        )
        
        # try:
        #     url = f"https://api.openai.com/v1/files/{TMP_FILE_ID}"
        #     del_response = requests.delete(url, headers=headers)
        #     del_response.raise_for_status()            
        #     return response
            
        # except Exception as e:
        #     return response

    return response

# Model list, Vector store ID
MODEL_LIST = ["gpt-4.1-nano", "gpt-4o-mini", "gpt-4.1", "o4-mini"]
VECTOR_STORE_ID = "vs_6858ab8cb9e881919572b5b2f09669df"

st.set_page_config(page_title="matia2", page_icon="📖", layout="wide")
st.header("matia2")

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
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

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
        with st.form("doc_form", clear_on_submit=True):
            submit_doc_ex = st.form_submit_button("Submit File")
    
            if not openai_api_key:
                st.error("Please enter your OpenAI API key!")
                st.stop()
            
            if submit_doc_ex and doc_ex:
                with st.spinner('Calculating...'):
                    response = generate_response("temp.txt", openai_api_key, model, template_prompt)
                st.write("[The summary may not always reflect the most current or precise information. Users are encouraged to review the original file and verify the data independently to ensure its reliability and relevance.]\n")
                st.write("Summary: ")
                st.write(response.output_text)
                # st.write(response.output[1].content[0].text)
    
if not openai_api_key:
    st.error("Please enter your OpenAI API key!")
    st.stop()
    
with st.form(key="qa_form"):
    query = st.text_area("Ask a question...")
    submit = st.form_submit_button("Submit")
            
if submit:

    if not query:
        st.error("Please enter a question!")
        st.stop()
            
    # Output Columns
    answer_col, sources_col = st.columns(2)

    client2 = OpenAI(api_key=openai_api_key)
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
        retrieved_files = set([response2.filename for response in annotations])   
        
        st.markdown(f'Files used: {retrieved_files}')    

import streamlit as st
from streamlit_chat import message
import time
from streamlit.runtime.scriptrunner import get_script_run_ctx
# made by Debanka Das - https://github.com/erdebankadas; also follow my page - https://fossbyte.in/

from functools import wraps
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
import tempfile
import json

# Collect API key securely from environment variable
user_api_key = st.sidebar.text_input(
    label="#### Your OpenAI API key ",
    placeholder="Paste your openAI API key, sk-",
    type="password",
    help="Ensure you've set the OPENAI_API_KEY environment variable."
)

uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")
# made by Debanka Das - https://github.com/erdebankadas; also follow my page - https://fossbyte.in/

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8")
    data = loader.load()
    # made by Debanka Das - https://github.com/erdebankadas; also follow my page - https://fossbyte.in/

    # Create embeddings with the API key
    embeddings = OpenAIEmbeddings(openai_api_key=user_api_key)
    vectors = FAISS.from_documents(data, embeddings)

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo', openai_api_key=user_api_key),
        retriever=vectors.as_retriever()
    )

    def conversational_chat(query):
        result = chain({"question": query, "chat_history": st.session_state['history']})
        st.session_state['history'].append((query, result["answer"]))
        update_memory(query, result["answer"])  # Update memory with new information
        return result["answer"]

    # Load memory from file or initialize empty
    # made by Debanka Das - https://github.com/erdebankadas; also follow my page - https://fossbyte.in/
    memory = load_memory() or {}

    def update_memory(query, answer):
        """Updates the memory with the new query and answer."""
        memory[query] = answer
        save_memory(memory)  # Save updated memory to file

    def load_memory():
        """Loads memory from a file if it exists."""
        try:
            with open("chat_memory.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_memory(memory):
        """Saves memory to a file."""
        with open("chat_memory.json", "w") as f:
            json.dump(memory, f)

    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Hello ! Ask me anything about " + uploaded_file.name + " "]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hey ! "]

    # Container for the chat history
    response_container = st.container()
    # Container for the user's text input
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):

            user_input = st.text_input("Query:", placeholder="Talk about your csv data here (:", key='input')
            submit_button = st.form_submit_button(label='Send')

            if submit_button and user_input:
                output = conversational_chat(user_input)

                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                message(st.session_state["generated"][i], key=str(i), avatar_style="thumbs")
                # made by Debanka Das - https://github.com/erdebankadas; also follow my page - https://fossbyte.in/


def add_session_state_lock(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            report_ctx = get_script_run_ctx()  # Assign report_ctx outside try block
        except RuntimeError:  # Optionally handle potential errors
            pass  # Or log a warning, etc.
        try:
            if report_ctx:
                report_ctx.session_state_lock.acquire()
            return func(*args, **kwargs)
        finally:
            if report_ctx:
                report_ctx.session_state_lock.release()
    return wrapper


@add_session_state_lock
def update_data_scheduler():
    while True:
        try:
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    # Replace with your actual data fetching and writing logic
                    # ... (fetch and write updated data to tmp_file) ...
                    tmp_file_path = tmp_file.name
                    # made by Debanka Das - https://github.com/erdebankadas; also follow my page - https://fossbyte.in/

                loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8")
                data = loader.load()

                # Update embeddings and vectors
                embeddings = OpenAIEmbeddings(openai_api_key=user_api_key)
                vectors = FAISS.from_documents(data, embeddings)
                chain.retriever = vectors.as_retriever()  # Update the chain's retriever

                st.session_state['generated'].append(f"Data has been updated with the latest information!")
            else:
                st.session_state['generated'].append("No CSV file uploaded yet.")
        except Exception as e:
            st.session_state['generated'].append(f"Error updating data: {str(e)}")
        finally:
            time.sleep(60 * 5)  # Update every 5 minutes

# Start the scheduler in a separate thread
import threading

threading.Thread(target=update_data_scheduler, daemon=True).start()
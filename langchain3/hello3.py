import streamlit as st
from pathlib import Path
from streamlit_chat import message
# from streamlit_chat import message, st_chat
# from langchain.document_loaders import CSVLoader
from langchain_community.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI 
from langchain_openai import OpenAIEmbeddings, OpenAI 
from sqlalchemy.engine import URL
import os
import apscheduler.schedulers.background as BackgroundScheduler

# Memory storage
memory = {}

def access_memory(key):
    if key in memory:
        return memory[key]
    else:
        return None

def update_memory(key, value):
    memory[key] = value

def extract_key_details(text):  # Replace with your extraction logic
    # Implement your extraction method here
    return key_details  # Return extracted details

# Prompt for OpenAI API key manually
openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")

os.environ["OPENAI_API_KEY"] = openai_api_key

st.title('CSV Question and Answer ChatBot')

csv_file_uploaded = st.file_uploader(label="Upload your CSV File here")

if csv_file_uploaded is not None:
    def save_file_to_folder(uploadedFile):
        save_folder = 'content'
        save_path = Path(save_folder, uploadedFile.name, encoding="utf-8")
        with open(save_path, mode='wb') as w:
            w.write(uploadedFile.getvalue())

        if save_path.exists():
            st.success(f'File {uploadedFile.name} is successfully saved!')

    save_file_to_folder(csv_file_uploaded)

    loader = CSVLoader(file_path=os.path.join('content/', csv_file_uploaded.name))
    index_creator = VectorstoreIndexCreator()
    docsearch = index_creator.from_loaders([loader])
    chain = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.vectorstore.as_retriever(), input_key="question")

    def update_csv_data():
        try:
            # Implement your data update logic here:
            # - Download or fetch new data
            # - Process and prepare the data
            # - Write the updated data to the CSV file
            # Example:
            # download_new_data()
            # process_data()
            # write_to_csv(file_path=os.path.join('content/', csv_file_uploaded.name))

            # Reload the CSVLoader, index, and chain:
            global loader
            global docsearch
            global chain
            loader = CSVLoader(file_path=os.path.join('content/', csv_file_uploaded.name))
            index_creator = VectorstoreIndexCreator()
            docsearch = index_creator.from_loaders([loader])
            chain = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.vectorstore.as_retriever(), input_key="question")

            st.info("CSV data updated successfully!")
        except Exception as e:
            st.error("Error during data update:", e)

    scheduler = BackgroundScheduler()
    scheduler.add_job(update_csv_data, 'interval', minutes=30)  # Adjust interval as needed
    scheduler.start()

    st.on_session_end(scheduler.shutdown)

    # Chatbot interface
    st.title("Chat with your CSV Data")

    # Create the chat interface using st_chat():
    st_chat()  # Add this line to create the chat widget

        # Storing the chat
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []


    def generate_response(user_query):
        response = chain({"question": user_query})
        return response['result']
    
    
    # We will get the user's input by calling the get_text function
    def get_text():
        input_text = st.text_input("You: ","Ask Question From your Document?", key="input")
        return input_text
    user_input = get_text()

    if user_input:
        output = generate_response(user_input)
        # store the output 
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)
    
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
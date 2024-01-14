import os
import openai  # Import the openai module
from langchain_experimental.agents import create_csv_agent
from langchain_community.llms import OpenAI
import streamlit as st
import tabulate
import time
import schedule  # Import the schedule library

# Directly set the OpenAI API key here (replace with your actual key)
OPENAI_API_KEY = ""

# Interval for automatic data updates (in seconds)
UPDATE_INTERVAL = 3600  # Update every hour

# Initialize conversation memory
memory = []

def update_data():
    try:
        # Implement your data update logic here
        # Fetch new data from the source and update the CSV file
        st.info("Updating data...")
        # (Replace this placeholder with your actual data update process)
        time.sleep(2)  # Simulate data update time
        st.success("Data updated successfully!")
    except Exception as err:
        st.error("An error occurred during data update:")
        st.write(err)

def main():
    st.set_page_config(page_title="Ask your CSV")
    st.header("Ask your CSV")

    csv_file = st.file_uploader("Upload a CSV file", type="csv")
    if csv_file is not None:
        try:
            agent = create_csv_agent(OpenAI(temperature=0.7, api_key=OPENAI_API_KEY, verbose=True), csv_file, verbose=True)

            user_question = st.text_input("Ask a question about your CSV: ")
            if user_question is not None and user_question != "":
                with st.spinner(text="In progress..."):
                    try:
                        # Include conversation history in prompt
                        prompt = f"Conversation history:\n{tabulate.tabulate(memory, headers=['User', 'Agent'], tablefmt='plain')}\n\nUser: {user_question}"
                        response = agent.invoke(prompt)
                        st.write(response)

                        # Store interaction in memory
                        memory.append({"User": user_question, "Agent": response})

                        time.sleep(1)  # Introduce a delay to avoid hitting rate limits
                    
                    except Exception as err:
                        st.error("An error occurred:")
                        st.write(err.response)
        except Exception as err:
            st.error("An error occurred during agent creation:")
            st.write(err)
       

# Schedule the data update function
schedule.every(UPDATE_INTERVAL).seconds.do(update_data)

if __name__ == "__main__":
    main()

    # Run the scheduler in the background
    while True:
        schedule.run_pending()
        time.sleep(1)
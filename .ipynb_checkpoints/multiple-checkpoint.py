from langchain.agents import create_pandas_dataframe_agent
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import pandas as pd
import chainlit as cl
import io
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

open_ai_key = "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"

# Create an OpenAI object.
llm = OpenAI(openai_api_key=open_ai_key)

def create_agent(data: SmartDataframe, llm):
    # Create a Pandas DataFrame agent.
    return create_pandas_dataframe_agent(llm,
                                         data,
                                         verbose=True)

@cl.on_chat_start
async def on_chat_start():
    elements = [cl.Image(name="image1", display="inline", path="./robot.jpeg")]
    await cl.Message(content="Hello there, Welcome to AskAnyQuery related to CSV Data!").send()

@cl.on_message
async def respond_to_user_message(message: str):

    # Get data from user session
    dfs = cl.user_session.get('data')
    print(dfs)

    # List to store responses
    responses = []

    # Loop through each DataFrame and process
    for df in dfs:
        # Agent creation
        agent = create_agent(df, llm)

        with get_openai_callback() as cb:
            # Run model
            response = agent.run(message)
            print(cb)  # Print cost incurred

        responses.append(response)

    # Send a response back to the user
    await cl.Message(
        content="\n".join(responses),
    ).send()

# Function to process uploaded CSV files and store them in the user session
def process_uploaded_csv_files(files):
    dfs = []

    for file in files:
        csv_file = io.BytesIO(file.content)  # Store file in memory as bytes
        df = pd.read_csv(csv_file, encoding="utf-8")
        dfs.append(df)

    return dfs

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Hello there, Welcome to AskAnyQuery related to CSV Data!").send()

@cl.on_message
async def respond_to_user_message(message: str):

    if cl.user_session.is_empty('data'):
        files = None

        # Waits for the user to upload CSV data
        while files is None:
            files = await cl.AskFileMessage(
                content="Please upload a CSV file to begin!", accept=["text/csv"], max_size_mb=100
            ).send()

        # Process and store uploaded CSV files in the user session
        dfs = process_uploaded_csv_files(files)

        # Store data in the user session
        cl.user_session.set('data', dfs)

        # Send a response back to the user
        await cl.Message(
            content="CSV file(s) uploaded! You can now ask me anything related to your CSV data."
        ).send()
    else:
        # User has already uploaded data, so respond to their query
        respond_to_user_message(message)

# # Initialize the ChainLit application
# cl.init()

# # Run the ChainLit application
# cl.run()

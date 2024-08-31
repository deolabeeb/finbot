
from langchain.agents import create_pandas_dataframe_agent
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback

import pandas as pd
import chainlit as cl
import io


# Create an OpenAI object.
llm = OpenAI(openai_api_key=open_ai_key)

def create_agent(data: str, llm):
    # Create a Pandas DataFrame agent.
    return create_pandas_dataframe_agent(llm,
                                         data,
                                         verbose=True,
                                         )

@cl.on_chat_start
async def on_chat_start():
    elements = [cl.Image(name="image1", display="inline", path="./robot.jpeg")]
    await cl.Message(content="Hello there, Welcome to AskAnyQuery related to CSV Data!", elements=elements).send()


    files = None
    # Waits for user to upload csv data
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload a csv file to begin!", accept=["text/csv"], max_size_mb= 100
        ).send()

    # load the csv data and store in user_session
    file = files[0]
    csv_file = io.BytesIO(file.content) # Store file in memory as bytes
    df = pd.read_csv(csv_file, encoding="utf-8")

    # creating user session to store data
    cl.user_session.set('data', df)

    # Send response back to user
    await cl.Message(
        content=f"`{file.name}` uploaded! Now you ask me anything related to your csv"
    ).send()

@cl.on_message
async def respond_to_user_message(message: str):

    # Get data
    df = cl.user_session.get('data')
    print(df)

    # Agent creation
    agent = create_agent(df, llm)

    with get_openai_callback() as cb:
        # Run model
        response = agent.run(message)
        print(cb) # Print cost incurred

    # Send a response back to the user
    await cl.Message(
        content=response,
    ).send()

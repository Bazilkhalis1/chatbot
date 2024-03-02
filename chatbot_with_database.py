import os
from openai import OpenAI
import gradio as gr
import mysql.connector


# Set your MySQL database connection details
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'chatbot_db'  # Replace with your database name
}

#connecting to database
def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Failed to connect to database: {err}")
        return None

def save_chat_to_database(user_input, ai_response):
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = "INSERT INTO chat_history (user_input, ai_response, timestamp) VALUES (%s, %s, NOW())"
        cursor.execute(query, (user_input, ai_response))
        connection.commit()
        cursor.close()
        connection.close() 

client = OpenAI()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_gpt(user_prompt):
    # Craft a more engaging, conversational prompt
    conversation_prompt = f"The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: {user_prompt}\nAI:"
    
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",  # Adjust based on your preference or requirements
        prompt=conversation_prompt,
        max_tokens=150,
        temperature=0.9,  # Adjust for more varied, human-like responses
        stop=["\n", " Human:", " AI:"],  # Stop generating further when hitting these patterns
    )
    ai_response = response.choices[0].text.strip()

    # Save the chat to the database
    save_chat_to_database(user_prompt, ai_response)
    
    return ai_response

if __name__ == "__main__":
    demo = gr.Interface(
        fn=chat_with_gpt,
        inputs=gr.Textbox(lines=2, placeholder="Type your message here...", label="Your Message"),
        outputs=gr.Textbox(label="AI Response"),
        title="GPT-based Chatbot",
        description="This is a chatbot powered by OpenAI's GPT. Type something to start chatting! The AI is designed to respond like a human being.",
        allow_flagging = "never"
    )
    demo.launch()
 
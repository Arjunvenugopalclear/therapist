import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_gpt_response(user_input: str) -> str:
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-realtime-preview",
            messages=[
                {"role": "system", "content": "You are a helpful and empathetic digital therapist. Provide supportive and insightful responses to the user's input."},
                {"role": "user", "content": user_input}
            ]
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned an empty response.")
        return content
    except Exception as e:
        print(f"Error in getting GPT response: {e}")
        return "I'm sorry, I'm having trouble processing that. Could you please try rephrasing?"

def start_therapy_session():
    return "Hi there! How can I help you?"

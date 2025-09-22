import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")


def main():
    # grab args from command line
    user_input = " ".join(sys.argv[1])
    if len(sys.argv) >= 1:
        messages = [types.Content(role="user", parts=[types.Part(text=user_input)]),]
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-001', 
            contents=messages
        )
        print(response.text)
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(
            f"Response tokens: {response.usage_metadata.candidates_token_count}")
    else: 
        raise ValueError("Please provide a prompt as a command line argument.")


if __name__ == "__main__":
    main()

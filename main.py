import os
import sys
from enum import Enum
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")


def main():
    # grab args from command line
    user_args = handle_args()
    if len(sys.argv) >= 1:
        messages = [types.Content(
            role="user", parts=[types.Part(text=user_args["prompt"])]),]
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=messages
        )
        print(response.text)
        if user_args.get('verbose', False):
            print(f"User prompt: {user_args['prompt']}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(
                f"Response tokens: {response.usage_metadata.candidates_token_count}")
    else:
        raise ValueError("Please provide a prompt as a command line argument.")


def handle_args():
    user_args = {}
    if len(sys.argv) < 2:
        print("Usage: python main.py <your prompt here>")
        sys.exit(1)
    user_args['prompt'] = " ".join(sys.argv[1])
    for arg in sys.argv[2:]:
        match arg:
            case "--verbose":
                user_args['verbose'] = True
            case _:
                print(f"Unknown argument: {arg}")
                sys.exit(1)
    return user_args


if __name__ == "__main__":
    main()

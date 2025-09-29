import os
import sys
from enum import Enum
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info, schema_get_files_info

# Load environment variables from .env file
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)


def main():
    system_prompt = """
                    You are a helpful AI coding agent.

                    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

                    - List files and directories

                    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
                    """
    # grab args from command line
    user_args = handle_args()
    if len(sys.argv) >= 1:
        messages = [types.Content(
            role="user", parts=[types.Part(text=user_args["prompt"])]),]
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            )
        )
        print(response.text)
        if response.function_calls:
            for function_call_part in response.function_calls:
                print(f"Calling function: {function_call_part.name}({function_call_part.args})")
        else:
            print(response.text)
        if user_args.get('verbose', False):
            print(f"User prompt: {user_args['prompt']}")
            print(
                f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(
                f"Response tokens: {response.usage_metadata.candidates_token_count}")
    else:
        raise ValueError("Please provide a prompt as a command line argument.")


def handle_args():
    user_args = {}
    if len(sys.argv) < 2:
        print("Usage: python main.py <your prompt here>")
        sys.exit(1)
    if type(sys.argv[1]) is str:
        user_args['prompt'] = sys.argv[1]
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

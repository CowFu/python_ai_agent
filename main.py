import os
import sys
from enum import Enum
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.write_file import write_file, schema_write_file
from functions.get_file_content import get_file_content, schema_get_files_content
from functions.run_python_file import run_python_file, schema_run_python_file

# Load environment variables from .env file
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_write_file,
        schema_get_files_content,
        schema_run_python_file,
    ]
)


def main():
    system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, you should use the available functions to complete the task.

Available functions:
- get_files_info: List files and directories in a given path
- get_file_content: Read the contents of a file
- write_file: Create or overwrite a file with given content
- run_python_file: Execute a Python file with optional arguments

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

When asked to run a Python file, use the run_python_file function. If no arguments are specified by the user, pass an empty list for arguments.
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
        if response.function_calls:
            for function_call_part in response.function_calls:
                function_call_result = call_function(
                    function_call_part, user_args.get('verbose', False))
                if not function_call_result.parts[0]:
                    raise ValueError("Function response is empty")
                elif user_args.get('verbose', True):
                    print(
                        f"-> {function_call_result.parts[0].function_response.response}")
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


def call_function(function_call_part, verbose=False):
    if verbose:
        print(
            f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_result = None

    match function_call_part.name:
        case "get_files_info":
            function_result = get_files_info(
                './calculator', **function_call_part.args)
        case "write_file":
            function_result = write_file(
                './calculator', **function_call_part.args)
        case "get_file_content":
            function_result = get_file_content(
                './calculator', **function_call_part.args)
        case "run_python_file":
            function_result = run_python_file(
                './calculator', **function_call_part.args)
        case _:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call_part.name,
                        response={
                            "error": f"Unknown function: {function_call_part.name}"},
                    )
                ],
            )

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": function_result},
            )
        ],
    )


if __name__ == "__main__":
    main()

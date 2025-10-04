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
        You are a helpful AI coding agent with access to tools for exploring and modifying code.

        When a user asks a question or makes a request:
        1. Use the available functions to explore the codebase and gather information
        2. Start by using get_files_info to see what files are available
        3. Use get_file_content to read relevant files
        4. Use run_python_file to test Python files when needed
        5. Use write_file to create or modify files

        Available functions:
        - get_files_info: List files and directories in a given path (use "." to list current directory)
        - get_file_content: Read the contents of a file
        - write_file: Create or overwrite a file with given content
        - run_python_file: Execute a Python file with optional arguments

        All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

        IMPORTANT: Before answering questions about code, always use the tools to explore and read the actual files. Don't ask the user for clarification when you can use get_files_info and get_file_content to find the answer yourself.

        When you have completed exploring and have enough information to fully answer the user's question, provide a clear and detailed final response.
        """
    
    # grab args from command line
    user_args = handle_args()
    
    if len(sys.argv) >= 2:
        # Initialize the conversation with the user's prompt
        messages = [
            types.Content(
                role="user", 
                parts=[types.Part(text=user_args["prompt"])]
            ),
        ]
        
        client = genai.Client(api_key=api_key)
        
        # Agent loop - maximum 20 iterations
        max_iterations = 20
        
        for iteration in range(max_iterations):
            try:
                # Call the model with the entire conversation history
                response = client.models.generate_content(
                    model='gemini-2.0-flash-001',
                    contents=messages,
                    config=types.GenerateContentConfig(
                        tools=[available_functions], 
                        system_instruction=system_prompt
                    )
                )
                
                # Add the model's response to the conversation
                # The response.candidates list contains the model's response(s)
                for candidate in response.candidates:
                    messages.append(candidate.content)
                
                # Check if the model returned a final text response (no more function calls)
                if response.text and not response.function_calls:
                    print("Final response:")
                    print(response.text)
                    
                    if user_args.get('verbose', False):
                        print(f"\nUser prompt: {user_args['prompt']}")
                        print(f"Total iterations: {iteration + 1}")
                        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
                    
                    break  # Exit the loop - we're done!

                # If there are function calls, execute them
                if response.function_calls:
                    function_responses = []
                    
                    for function_call_part in response.function_calls:
                        function_call_result = call_function(
                            function_call_part, 
                            user_args.get('verbose', False)
                        )
                        
                        if not function_call_result.parts[0]:
                            raise ValueError("Function response is empty")
                        
                        if user_args.get('verbose', False):
                            print(f"-> {function_call_result.parts[0].function_response.response}")
                        
                        function_responses.append(function_call_result.parts[0])
                    
                    # Add all function results to the conversation as a single message
                    messages.append(
                        types.Content(
                            role="user",  # Tool responses come back as "user" role
                            parts=function_responses
                        )
                    )
                                
            except Exception as e:
                print(f"Error during agent loop: {e}")
                if user_args.get('verbose', False):
                    import traceback
                    traceback.print_exc()
                break
        else:
            # This executes if we complete all iterations without breaking
            print("Agent reached maximum iterations without completing the task.")
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
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_result = None

    match function_call_part.name:
        case "get_files_info":
            function_result = get_files_info('./calculator', **function_call_part.args)
        case "write_file":
            function_result = write_file('./calculator', **function_call_part.args)
        case "get_file_content":
            function_result = get_file_content('./calculator', **function_call_part.args)
        case "run_python_file":
            function_result = run_python_file('./calculator', **function_call_part.args)
        case _:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call_part.name,
                        response={"error": f"Unknown function: {function_call_part.name}"},
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
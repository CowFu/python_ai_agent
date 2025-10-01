import google.genai.types as types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a specified Python file within the working directory and returns its output. Limits execution time to 30 seconds.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="A list of arguments to pass to the Python file when executing it.",
            ),
        },
    ),
)


def run_python_file(working_directory, file_path, args=[]):
    import os
    import subprocess

    full_path = os.path.join(working_directory, file_path)
    # Ensure the file is within the working directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    # Ensure the file exists and is a file
    if not os.path.isfile(full_path):
        return f'Error: File "{file_path}" not found.'
    if not full_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    # Execute the Python file and capture output
    try:
        result = subprocess.run(
            ['python3', full_path] + args,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        if not result.stdout and not result.stderr:
            return 'No output produced.'
        output = f"STDOUT: {result.stdout}, STDERR: {result.stderr}"
        # if result process exited with non-zero code, return error
        if result.returncode != 0:
            output += f'Error: Process exited with code {result.returncode}'
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: executing Python file: {e}"
    except Exception as e:
        return f'Error: {str(e)}'

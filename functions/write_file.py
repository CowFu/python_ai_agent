from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specified file, creating the file if it does not exist. If the file already exists, it will be overwritten.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
    ),
)

def write_file(working_directory, file_path, content):
    import os

    # Construct the absolute path
    abs_path = os.path.join(working_directory, file_path)
    if not os.path.abspath(abs_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot read "{abs_path}" as it is outside the permitted working directory'
    try:
        # If the abs_path doesn't exist, create it
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        # Write the content to the file
        with open(abs_path, 'w') as file:
            file.write(content)
        return f'Successfully wrote to "{abs_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error writing file: {e}"

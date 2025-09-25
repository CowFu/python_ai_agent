import os
from config import MAX_FILE_SIZE

def get_file_content(working_directory, file_path):
    full_path = os.path.join(working_directory, file_path)
    # Ensure the file is within the working directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    # Ensure the file exists and is a file
    if not os.path.isfile(full_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    # Read and return the file content
    try:
        with open(full_path, 'r') as file:
            content = file.read()
            # Limit content size to 1000 characters
            if len(content) > MAX_FILE_SIZE:
                content = content[:MAX_FILE_SIZE] + f'[...File "{file_path}" truncated at 10000 characters]'
        return content
    except Exception as e:
        return f'Error: {str(e)}'
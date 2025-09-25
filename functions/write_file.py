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

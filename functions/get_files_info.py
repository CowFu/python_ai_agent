import os


def get_files_info(working_directory, directory="."):
    full_path = os.path.join(working_directory, directory)
    # Ensure the directory is within the working directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    # Ensure the directory is a directory
    if not os.path.isdir(full_path):
        return f'Error: "{directory}" is not a directory'
    # Build and return a string representing the contents of the directory (ex. README.md: file_size=1032 bytes, is_dir=False)
    try:
        files_info = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            item_info = {
                "name": item,
                "file_size": os.path.getsize(item_path),
                "is_dir": os.path.isdir(item_path)
            }
            files_info.append(
                f"{item}: file_size={item_info['file_size']} bytes, is_dir={item_info['is_dir']}")
        return "\n".join(files_info)
    except Exception as e:
        return f'Error: {str(e)}'

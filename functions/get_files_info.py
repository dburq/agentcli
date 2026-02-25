import os

def get_files_info(working_directory, directory="."):
    working_dir_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))

    if os.path.commonpath([working_dir_abs, target_dir]) != working_dir_abs:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'
    
    dir_list = os.listdir(target_dir)
    dir_info = []

    for dir_object in dir_list:
        item_path = os.path.join(target_dir, dir_object)
        size = os.path.getsize(item_path)
        is_directory = os.path.isdir(item_path)

        dir_info.append(f'- {dir_object}: file_size={size} bytes, is_dir={is_directory}')
        
    return "\n".join(dir_info)
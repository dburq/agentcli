import os
import sys
import subprocess

def run_python_file(working_directory, file_path, args=None):
    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

    if os.path.commonpath([working_dir_abs, target_file]) != working_dir_abs:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not a regular file'
    
    if os.path.splitext(target_file)[1].lower() != ".py":
        return f'Error: "{file_path}" is not a Python file'

    command = [sys.executable, target_file]
    if args:
        command.extend(args)

    result = subprocess.run(command, capture_output=True, cwd=working_dir_abs, timeout=30, text=True)


    output_lines = []
    
    if result.returncode != 0:
        output_lines.append(f'Process exited with code {result.returncode}')

    if result.stdout == "" and result.stderr == "":
        output_lines.append("No output produced")
    else:
        if result.stdout != "":
            output_lines.append(f'STDOUT: {result.stdout}')
        if result.stderr != "":
            output_lines.append(f'STDERR: {result.stderr}')

    return "\n".join(output_lines)
import os
import shutil


def reset_tmp_folder():
    """
    Deletes the './tmp' folder and its contents, then recreates the folder.
    If the folder doesn't exist, it simply creates it.
    """
    tmp_path = os.path.join(os.path.dirname(__file__), "tmp")
    tmp_path = os.path.abspath(tmp_path)
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
    os.makedirs(tmp_path, exist_ok=True)
    print(f"TRACE: Reset temporary folder 'tmp/'")


def get_sys_prompt():
    with open("../llm.md") as infile:
        return infile.read()

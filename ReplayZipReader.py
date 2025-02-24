import os
import zipfile
from typing import Tuple

def get_all_replays_paths():
    replays_dir = "replays"
    file_names = [os.path.join(replays_dir, f) for f in os.listdir(replays_dir) if f.endswith(".zip")]
    return file_names
def get_replay_content(zip_path)->Tuple[str, str]:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # List all files in the zip archive
        file_list = zip_ref.namelist()
        qm_filename = [name for name in file_list if ".qm" in name][0]
        ss_filename = [name for name in file_list if ".ss" in name][0]
        qm = ""
        with zip_ref.open(qm_filename, "r") as file:
            qm = str(file.read())
        with zip_ref.open(ss_filename, "r") as file:
            ss = str(file.read().decode("utf-8"))
        return (qm,ss)
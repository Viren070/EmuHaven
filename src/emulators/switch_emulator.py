import os 
import shutil 

from zipfile import ZipFile


def check_current_firmware(firmware_path):

    if os.path.exists(firmware_path) and os.listdir(firmware_path):
        return True
    return False

def check_current_keys(key_path):
    if os.path.exists(key_path):
        return True 
    return False

def verify_firmware_archive(path_to_archive):
    archive = path_to_archive
    if not os.path.exists(archive):
        return False 
    if not archive.endswith(".zip"):
        return False 
    with ZipFile(archive, 'r') as r_archive:
        for filename in r_archive.namelist():
            if not filename.endswith(".nca"):
                return False 
    return True 
    
def verify_key_archive(path_to_archive):
    archive = path_to_archive
    if not os.path.exists(archive):
        return False 
    if path_to_archive.endswith(".keys"):
        return True
    if not archive.endswith(".zip"):
        return False 
    with ZipFile(archive, 'r') as r_archive:
        for filename in r_archive.namelist():
            if not filename.endswith(".keys"):
                return False 
            if filename=="prod.keys":
                found=True
    return found


def install_firmware_from_archive(firmware_source, extract_folder, progress_frame, emulator):

    if os.path.exists(extract_folder):
        shutil.rmtree(extract_folder)
    os.makedirs(extract_folder, exist_ok=True)
    extracted_files = []
    progress_frame.start_download(os.path.basename(firmware_source), 0)
    progress_frame.complete_download()
    progress_frame.update_status_label("Extracting...")
    progress_frame.grid(row=0, column=0, sticky="ew")
    excluded = []
    try:
        with open(firmware_source, "rb") as file:
            with ZipFile(file, 'r') as archive:
                total = len(archive.namelist())
                for entry in archive.infolist():
                    if entry.filename.endswith(".nca") or entry.filename.endswith(".nca/00"):
                        path_components = entry.filename.replace(".cnmt", "").split("/")
                        nca_id = path_components[-1]
                        if nca_id == "00":
                            nca_id = path_components[-2]
                        if ".nca" in nca_id:
                            if emulator == "ryujinx":
                                new_path = os.path.join(extract_folder, nca_id)
                                os.makedirs(new_path, exist_ok=True)
                                with open(os.path.join(new_path, "00"), "wb") as f:
                                    f.write(archive.read(entry))
                            elif emulator == "yuzu":
                                new_path = os.path.join(extract_folder, nca_id)
                                os.makedirs(extract_folder, exist_ok=True)
                                with open(new_path, "wb") as f:
                                    f.write(archive.read(entry))
                          
                            extracted_files.append(entry.filename)
                            progress_frame.update_extraction_progress(len(extracted_files)/total)
                        else:
                            excluded.append(entry.filename)
                        
    except Exception as error:
        progress_frame.grid_forget()
        return (False, error)
    progress_frame.grid_forget()
    return (True, excluded)


def install_keys_from_file(key_path, target_key_folder):
    if not os.path.exists(target_key_folder):
        os.makedirs(target_key_folder)
    target_key_location = os.path.join(target_key_folder, "prod.keys")
    shutil.copy(key_path, target_key_location)
    return target_key_location

def install_keys_from_archive(key_archive, extract_folder, progress_frame):
    extracted_files = []
    progress_frame.start_download(os.path.basename(key_archive).replace(".zip", ""), 0)
    progress_frame.grid(row=0, column=0, sticky="ew")
    try:
        with ZipFile(key_archive, 'r') as zip_ref:
            total = len(zip_ref.namelist())
            for file_info in zip_ref.infolist():
                extracted_file_path = os.path.join(extract_folder, file_info.filename)
                os.makedirs(os.path.dirname(extracted_file_path), exist_ok=True)
                with zip_ref.open(file_info.filename) as source, open(extracted_file_path, 'wb') as target:
                    target.write(source.read())
                extracted_files.append(file_info.filename)
                progress_frame.update_extraction_progress(len(extracted_files)/total)
    except Exception as error:
        progress_frame.grid_forget()
        return (False, error)
    progress_frame.grid_forget()
    return (True, extracted_files)

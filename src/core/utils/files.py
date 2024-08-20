import os
import shutil
from zipfile import ZipFile
from utils.progress_handler import ProgressHandler


def copy_directory_with_progress(source_dir, target_dir, progress_handler=ProgressHandler(), exclude=None, include=None):
    if not os.path.exists(source_dir):
        return {"status": False, "message": f"Path does not exist: {source_dir}"}
    # Get a list of all files and folders in the source directory
    all_files = []
    for root, dirs, files in os.walk(source_dir):
        all_files.extend([os.path.join(root, file) for file in files])

    if include:
        all_files = [file for file in all_files if any(
            incl_folder in file for incl_folder in include)]
    elif exclude:
        all_files = [file for file in all_files if not any(
            excl_folder in file for excl_folder in exclude)]
    # Get the total number of files to copy
    total_files = len(all_files)
    progress_handler.update_total_files(total_files)
    progress_handler.start_operation()

    # Create the target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Copy files from source to target directory and display progress
    copied_files = 0
    for file in all_files:
        if progress_handler.should_cancel_operation():
            progress_handler.cancel_operation()
            return

        target_file = os.path.join(
            target_dir, os.path.relpath(file, source_dir))

        target_dirname = os.path.dirname(target_file)

        # Create the necessary directories in the target if they don't exist
        if not os.path.exists(target_dirname):
            os.makedirs(target_dirname)

        # Copy the file to the target directory
        shutil.copy2(file, target_file)

        copied_files += 1
        progress = (copied_files / total_files)
        progress_handler.report_progress(progress)

    progress_handler.complete_operation()
    return {
        "status": True,
        "message": "Files copied successfully",
    }

def extract_zip_archive_with_progress(zip_path, extract_directory, progress_handler=ProgressHandler()):
    extracted_files = []

    if extract_directory.exists() and extract_directory.iterdir():
        shutil.rmtree(extract_directory)
    try:
        with ZipFile(zip_path, 'r') as archive:
            total_files = len(archive.namelist())
            for file in archive.namelist():
                if progress_handler.should_cancel():
                    progress_handler.cancel()
                    return {"status": False, "message": "The extraction was cancelled by the user"}
                archive.extract(file, extract_directory)
                extracted_files.append(file)
                # Calculate and display progress
                progress_handler.report_progress(len(extracted_files))
    except Exception as error:
        progress_handler.report_error(error)
        return {"status": False, "message": error}
    progress_handler.complete_operation()
    return {"status": True, "message": "Extraction successful", "extracted_files": extracted_files}
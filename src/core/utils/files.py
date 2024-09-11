import shutil
import zipfile

from core.utils.progress_handler import ProgressHandler


def copy_directory_with_progress(source_dir, target_dir, progress_handler=None, exclude=None, include=None):
    if progress_handler is None:
        progress_handler = ProgressHandler()    
    if not source_dir.exists() or not source_dir.is_dir():
        progress_handler.report_error(f"Path does not exist or is not a directory: {source_dir}")
        return {"status": False, "message": f"Path does not exist or is not a directory: {source_dir}"}

    # Get a list of all files and folders in the source directory
    all_files = []
    for root, dirs, files in source_dir.walk():
        all_files.extend([root / file for file in files])

    if include:
        all_files = [file for file in all_files if any(
            incl_folder in file.parts for incl_folder in include)]
    elif exclude:
        all_files = [file for file in all_files if not any(
            excl_folder in file.parts for excl_folder in exclude)]
    # Get the total number of files to copy
    total_files = len(all_files)
    progress_handler.set_total_units(total_files)

    # Create the target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy files from source to target directory and display progress
    copied_files = 0
    for file in all_files:
        if progress_handler.should_cancel():
            progress_handler.cancel()
            return {"status": False, "message": "Copy operation cancelled"}

        target_file = target_dir / file.relative_to(source_dir)

        target_dirname = target_file.parent

        # Create the necessary directories in the target if they don't exist
        target_dirname.mkdir(parents=True, exist_ok=True)

        # Copy the file to the target directory
        shutil.copy2(file, target_file)

        copied_files += 1
        progress_handler.report_progress(copied_files)

    progress_handler.report_success()
    return {
        "status": True,
        "message": "Files copied successfully",
    }

def extract_zip_archive_with_progress(zip_path, extract_directory, progress_handler):
    extracted_files = []
    if progress_handler is None:
        progress_handler = ProgressHandler()
    rollback_needed = False
    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            total_files = len(archive.namelist())
            progress_handler.set_total_units(total_files)
            for file in archive.namelist():
                if progress_handler.should_cancel():
                    rollback_needed = True
                    break
                archive.extract(file, extract_directory)
                extracted_files.append(file)
                # Calculate and display progress
                progress_handler.report_progress(len(extracted_files))
    except zipfile.BadZipFile as error:
        progress_handler.report_error(error)
        return {"status": False, "message": "The ZIP file is corrupted or invalid"}
    except Exception as error:
        progress_handler.report_error(error)
        return {"status": False, "message": error}
    
    if rollback_needed:
        progress_handler.cancel()
        dirs = []
        for file in extracted_files:
            file_path = extract_directory / file
            if file_path.is_dir():
                dirs.append(file_path)
            if file_path.is_file():
                file_path.unlink(missing_ok=True)
        for dir in dirs:
            try:
                dir.rmdir()
            except OSError:
                pass
        zip_path.unlink(missing_ok=True)
        return {"status": False, "message": "Extraction cancelled"}
    progress_handler.report_success()
    return {"status": True, "message": "Extraction successful", "extracted_files": extracted_files}
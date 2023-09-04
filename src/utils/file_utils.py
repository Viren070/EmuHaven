import os
import shutil
from tkinter import messagebox

from gui.frames.progress_frame import ProgressFrame


def copy_directory_with_progress(source_dir, target_dir, title, log_frame, exclude=None):
        if not os.path.exists(source_dir):
            messagebox.showerror("Path Error", f"Path does not exist: {source_dir}")
            return
        progress_bar = ProgressFrame(log_frame, title)
        progress_bar.skip_to_installation()
        progress_bar.grid(row=0, column=0, sticky="nsew")
        progress_bar.grid_propagate(False)
        progress_bar.cancel_download_button.configure(state="normal")
        # Get a list of all files and folders in the source directory
        all_files = []
        for root, dirs, files in os.walk(source_dir):
            all_files.extend([os.path.join(root, file) for file in files])
            
        if exclude:
            all_files = [file for file in all_files if not any(excl_folder in file for excl_folder in exclude)]
        # Get the total number of files to copy
        total_files = len(all_files)

        # Create the target directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        def find_common_suffix(file_path, target_file_path):
            file_parts = file_path.split(os.sep)
            target_parts = target_file_path.split(os.sep)

            common_suffix = []
            while file_parts and target_parts and file_parts[-1] == target_parts[-1]:
                common_suffix.insert(0, file_parts.pop())
                target_parts.pop()

            return os.path.join(*common_suffix)

        # Copy files from source to target directory and display progress
        copied_files = 0
        for file in all_files:
            if progress_bar.cancel_download_raised:
                progress_bar.destroy()
                return 
            
            target_file = os.path.join(target_dir, os.path.relpath(file, source_dir))
            
            target_dirname = os.path.dirname(target_file)
            
            progress_bar.install_status_label.configure(text=find_common_suffix(file, target_file))
            # Create the necessary directories in the target if they don't exist
            if not os.path.exists(target_dirname):
                os.makedirs(target_dirname)

            # Copy the file to the target directory
            shutil.copy2(file, target_file)

            copied_files += 1
            progress = (copied_files / total_files) 
            progress_bar.update_extraction_progress(progress)
        progress_bar.destroy()
        messagebox.showinfo("Copy Complete!", f"{title} Complete!")
    
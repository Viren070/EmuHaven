import os
import shutil
import subprocess
import time
from tkinter import messagebox
from zipfile import ZipFile

from core.utils.github import get_latest_release_with_asset
from core.utils.files import copy_directory_with_progress


class Xenia:
    def __init__(self, gui, settings, metadata):
        self.settings = settings
        self.metadata = metadata
        self.gui = gui
        self.running = False
        self.main_progress_frame = None
        self.data_progress_frame = None

    def delete_xenia_zip(self, zip_path):
        time.sleep(2)
        os.remove(zip_path)

    def verify_xenia_zip(self, path_to_archive, release_channel):
        try:
            with ZipFile(path_to_archive, 'r') as archive:
                if ("xenia.exe" if release_channel == "Master" else "xenia_canary.exe") in archive.namelist():
                    return True
                else:
                    return False
        except Exception:
            return False

    def install_xenia_handler(self, release_channel=None, path_to_archive=None, updating=False):
        release_archive = path_to_archive
        if release_channel is None and path_to_archive is None:
            raise ValueError("If release channel is None, you must provide a path to archive")
        if path_to_archive is None:
            release_result = self.get_xenia_release(release_channel)
            if not all(release_result):
                messagebox.showerror("Install Xenia", f"There was an error while attempting to fetch the latest {release_channel} release of Xenia:\n\n{release_result[1]}")
                return
            release = release_result[1]
            installed_version = self.metadata.get_installed_version(f"xenia_{release_channel.lower()}")
            if updating and release.version == installed_version:
                return
            download_result = self.download_release(release)
            if not all(download_result):
                if download_result[1] != "Cancelled":
                    messagebox.showerror("Error", f"There was an error while attempting to download the latest {release_channel} release of Xenia\n\n{download_result[1]}")
                else:
                    try:
                        os.remove(download_result[2])
                    except Exception as error:
                        messagebox.showwarning("Error", f"Failed to delete file after cancelling due to error below:\n\n{error}")
                return
            release_archive = download_result[1]
        elif not self.verify_xenia_zip(path_to_archive, release_channel):
            messagebox.showerror("Error", "The xenia archive you have provided is invalid. ")
            return
        extract_result = self.extract_xenia_release(release_archive, release_channel)
        if path_to_archive is None and self.settings.app.delete_files == "True":
            os.remove(release_archive)
        if not all(extract_result):
            if extract_result[1] != "Cancelled":
                messagebox.showerror("Extract Error", f"An error occurred while extracting the release: \n\n{extract_result[1]}")
            return
        if path_to_archive is None:
            self.metadata.update_installed_version(f"xenia_{release_channel.lower()}", release.version)
        if not updating:
            messagebox.showinfo("Install Xenia", f"Xenia was successfully installed to {self.settings.xenia.install_directory}")

    def get_xenia_release(self, release_channel):
        repo_url = "https://api.github.com/repos/xenia-project/release-builds-windows/releases/latest" if release_channel == "Master" else "https://api.github.com/repos/xenia-canary/xenia-canary/releases/latest"
        response = create_get_connection(repo_url, headers=get_headers(self.settings.app.token), timeout=30)
        if not all(response):
            return response
        response = response[1]
        try:
            release_info = response.json()
            latest_version = release_info["tag_name"] if release_channel == "Master" else release_info["target_commitish"][:7]
            assets = release_info["assets"]
        except KeyError:
            return (False, "Unable to parse response from GitHub. You may have been API rate limited.")
        release = get_release_from_assets(assets, f"xenia_{release_channel.lower()}.zip", wildcard=True)
        release.version = latest_version
        return (True, release)

    def download_release(self, release):
        download_folder = os.getcwd()
        download_path = os.path.join(download_folder, f"{release.name.replace(".zip", "")}@{release.version}.zip")
        response_result = create_get_connection(release.download_url, headers=get_headers(), stream=True, timeout=30)
        if not all(response_result):
            return response_result
        response = response_result[1]
        self.main_progress_frame.start_download(release.name, release.size)
        self.main_progress_frame.grid(row=0, column=0, sticky="ew")

        download_result = download_through_stream(response, download_path, self.main_progress_frame, 1024*203)
        self.main_progress_frame.complete_download()
        return download_result

    def extract_xenia_release(self, release, release_channel):
        if release.endswith(".zip"):
            return self.extract_xenia_zip_archive(release, release_channel)
        else:
            return (False, "Unsupported archive type")

    def extract_xenia_zip_archive(self, release_archive, release_channel):
        self.main_progress_frame.start_download(f"{os.path.basename(release_archive).replace(".zip", "")}", 0)
        self.main_progress_frame.complete_download()
        self.main_progress_frame.update_status_label("Extracting... ")
        self.main_progress_frame.grid(row=0, column=0, sticky="nsew")
        extracted = True
        try:
            with ZipFile(release_archive, 'r') as archive:
                total_files = len(archive.namelist())
                extracted_files = []
                for file in archive.namelist():
                    if self.main_progress_frame.cancel_download_raised:
                        extracted = False
                        break
                    archive.extract(file, os.path.join(self.settings.xenia.install_directory, release_channel.lower()))
                    extracted_files.append(file)
                    # Calculate and display progress
                    self.main_progress_frame.update_extraction_progress(len(extracted_files) / total_files)
            self.main_progress_frame.grid_forget()
            if extracted:
                return (True, extracted_files)
            else:
                return (False, "Cancelled")
        except Exception as error:
            self.main_progress_frame.grid_forget()
            return (False, error)

    def delete_xenia(self, version):
        try:
            path_to_remove = os.path.join(self.settings.xenia.install_directory, version)
            shutil.rmtree(path_to_remove)
            messagebox.showinfo("Success", f"The Xenia {version} installation was successfully was removed")
        except Exception as e:
            messagebox.showerror("Error", f"There was an error while attempting to delete Xenia {version}: \n\\n{e}")
            return

    def launch_xenia_handler(self, release_channel, skip_update=False, wait_for_exit=True):
        if not skip_update:
            self.gui.configure_action_buttons("disabled", text="Fetching Updates...  ", width=170)
            self.install_xenia_handler(release_channel, None, True)

        self.gui.configure_action_buttons("disabled", text="Launched!  ", width=170)
        xenia_exe = os.path.join(self.settings.xenia.install_directory, release_channel, "xenia.exe" if release_channel == "Master" else "xenia_canary.exe")
        args = [xenia_exe]
        self.running = True

        if wait_for_exit:
            subprocess.run(args, check=False)
        else:
            subprocess.Popen(args)
        self.running = False

    def export_xenia_data(self, mode, directory_to_export_to, folders_to_export=None):
        user_directory = self.settings.xenia.user_directory

        if not os.path.exists(user_directory):
            messagebox.showerror("Missing Folder", "No xenia data on local drive found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Xenia Data", self.data_progress_frame)
        elif mode == "Custom":
            if not folders_to_export:
                messagebox.showerror("Missing Folder", "No folders were selected to export")
                return
            copy_directory_with_progress(user_directory, directory_to_export_to, "Exporting All Xenia Data", self.data_progress_frame, include=folders_to_export)

    def import_xenia_data(self, mode, directory_to_import_from, folders_to_import=None):
        user_directory = self.settings.xenia.user_directory

        if not os.path.exists(directory_to_import_from):
            messagebox.showerror("Missing Folder", "No xenia data associated with your username was found")
            return  # Handle the case when the user directory doesn't exist.
        if mode == "All Data":
            copy_directory_with_progress(directory_to_import_from, user_directory, "Importing All xenia Data", self.data_progress_frame)
        elif mode == "Custom":
            if not folders_to_import:
                messagebox.showerror("Missing Folder", "No folders were selected to import")
                return
            copy_directory_with_progress(directory_to_import_from, user_directory, "Importing All xenia Data", self.data_progress_frame, include=folders_to_import)

    def delete_xenia_data(self, mode, folders_to_delete=None):
        result = ""
        user_directory = self.settings.xenia.user_directory

        def delete_directory(directory):
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    return True
                except Exception as error:
                    messagebox.showerror("Delete Xenia Data", f"Unable to delete \n{directory}\ndue to error:\n\n{error}")
                    return False
            return False
        if mode == "All Data":
            result += f"Data Deleted from {user_directory}\n" if delete_directory(user_directory) else ""
        elif mode == "Custom":
            deleted = False
            for folder in folders_to_delete:
                folder_path = os.path.join(user_directory, folder)
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    if delete_directory(folder_path):
                        deleted = True
                        result += f"Data deleted from {folder_path}\n"
                    else:
                        result += f"Deletion failed for {folder_path}\n"
            if not deleted:
                result = ""
        if result:
            messagebox.showinfo("Delete result", result)
        else:
            messagebox.showinfo("Delete result", "Nothing was deleted.")

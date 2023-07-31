from base64 import b64decode
import os
import re
from sys import exit as sysexit
from shutil import copy, rmtree
from threading import Thread
import tkinter as tk
from zipfile import ZipFile 
from io import BytesIO
from time import perf_counter, sleep
from tkinter import filedialog, messagebox
from urllib.parse import unquote

import customtkinter
import requests
from bs4 import BeautifulSoup


class DownloadStatusFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, filename, parent):
        super().__init__(parent_frame)
        self.grid_columnconfigure(0, weight=1)
        self.cancel_download_raised = False
        self.filename = filename
        self.start_time = perf_counter()
        self.parent = parent
        self.total_size = 0
        self.time_during_cancel = 0
        self._current_width = 200
        self.download_name = customtkinter.CTkLabel(self, text=filename)
        self.download_name.grid(row=0, column=0, sticky="W", padx=10, pady=5)

        self.progress_label = customtkinter.CTkLabel(self, text="0 MB / 0 MB")
        self.progress_label.grid(row=1, column=0, sticky="W", padx=10)

        self.progress_bar = customtkinter.CTkProgressBar(
            self, orientation="horizontal", mode="determinate")
        self.progress_bar.grid(row=2, column=0, columnspan=6,
                               padx=(10, 45), pady=5, sticky="EW")
        self.progress_bar.set(0)

        self.percentage_complete = customtkinter.CTkLabel(self, text="0%")
        self.percentage_complete.grid(row=2, column=5, sticky="E", padx=10)

        self.download_speed_label = customtkinter.CTkLabel(self, text="0 MB/s")
        self.download_speed_label.grid(row=1, column=5, sticky="E", padx=10)

        self.install_status_label = customtkinter.CTkLabel(
            self, width=100, text="Status: Downloading...")
        self.install_status_label.grid(
            row=3, column=0, sticky="W", padx=10, pady=5)

        self.eta_label = customtkinter.CTkLabel(
            self, text="Time Left: 00:00:00")
        self.eta_label.grid(row=0, column=5, sticky="E", pady=5, padx=10)

        self.cancel_download_button = customtkinter.CTkButton(
            self, text="Cancel", command=self.cancel_button_event)
        self.cancel_download_button.grid(
            row=3, column=5, pady=10, padx=10, sticky="E")

    def update_download_progress(self, downloaded_bytes, chunk_size):

        done = downloaded_bytes / self.total_size
        avg_speed = downloaded_bytes / \
            ((perf_counter() - self.start_time) - self.time_during_cancel)
        # cur_speed = chunk_size / (perf_counter() - self.time_at_start_of_chunk)
        time_left = (self.total_size - downloaded_bytes) / avg_speed

        minutes, seconds = divmod(int(time_left), 60)
        hours, minutes = divmod(minutes, 60)
        time_left_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.progress_bar.set(done)
        self.progress_label.configure(
            text=f"{downloaded_bytes/1024/1024:.2f} MB / {self.total_size/1024/1024:.2f} MB")
        self.percentage_complete.configure(
            text=f"{str(done*100).split('.')[0]}%")
        self.download_speed_label.configure(
            text=f"{avg_speed/1024/1024:.2f} MB/s")
        self.eta_label.configure(text=f"Time Left: {time_left_str}")
        self.time_at_start_of_chunk = perf_counter()
        if self.install_status_label.cget("text") != "Status: Downloading...":
            self.install_status_label.configure(text="Status: Downloading...")
        # print(f"Current: {speed/1024/1024:.2f} MB/s")
        # print(f"Avg: {avg_speed/1024/1024:.2f} MB/s")

    def cancel_button_event_old(self, skip_confirmation=False):
        start_time = perf_counter()
        self.cancel_download_raised = True
        self.install_status_label.configure(text="Status: Cancelling...")
        if skip_confirmation and messagebox.askyesno("Confirmation", "Are you sure you want to cancel this download?"):
            
            self.install_status_label.configure(text="Status: Cancelled")
            return True
        else:
            self.time_during_cancel += (perf_counter() - start_time)
            return False
    def cancel_button_event(self):
        start_time = perf_counter()
        
        
        if messagebox.askyesno("Confirmation", "Are you sure you want to cancel this download?"):
    
            self.install_status_label.configure(text="Status: Cancelled")
            self.cancel_download_raised = True
            self.parent.firmware_installation_in_progress = False
            return True
        else:
            self.time_during_cancel += (perf_counter() - start_time)
            return False
    
    def remove_status_frame(self):
        self.parent.downloads_in_progress -= 1
        self.destroy()

    def update_extraction_progress(self, value):
        self.progress_bar.set(value)
        self.percentage_complete.configure(
            text=f"{str(value*100).split('.')[0]}%")

    def installation_interrupted(self, error):
        self.cancel_download_raised = True
        self.cancel_download_button.configure(state="disabled")
        self.install_status_label.configure(text=f"Encountered error: {error}")
        self.cancel_download_button.configure(
            text="Remove", command=self.remove_status_frame, state="normal")

    def skip_to_installation(self):
        self.download_speed_label.grid_forget()
        self.eta_label.grid_forget()
        self.cancel_download_button.configure(state="disabled")
        self.progress_label.grid_forget()

    def complete_download(self, emulator):
        self.cancel_download_button.configure(state="disabled")
        self.install_status_label.configure(
            text=f"Status: Installing for {emulator}....")
        self.progress_bar.set(0)
        self.percentage_complete.configure(text="0%")

    def finish_installation(self):
        minutes, seconds = divmod(int(perf_counter()-self.start_time), 60)
        hours, minutes = divmod(minutes, 60)
        elapsed_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.install_status_label.configure(text="Status: Complete")
        self.eta_label.configure(text=f"Elapsed time: {elapsed_time}")
        self.download_speed_label.configure(text="0 MB/s")
        self.cancel_download_button.configure(
            text="Remove", command=self.remove_status_frame, state="normal")
        messagebox.showinfo("Download Complete",
                            f"{self.filename} has been installed")


class OptionsMenu(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("600x400")

        # Install Firmware section
        self.firmware_frame = customtkinter.CTkFrame(self)
        self.firmware_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.install_firmware_label = customtkinter.CTkLabel(self.firmware_frame, text="Install Firmware:")
        self.install_firmware_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.install_from_zip_button = customtkinter.CTkButton(self.firmware_frame, text="Install Firmware from ZIP", command=master.install_from_zip_button_wrapper)
        self.install_from_zip_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.install_from_directory_button = customtkinter.CTkButton(self.firmware_frame, text="Install Firmware from Directory", command=master.start_firmware_installation_from_directory)
        self.install_from_directory_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.install_keys_button = customtkinter.CTkButton(self.firmware_frame, text="Install keys from ZIP/.keys file", command=master.install_keys_button_wrapper)
        self.install_keys_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Options section
        self.options_frame = customtkinter.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Delete files option
        
        self.delete_files_checkbutton = customtkinter.CTkCheckBox(self.options_frame, text="Delete files after installing", variable=master.delete_download)
        self.delete_files_checkbutton.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Emulator choice option
        self.emulator_choice = customtkinter.StringVar(value="Both")
        self.emulator_label = customtkinter.CTkLabel(self.options_frame, text="Install files for:")
        self.emulator_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.emulator_dropdown = customtkinter.CTkOptionMenu(self.options_frame, variable=master.emulator_choice, values=["Yuzu", "Ryujinx", "Both"])
        self.emulator_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Chunk size option
        self.chunk_label = customtkinter.CTkLabel(self.options_frame, text="Choose chunk size:")
        self.chunk_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        chunk_size_list = []
        for i in range(10):
            
            value = 16384*(2**i)
            label = f"{str(int((value)/1024))} KB" if value < 1024 * \
                1024 else f"{str(int((value)/1024/1024))} MB"
            chunk_size_list.append(label)
        self.chunk_size_dropdown = customtkinter.CTkOptionMenu(self.options_frame, variable=master.chunk_size, values= chunk_size_list)
        self.chunk_size_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Fetch versions command
        self.fetch_versions_button = customtkinter.CTkButton(self.options_frame, text="Attempt version fetch", command=master.fetch_versions)
        self.fetch_versions_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

class Application(customtkinter.CTkFrame):
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        
        self.delete_download = tk.BooleanVar()
        self.delete_download.set(True)
        self.chunk_size = customtkinter.StringVar()
        self.chunk_size.set("64 KB")
        self.emulator_choice = customtkinter.StringVar()
        self.emulator_choice.set("Yuzu")
        # self.resizable(False, False)
        self.fetched_versions = 0
        self.fetching_versions = False
        self.versions_fetched = False
        self.firmware_installation_in_progress = False
        self.key_installation_in_progress = False
        self.retries_attempted = 0
        self.error_fetching_versions = False
        self.downloads_in_progress = 0
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.add("Both")
        self.tabview.add("Firmware")
        self.tabview.add("Keys")
        self.tabview.add("Downloads")
        self.tabview.grid(row=1, column=0, padx=20, pady=20)
        self.toplevel_window = None
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.firmware_versions_frame = customtkinter.CTkScrollableFrame(
            self.tabview.tab("Firmware"), width=700, height=400)
        self.firmware_versions_frame.grid(row=0, column=0, sticky="nsew")
        self.firmware_versions_frame.grid_columnconfigure(0, weight=1)
        self.firmware_versions_frame_label = customtkinter.CTkLabel(
            self.firmware_versions_frame, text="Fetching, please wait...")

        self.key_versions_frame = customtkinter.CTkScrollableFrame(
            self.tabview.tab("Keys"), width=700, height=400)
        self.key_versions_frame.grid(row=0, column=0)
        self.key_versions_frame.grid_columnconfigure(0, weight=1)
        self.key_versions_frame_label = customtkinter.CTkLabel(
            self.key_versions_frame, text="Fetching, please wait...")

        self.both_versions_frame = customtkinter.CTkScrollableFrame(
            self.tabview.tab("Both"), width=700, height=400)
        self.both_versions_frame.grid(row=0, column=0)
        self.both_versions_frame.grid_columnconfigure(0, weight=1)
        self.both_versions_frame_label = customtkinter.CTkLabel(
            self.both_versions_frame, text="Fetching, please wait...")

        self.downloads_frame = customtkinter.CTkScrollableFrame(
            self.tabview.tab("Downloads"), width=700, height=400)
        self.downloads_frame.grid(row=0, column=0)
        self.downloads_frame.grid_columnconfigure(0, weight=1)
       
        # Create downloads folder
        

        # Add closing behavior
        

        # Fetch versions and start the GUI loop
        
    def options_menu(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = OptionsMenu(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it
        
        
        

    def on_closing(self):
        if self.firmware_installation_in_progress or self.key_installation_in_progress:
            if not messagebox.askyesno("Confirmation", "Are you sure you want to quit? The download in progress will be stopped"):
                return

        sysexit()

    def fetch_versions(self):

        if self.fetching_versions:
            messagebox.showerror(
                "EmuTool", "A version fetch is already in progress!")
            return
        if self.versions_fetched:
            messagebox.showerror(
                "EmuTool", "The versions available have already been displayed")
            return
        self.firmware_versions_frame_label.grid(sticky='nsew')
        self.key_versions_frame_label.grid(sticky='nsew')
        self.both_versions_frame_label.grid(sticky='nsew')
        self.fetching_versions = True
        self.versions_fetched = False
        self.fetched_versions = 0
        self.error_encountered = None
        self.error_fetching_versions = False
        Thread(target=self.fetch_firmware_versions).start()
        Thread(target=self.fetch_key_versions).start()
        Thread(target=self.display_both_versions).start()

    def display_both_versions(self):
        while self.fetched_versions < 2:
            if self.error_fetching_versions:

                self.fetching_versions = False
                if messagebox.askretrycancel("Error", f"Error while fetching versions. Retry?\n\nFull Error: {self.error_encountered}"):
                    self.retries_attempted += 1
                    self.fetch_versions()
                    return
                else:
                    self.both_versions_frame_label.grid_forget()
                    self.key_versions_frame_label.grid_forget()
                    self.firmware_versions_frame_label.grid_forget()
                    messagebox.showinfo(
                        "EmuTool", "You will only be able to install firmware and keys through files that are already downloaded by clicking \nFile > Install Firmware/Keys from ZIP/.keys file at the tom.")
                    return

            sleep(1)
        self.both_versions_frame_label.grid_forget()
        count = 0
        firmware_versions_dict = {}
        versions_added = set()

        for firmware_version in self.firmware_versions:
            firmware_version_number = firmware_version[0].split(
                "Firmware ")[-1]
            firmware_version_number = (
                "".join(re.split("\(|\)|\[|\]", firmware_version_number)[::2])).replace(" ", "")
            if firmware_version_number in firmware_versions_dict:
                continue
            firmware_versions_dict[firmware_version_number] = (
                firmware_version[1])

        for key_version in self.key_versions:
            key_version_number = key_version[0].split("Keys ")[-1]
            if key_version_number in versions_added:
                continue
            if key_version_number in firmware_versions_dict:
                versions_added.add(key_version_number)
                version = key_version_number
                links = [key_version[1],
                         firmware_versions_dict[key_version_number]]
                version_label = customtkinter.CTkLabel(
                    self.both_versions_frame, text=f"{version} - Latest" if count == 0 else version)
                version_label.grid(row=count, column=0, pady=10, sticky="W")
                version_button = customtkinter.CTkButton(
                    self.both_versions_frame, text="Download", command=lambda links=links: self.start_installation(links, mode="Both"))
                version_button.grid(row=count, column=1, pady=10, sticky="E")
                count += 1

        self.fetching_versions = False
        self.versions_fetched = True

    def fetch_firmware_versions(self):

        url = b64decode(
            'aHR0cHM6Ly9kYXJ0aHN0ZXJuaWUubmV0L3N3aXRjaC1maXJtd2FyZXMv'.encode("ascii")).decode("ascii")
        try:
            page = requests.get(url)
        except Exception as error:
            self.error_fetching_versions = True
            self.error_encountered = error

            return
        soup = BeautifulSoup(page.content, "html.parser")

        self.firmware_versions = []

        for link in soup.find_all("a"):
            if ('.zip' in link.get('href', []) and 'global' in link['href']):
                version = link['href'].split('/')[-1].split('.zip')[-2]
                self.firmware_versions.append((unquote(version), link))
        self.firmware_versions_frame_label.grid_forget()
        if len(self.firmware_versions) > 0:
            self.display_firmware_versions(self.firmware_versions)
        else:

            messagebox.showerror("Connection Error",
                                 "Could not fetch firmware versions")

    def fetch_key_versions(self):
        url = "https://github.com/Viren070/SwitchFirmwareKeysInstaller/blob/main/Keys/keys.md/"
        try:
            page = requests.get(url)
        except Exception as error:
            self.error_fetching_versions = True
            self.error_encountered = error
            return
        soup = BeautifulSoup(page.content, "html.parser")

        self.key_versions = []

        for link in soup.find_all("a"):

            if '.keys' in link.get('href', []):
                version = re.sub('<[^>]+>', '', str(link))
                self.key_versions.append((unquote(version), link))

        self.key_versions_frame_label.grid_forget()
        if len(self.key_versions) > 0:
            self.display_key_versions(self.key_versions)
        else:
            messagebox.showerror("Connection Error",
                                 "Could not fetch key versions")

    def display_firmware_versions(self, versions):
        for widget in self.firmware_versions_frame.winfo_children():
            widget.grid_forget()

        for i, (version, link) in enumerate(versions):
            version_label = customtkinter.CTkLabel(
                self.firmware_versions_frame, text=f"{version} - Latest" if i == 0 else version)
            version_label.grid(row=i, column=0, pady=10, sticky="W")
            version_button = customtkinter.CTkButton(
                self.firmware_versions_frame, text="Download", command=lambda link=link: self.start_installation(link, mode="Firmware"))
            version_button.grid(row=i, column=1, pady=10, sticky="E")
        self.fetched_versions += 1

    def display_key_versions(self, versions):
        for widget in self.key_versions_frame.winfo_children():
            widget.grid_forget()
        for i, (version, link) in enumerate(versions):
            version_label = customtkinter.CTkLabel(
                self.key_versions_frame, text=f"{version} - Latest" if i == 0 else version)
            version_label.grid(row=i, column=0, pady=10, sticky="W")
            version_button = customtkinter.CTkButton(
                self.key_versions_frame, text="Download", command=lambda link=link: self.start_installation(link, mode="Keys"))
            version_button.grid(row=i, column=1, pady=10, sticky="E")
        self.fetched_versions += 1

    def start_installation(self, link, mode):
        self.tabview.set("Downloads")
        if mode == "Both":
            if self.key_installation_in_progress or self.firmware_installation_in_progress:
                messagebox.showerror(
                    "Error", "There is already a firmware or key installation in progress!")
                return

            Thread(target=self.install_both, args=(link,)).start()
        elif mode == "Keys":
            if self.key_installation_in_progress:
                messagebox.showerror(
                    "Error", "There is already a key installation in progress!")
                return

            Thread(target=self.start_key_installation,
                             args=(link,)).start()
        elif mode == "Firmware":
            if self.firmware_installation_in_progress:
                messagebox.showerror(
                    "Error", "There is already a firmware installation in progress!")
                return

            Thread(
                target=self.start_firmware_installation, args=(link,)).start()

    def install_both(self, links):
        self.start_key_installation(links[0])
        self.start_firmware_installation(links[1])

    def start_key_installation(self, link):
        self.downloads_in_progress += 1
        self.key_installation_in_progress = True
        try:
            download_result = self.download_from_link(link['href'].replace(
                "\\", "").replace('"', ''), re.sub('<[^>]+>', '', str(link)))
        except Exception as error:
            messagebox.showerror("Error", error)
            self.key_installation_in_progress = False
            return
        if download_result is not None:
            downloaded_file = download_result[0]
            status_frame = download_result[1]
            if self.emulator_choice.get() == "Both":
                try:
                    self.install_keys("Yuzu", downloaded_file, status_frame)
                    self.install_keys("Ryujinx", downloaded_file, status_frame)
                except Exception as error:
                    messagebox.showerror("Error", error)
                    self.key_installation_in_progress = False
                    return
            else:
                try:
                    self.install_keys(self.emulator_choice.get(),
                                      downloaded_file, status_frame)
                except Exception as error:
                    messagebox.showerror("Error", error)
                    self.key_installation_in_progress = False
                    return

            status_frame.finish_installation()

            if self.delete_download.get():
                os.remove(downloaded_file)
        self.key_installation_in_progress = False

    def install_keys(self, emulator, keys, status_frame=None):
        if status_frame is not None:
            status_frame.complete_download(emulator)
        dst_folder = os.path.join(os.path.join(os.getenv('APPDATA'), emulator), "keys") if emulator == "Yuzu" else os.path.join(
            os.path.join(os.getenv('APPDATA'), emulator), "system")
        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)
        dst_file = os.path.join(dst_folder, "prod.keys")
        if os.path.exists(dst_file):
            os.remove(dst_file)
        copy(keys, dst_folder)
        if status_frame is not None:
            status_frame.update_extraction_progress(1)

    def start_firmware_installation(self, link):
        self.downloads_in_progress += 1
        self.firmware_installation_in_progress = True
        try:
            download_result = self.download_from_link(
                link['href'], unquote(link['href'].split('/')[-1].split('.zip')[-2]))
        except Exception as error:
            messagebox.showerror("Error", error)
            self.firmware_installation_in_progress = False
            return
        if download_result is not None:
            downloaded_file = download_result[0]
            status_frame = download_result[1]
            if self.emulator_choice.get() == "Both":
                try:
                    self.install_firmware(
                        "Yuzu", downloaded_file, status_frame)
                    self.install_firmware(
                        "Ryujinx", downloaded_file, status_frame)
                    status_frame.finish_installation()
                except Exception as error:
                    messagebox.showerror("ERROR", f"{error}")
                    status_frame.installation_interrupted(error)
                    self.firmware_installation_in_progress = False
                    return
            else:
                try:
                    self.install_firmware(
                        self.emulator_choice.get(), downloaded_file, status_frame)
                    status_frame.finish_installation()
                except Exception as error:
                    messagebox.showerror("Error", error)
                    status_frame.installation_interrupted(error)
                    self.firmware_installation_in_progress = False

            if self.delete_download.get():
                os.remove(downloaded_file)

        self.firmware_installation_in_progress = False

    def install_firmware(self, emulator, firmware_source, status_frame=None):
        emulator_folder = os.path.join(os.getenv('APPDATA'), emulator)
        if status_frame is not None:
            status_frame.complete_download(emulator)
        if emulator == "Ryujinx":
            install_directory = os.path.join(
                emulator_folder, r'bis\system\Contents\registered')
        elif emulator == "Yuzu":
            install_directory = os.path.join(
                emulator_folder, r'nand\system\Contents\registered')

        _, ext = os.path.splitext(firmware_source)
        with open(firmware_source, 'rb') as file:
            if ext == ".zip":

                with ZipFile(file) as archive:
                    self.extract_firmware_from_zip(
                        archive, install_directory, emulator, status_frame)
            else:
                raise Exception("Error: Firmware file is not a zip file.")

    def install_keys_button_wrapper(self):
        Thread(target=self.start_key_installation_custom).start()

    def start_key_installation_custom(self, path_to_key = None, status_frame = None):
        if self.key_installation_in_progress:
            messagebox.showerror(
                "Error", "There is already a key installation in progress. Please cancel the current installation to continue")
            return
        if path_to_key is None: path_to_key = filedialog.askopenfilename(
            filetypes=[("keys", "*.keys *.zip")])
        _, ext = os.path.splitext(path_to_key)
        if ext == "":
            return
        self.downloads_in_progress += 1
        if status_frame is None:
            status_frame = DownloadStatusFrame(
                self.downloads_frame, (path_to_key.split("/")[-1]), self)
            status_frame.grid(row=self.downloads_in_progress, pady=10, sticky="EW")
            status_frame.skip_to_installation()

        if ext == ".zip":
            try:
                self.tabview.set("Downloads")
                path_to_extracted_key = self.extract_keys_from_custom_zip(
                    path_to_key, status_frame)
            except Exception as Error:
                messagebox.showerror("Error", Error)
                status_frame.installation_interrupted(Error)
                return
        elif ext == ".keys":
            path_to_extracted_key = path_to_key
        else:
            messagebox.showerror(
                "Error", "Invalid filetype; should only be a zip file or a .keys file")
            status_frame.destroy()
            self.downloads_in_progress -= 1
            return
        self.key_installation_in_progress = True

        self.tabview.set("Downloads")
        try:
            if self.emulator_choice.get() != "Both":
                self.install_keys(self.emulator_choice.get(),
                                  path_to_extracted_key, status_frame)
            else:
                self.install_keys("Yuzu", path_to_extracted_key, status_frame)
                self.install_keys(
                    "Ryujinx", path_to_extracted_key, status_frame)
        except Exception as Error:
            messagebox.showerror("Error", Error)
            self.key_installation_in_progress = False
            return
        rmtree(self.temp_directory)
        status_frame.finish_installation()
        self.key_installation_in_progress = False

    def extract_keys_from_custom_zip(self, zip_location, status_frame):
        self.temp_directory = os.path.join(os.getenv("TEMP"), "Emulator Manager Extracts")
        with open(zip_location, 'rb') as file:

            with ZipFile(file) as archive:
                return self.extract_keys_from_zip(archive, self.temp_directory, status_frame)
        

    def extract_keys_from_zip(self, archive, extract_location, status_frame):
        self.delete_files_and_folders(extract_location)
        os.makedirs(extract_location, exist_ok=True)
        total_files = len(archive.namelist())
        extracted_files = 0
        status_frame.install_status_label.configure(
            text="Status: Extracting keys...")
        for entry in archive.infolist():
            if entry.filename.endswith('.keys'):
                if os.path.exists(os.path.join(extract_location, entry.filename)):
                    os.remove(os.path.join(extract_location, entry.filename))
                file = entry.filename
                extracted_file = os.path.join(extract_location, file)
                with open(extracted_file, 'wb') as f:
                    f.write(archive.read(entry))
                extracted_files += 1
            else:
                total_files -= 1
            if total_files == 0:
                raise Exception("ZIP file does not contain any .keys files")
            status_frame.update_extraction_progress(
                extracted_files / total_files)
        key_location = os.path.join(extract_location, "prod.keys")
        if os.path.exists(key_location):
            return key_location
        else:
            raise Exception("prod.keys not found within .ZIP file.")

    def install_from_zip_button_wrapper(self):
        Thread(
            target=self.start_firmware_installation_from_custom_zip).start()

    def start_firmware_installation_from_custom_zip(self, path_to_zip=None, status_frame=None):
        if self.firmware_installation_in_progress:
            messagebox.showerror(
                "Error", "There is already a firmware installation in progress. Please cancel the current installation to continue")
            return
        if path_to_zip == None: path_to_zip = filedialog.askopenfilename(
            filetypes=[("Zip files", "*.zip")])
        if path_to_zip is not None and path_to_zip != "":
            self.downloads_in_progress += 1
            self.firmware_installation_in_progress = True
            self.tabview.set("Downloads")
            if status_frame is None:
                status_frame = DownloadStatusFrame(
                    self.downloads_frame, (path_to_zip.split("/")[-1]), self)
                status_frame.grid(row=self.downloads_in_progress,
                                pady=10, sticky="EW")
                status_frame.skip_to_installation()
            if self.emulator_choice.get() == "Both":
                try:
                    self.install_firmware("Yuzu", path_to_zip, status_frame)
                    self.install_firmware("Ryujinx", path_to_zip, status_frame)
                except Exception as error:
                    messagebox.showerror("Error", error)
                    status_frame.installation_interrupted(error)
                    self.firmware_installation_in_progress = False
                    return

            else:
                try:
                    self.install_firmware(
                        self.emulator_choice.get(), path_to_zip, status_frame)
                except Exception as error:
                    messagebox.showerror("Error", error)
                    status_frame.installation_interrupted(error)
                    self.firmware_installation_in_progress = False
                    return
            status_frame.finish_installation()
            self.firmware_installation_in_progress = False

    def start_firmware_installation_from_directory(self):
        if self.firmware_installation_in_progress:
            messagebox.showerror(
                "Error", "There is already a firmware installation in progress. Please cancel the current installation to continue")
            return

        messagebox.showinfo(
            "Sorry", "This feature has not been implemented yet")
        # firmware_directory = filedialog.askdirectory(mustexist=True)

    def extract_firmware_from_zip(self, archive, install_directory, emulator, status_frame=None):
        self.delete_files_and_folders(install_directory)
        total_files = len(archive.namelist())
        extracted_files = 0
        for entry in archive.infolist():
            if entry.filename.endswith('.nca') or entry.filename.endswith('.nca/00'):
                path_components = entry.filename.replace(
                    '.cnmt', '').split('/')
                nca_id = path_components[-1]

                if nca_id == '00':
                    nca_id = path_components[-2]

                if '.nca' in nca_id:
                    if emulator == "Ryujinx":
                        new_path = os.path.join(install_directory, nca_id)
                        os.makedirs(new_path, exist_ok=True)
                        with open(os.path.join(new_path, '00'), 'wb') as f:
                            f.write(archive.read(entry))
                    elif emulator == "Yuzu":
                        new_path = os.path.join(install_directory, nca_id)
                        os.makedirs(install_directory, exist_ok=True)
                        with open(new_path, 'wb') as f:
                            f.write(archive.read(entry))
                    extracted_files += 1
                    if status_frame is not None:
                        status_frame.update_extraction_progress(
                            extracted_files / total_files)

            else:

                raise Exception(
                    "Error: ZIP file is not a firmware file or contains other files.")

    def download_from_link(self, link, filename):

        download_status_frame = DownloadStatusFrame(
            self.downloads_frame, filename, self)
        download_status_frame.grid(
            row=self.downloads_in_progress, column=0, sticky="EW", pady=20)
        download_status_frame.install_status_label.configure(
            text="Status: Waiting for response...")
        filename = unquote(link.split('/')[-1])

        # link = "https://speed.hetzner.de/1GB.bin"
        headers = {
            'Accept-Encoding': 'identity'  # Disable compression
        }

        try:
            session = requests.Session()
            response = session.get(link, headers=headers, stream=True)
            response.raise_for_status()

        except requests.exceptions.MissingSchema as error:
            download_status_frame.installation_interrupted(
                "Error During Download")
            messagebox.showerror("Missing Schema Error", error)
            return

        except requests.exceptions.InvalidSchema as error:
            download_status_frame.installation_interrupted(
                "Error During Download")
            messagebox.showerror("Invalid Schema Error", error)
            print(error)
            return

        except requests.exceptions.ConnectionError as error:
            download_status_frame.installation_interrupted(
                "Error During Download")
            messagebox.showerror("Connection Error", error)
            return
        except Exception as error:
            download_status_frame.installation_interrupted(
                "Error During Download")
            messagebox.showerror("Unkown Error", error)
            return None
        download_status_frame.install_status_label.configure(
            text="Status: Downloading")
        # response=requests.get(link, headers=headers, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        file_path = os.path.join(os.getcwd(), filename)
        with BytesIO() as f:

            start_time = perf_counter()
            download_status_frame.start_time = perf_counter()
            download_status_frame.total_size = total_size
            download_status_frame.time_at_start_of_chunk = perf_counter()
            if total_size is None:
                f.write(response.content)
            else:
                downloaded_bytes = 0
                chunk_size = self.convert_to_bytes(self.chunk_size.get())
                for data in response.iter_content(chunk_size=chunk_size):
                    if download_status_frame.cancel_download_raised:
                        self.firmware_installation_in_progress = False
                        
                        download_status_frame.cancel_download_button.configure(
                text="Remove", command=download_status_frame.remove_status_frame)
                        return None

                    downloaded_bytes += len(data)
                    f.write(data)

                    download_status_frame.update_download_progress(
                        downloaded_bytes, chunk_size)

            if downloaded_bytes != total_size:
                download_status_frame.destroy()
                self.downloads_in_progress -= 1
                raise Exception(
                    f"File was not completely downloaded {(downloaded_bytes/1024/1024):.2f} MB / {(total_size/1024/1024):.2f} MB\n Exited after {(perf_counter() - start_time):.2f} s.")

            with open(file_path, 'wb') as file:
                file.write(f.getvalue())

        return file_path, download_status_frame

    def delete_files_and_folders(self, directory):
        for root, dirs, files in os.walk(directory, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for folder in dirs:
                os.rmdir(os.path.join(root, folder))

    def convert_to_bytes(self, value):
        if "KB" in value:
            return ( int(value.replace(" KB", "")) * 1024 )
        elif "MB" in value:
            return (int(value.replace(" MB", "")) * 1024**2)
        else:
            return 16000

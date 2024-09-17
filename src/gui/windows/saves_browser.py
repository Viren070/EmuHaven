import textwrap
from pathlib import Path
from urllib.parse import unquote

import customtkinter

from core.config import constants
from core.network.web import download_file_with_progress
from gui.handlers.progress.progress_handler import ProgressHandler
from gui.libs.CTkMessagebox import messagebox


class SavesBrowser(customtkinter.CTkToplevel):
    def __init__(self, master, title, saves_list, event_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)
        self.saves = saves_list
        self.downloading_save = False
        self.event_manager = event_manager
        self.progress_handler = ProgressHandler(self, widget="window")
        self.lift()  # lift window on top
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(30, self.build_frame)  # create widgets with slight delay, to avoid white flickering of background
        self.grab_set()  # make other windows not clickable

    def build_frame(self):
        self.resizable(False, True)
        self.minsize(415, 400)
        self.geometry("415x600")
        # Create a label for the title
        title_label = customtkinter.CTkLabel(self, text="Download Saves", font=customtkinter.CTkFont("Arial", 20), anchor="center")
        title_label.grid(row=0, column=0, sticky="nsew")

        # Create a label for the paragraph
        paragraph_label = customtkinter.CTkLabel(self, font=customtkinter.CTkFont("Arial", 15), anchor="center", text=textwrap.fill("Once the download is complete, the save file will be placed on your desktop. To install a save, right click then game in the emulator game list, "'open save folder'" and extract the downloaded archive there. Be sure to backup your current save file if you want to use it later!", 60))
        paragraph_label.grid(row=1, column=0, pady=20, sticky="nsew")

        # Create a vertically scrollable frame
        scrollable_frame = customtkinter.CTkScrollableFrame(self)
        scrollable_frame.grid(row=2, column=0, sticky="nsew")

        # make buttons expand to fill the entire width of the frame
        scrollable_frame.grid_columnconfigure(0, weight=1)

        for i, save in enumerate(self.saves):
            filename = unquote(save).split('/')[-1].split(".zip")[-2]

            # Create a button for the save
            save_button_text = textwrap.fill(filename, width=38)  # Insert newlines into the filename
            save_button = customtkinter.CTkButton(scrollable_frame, text=save_button_text, font=customtkinter.CTkFont("Arial", 20), command=lambda save=save: self.download_save_button_event(save))
            save_button.grid(row=i, column=0, padx=(2, 2), pady=5, sticky="ew")
            save_button.update_idletasks()
        # Configure the grid to allocate all extra space to the scrollable frame
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def download_save_button_event(self, save):
        if self.downloading_save:
            return
        self.downloading_save = True
        self.event_manager.add_event(
            event_id="download_save",
            func=self.download_save,
            kwargs={"save": save},
            error_functions=[lambda: messagebox.showerror(self, "Save Download", "An unexpected error occurred while attempting to download this save"), lambda: setattr(self, "downloading_save", False)],
        )

    def download_save(self, save):
        save_download_url = constants.GitHub.RAW_URL.value.format(
            owner=constants.Switch.SAVES_GH_REPO_OWNER.value,
            repo=constants.Switch.SAVES_GH_REPO_NAME.value,
            branch="main",
            path=f"{constants.Switch.SAVES_GH_REPO_PATH.value}/{save}",
        )
        self.progress_handler.start_operation(title=save, total_units=0, units="MiB", status="Downloading...")
        download_result = download_file_with_progress(
            download_url=save_download_url,
            download_path=Path.home() / "Desktop" / save,
            progress_handler=self.progress_handler,
        )

        self.downloading_save = False
        if not download_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self, "Save Download", f"An error occurred while attempting to download this save\n\n{download_result['message']}"),
                }
            }

        return {
            "message": {
                "function": messagebox.showsuccess,
                "arguments": (self, "Save Download", "The savefile was successfully downloaded to your desktop"),
            }
        }

    def on_closing(self):
        self.grab_release()
        self.destroy()  # destroy window

import customtkinter 

from urllib.parse import unquote
import textwrap

class SavesBrowser(customtkinter.CTkToplevel):
    def __init__(self, title, saves, title_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)
        self.saves = saves
        self.build_frame()
        self.grab_set()
        self.focus_set()

    def build_frame(self):
        self.resizable(False, True)
        self.minsize(400, 400)
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

        for i, save in enumerate(self.saves):
            filename = unquote(save).split('/')[-1].split(".zip")[-2]

            # Create a button for the save
            save_button_text = textwrap.fill(filename, width=42)  # Insert newlines into the filename
            save_button = customtkinter.CTkButton(scrollable_frame, text=save_button_text, font=customtkinter.CTkFont("Arial", 20), anchor="w", command=lambda save=save: self.download_save(save))
            save_button.grid(row=i, column=0, padx=(2,10), pady=5, sticky="ew")
            
        # Configure the grid to allocate all extra space to the scrollable frame
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
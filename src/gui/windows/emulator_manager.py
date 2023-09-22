import os
import shutil
from sys import exit as sysexit
from tkinter import messagebox

import customtkinter
from PIL import Image

from gui.frames.dolphin.dolphin_frame import DolphinFrame
from gui.frames.settings.settings_frame import SettingsFrame
from gui.frames.yuzu.yuzu_frame import YuzuFrame
from settings.app_settings import load_customtkinter_themes
from settings.settings import Settings
from settings.metadata import Metadata
from utils.auth_token_manager import delete_token_file


class EmulatorManager(customtkinter.CTk):
    def __init__(self, root_dir, open_app_settings=False, pos=["",""]):
        self.just_opened = True
        super().__init__()
        self.settings = Settings(self, root_dir)
        self.metadata = Metadata(self, self.settings)
        self.version = "v0.11.2"
        self.root_dir = root_dir
        self.x = pos[0]
        self.y = pos[1]
        try:
            self.define_images()
        except FileNotFoundError:
            messagebox.showerror("Image Error", "The image files could not be found, try re-downloading the latest release from the GitHub repository.", master=self)
            return
        self.build_gui()
        self.just_opened = False
        if open_app_settings:
            self.select_frame_by_name("settings")
            self.settings_frame.select_settings_frame_by_name("app")
            
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainloop()
    def define_images(self):
        self.dolphin_logo = customtkinter.CTkImage(Image.open(self.settings.get_image_path("dolphin_logo")), size=(26, 26))
        self.dolphin_banner =  customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("dolphin_banner_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("dolphin_banner_dark")), size=(276, 129))
        self.yuzu_logo = customtkinter.CTkImage(Image.open(self.settings.get_image_path("yuzu_logo")), size=(26, 26))
        self.yuzu_mainline = customtkinter.CTkImage(Image.open(self.settings.get_image_path("yuzu_mainline")), size=(120, 40))
        self.yuzu_early_access = customtkinter.CTkImage(Image.open(self.settings.get_image_path("yuzu_early_access")), size=(120, 40))
        self.play_image = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("play_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("play_dark")), size=(20, 20))
        self.settings_image =  customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("settings_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("settings_dark")), size=(20, 20))
        self.lock_image =  customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("padlock_light")),
                                                     dark_image=Image.open(self.settings.get_image_path("padlock_dark")), size=(20, 20))
    def build_gui(self):
        self.resizable(False, False)  # disable resizing of window
        self.title("Emulator Manager")  # set title of window
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.minsize(1100,570) # set the minimum size of the window 
        self.geometry("1100x500+{}+{}".format(self.x, self.y))
        
        # create navigation frame 
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        # create navigation frame title. 
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text= f"Emulator Manager {self.version}",
                                                             compound="left", padx=5, font=customtkinter.CTkFont(size=12, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        self.navigation_frame_label.bind('<Double-Button-1>', command=lambda event: messagebox.showinfo("About", f"Emulator Manager {self.version}, made by Viren070 on GitHub."))
        # create navigation menu buttons
        self.dolphin_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image = self.dolphin_logo, border_spacing=10, text="Dolphin",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   anchor="w", command=self.dolphin_button_event)
        self.dolphin_button.grid(row=1, column=0, sticky="ew")

        self.yuzu_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image = self.yuzu_logo, border_spacing=10, text="Yuzu",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), 
                                                      anchor="w", command=self.yuzu_button_event)
        self.yuzu_button.grid(row=2, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image = self.settings_image, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                                      anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=6, column=0, sticky="ew")
        
        self.yuzu_frame = YuzuFrame(self, self.settings, self.metadata)
        self.dolphin_frame = DolphinFrame(self, self.settings, self.metadata)
        self.settings_frame = SettingsFrame(self, self.settings)
        self.settings.yuzu.refresh_app_settings = self.settings_frame.app_settings_frame.refresh_settings
    def dolphin_button_event(self):
        self.select_frame_by_name("dolphin")

    def yuzu_button_event(self):
        self.select_frame_by_name("yuzu")

    def settings_button_event(self):
        self.select_frame_by_name("settings")
    
    def select_frame_by_name(self, name):
        if not self.just_opened and ( self.settings_changed()) and name != "settings":
            if messagebox.askyesno("Confirmation", "You have unsaved changes in the settings. If you leave now, the changes you made will be discarded. Continue?"):
                self.revert_settings()
            else:
                return 
        self.settings_button.configure(fg_color=self.settings_button.cget("hover_color") if name == "settings" else "transparent")
        self.dolphin_button.configure(fg_color=self.dolphin_button.cget("hover_color") if name == "dolphin" else "transparent")
        self.yuzu_button.configure(fg_color=self.yuzu_button.cget("hover_color") if name == "yuzu" else "transparent")
        
        # show selected frame
        if name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")       
        else:
            self.settings_frame.grid_forget()
            self.settings_frame.select_settings_frame_by_name(None)

        if name == "dolphin":
            self.dolphin_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.dolphin_frame.grid_forget()
            self.dolphin_frame.select_dolphin_frame_by_name(None)
        if name == "yuzu":
            self.yuzu_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.yuzu_frame.grid_forget()
            self.yuzu_frame.select_yuzu_frame_by_name(None)
        
        
    def settings_changed(self):
        return self.settings_frame.settings_changed()
    def revert_settings(self):
        self.settings_frame.revert_settings()
    def restart(self):
        for after_id in self.tk.eval('after info').split():
            self.after_cancel(after_id)
        pos = [self.winfo_x(), self.winfo_y()]
        self.destroy()
        load_customtkinter_themes(os.path.join(self.root_dir, "themes"))
        EmulatorManager(self.root_dir, True, pos)
        
    def on_closing(self):
        if (self.dolphin_frame.dolphin.running or self.yuzu_frame.yuzu.running):
            messagebox.showerror("Emulator Manager", "Please close any emulators before attempting to exit.")
            return 
        temp_folder = os.path.join(os.getenv("TEMP"), "Emulator Manager")
        if os.path.exists(temp_folder):
            try:
                shutil.rmtree(temp_folder)
            except:
                pass
        delete_token_file()
        self.destroy()
        sysexit()
        
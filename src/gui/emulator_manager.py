from hashlib import pbkdf2_hmac
from tkinter import messagebox

import customtkinter
from PIL import Image

from gui.frames.dolphin_frame import DolphinFrame
from gui.frames.settings_frame import SettingsFrame
from gui.frames.yuzu_frame import YuzuFrame
from gui.password_dialog import PasswordDialog
from settings.settings import Settings


class EmulatorManager(customtkinter.CTk):
    def __init__(self, root_dir, open_app_settings=False):
        self.just_opened = True
        super().__init__()
        self.settings = Settings(self, root_dir)
        self.version = "v0.8.0"
        try:
            self.define_images()
        except FileNotFoundError as error:
            messagebox.showerror("Image Error", "The image files could not be found, try re-downloading the latest release from the GitHub repository.", master=self)
            return
        self.build_gui()
        self.just_opened = False
        if open_app_settings:
            self.select_frame_by_name("settings")
            self.settings_frame.select_settings_frame_by_name("app")
        self.mainloop()
    def define_images(self):
        self.dolphin_image = customtkinter.CTkImage(Image.open(self.settings.get_image_path("dolphin_logo")), size=(26, 26))
        self.yuzu_image = customtkinter.CTkImage(Image.open(self.settings.get_image_path("yuzu_logo")), size=(26, 26))
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
        
        self.minsize(800,500) # set the minimum size of the window 
        
        
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
        self.dolphin_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image = self.dolphin_image, border_spacing=10, text="Dolphin",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.dolphin_button_event)
        self.dolphin_button.grid(row=1, column=0, sticky="ew")

        self.yuzu_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image = self.yuzu_image, border_spacing=10, text="Yuzu",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.yuzu_button_event)
        self.yuzu_button.grid(row=2, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image = self.settings_image, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=6, column=0, sticky="ew")
        
        self.yuzu_frame = YuzuFrame(self, self.settings)
        self.dolphin_frame = DolphinFrame(self, self.settings)
        self.settings_frame = SettingsFrame(self, self.settings)
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
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.dolphin_button.configure(fg_color=("gray75", "gray25") if name == "dolphin" else "transparent")
        self.yuzu_button.configure(fg_color=("gray75", "gray25") if name == "yuzu" else "transparent")
        
        # show selected frame
        if name == "settings":

            self.minsize(1100,500)
            self.settings_button.configure(fg_color=("gray75", "gray25"))
            self.settings_frame.grid(row=0, column=1, sticky="nsew")       
        else:
            self.settings_frame.grid_forget()
            self.settings_frame.select_settings_frame_by_name(None)
            self.minsize(800,500)

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
        to_return = self.settings_frame.settings_changed()
        return to_return
    def revert_settings(self):
        self.settings_frame.revert_settings()
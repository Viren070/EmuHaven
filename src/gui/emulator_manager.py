import os
import shutil
import webbrowser
from sys import exit as sysexit
from threading import Thread
from packaging import version

import customtkinter
from customtkinter import ThemeManager
from PIL import Image

from gui.frames.dolphin.dolphin_frame import DolphinFrame
from gui.frames.ryujinx.ryujinx_frame import RyujinxFrame
from gui.frames.settings.settings_frame import SettingsFrame
from gui.frames.yuzu.yuzu_frame import YuzuFrame
from gui.frames.xenia.xenia_frame import XeniaFrame
from gui.libs import messagebox

from core.assets import Assets
from core.settings import Settings
from core.versions import Versions
from core.cache import Cache
from core.paths import Paths
from core.utils.thread_event_manager import ThreadEventManager
from core import constants


class EmulatorManager(customtkinter.CTk):
    def __init__(self, paths: Paths, settings: Settings, versions: Versions, cache: Cache, assets: Assets, opening_menu=""):
        self.just_opened = True
        super().__init__()
        self.paths, self.settings, self.versions, self.cache, self.assets = paths, settings, versions, cache, assets
        self.event_manager = ThreadEventManager(self)
        self.version = version.parse(constants.App.VERSION.value)
        self.build_gui()
        self.just_opened = False
        self.select_frame_by_name(opening_menu)
  
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def build_gui(self):
        self.resizable(True, True)  # disable resizing of window
        self.title(constants.App.NAME.value)  # set title of window

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.minsize(1100, 570)  # set the minimum size of the window
        self.geometry("1100x500")

        # Create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(1, weight=1)
        self.navigation_frame.grid_columnconfigure(0, weight=1)
        
        # Create navigation frame title.
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=f"{constants.App.NAME.value} v{self.version.public}",
                                                             compound="left", padx=5, font=customtkinter.CTkFont(size=12, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        self.navigation_frame_label.bind('<Double-Button-1>', command=lambda event: messagebox.showinfo(self, "About", f"{constants.App.NAME.value} v{self.version}, made by {constants.App.AUTHOR.value} on GitHub."))

        # Create scrollable frame in the middle
        scrollable_frame = customtkinter.CTkScrollableFrame(self.navigation_frame, fg_color="transparent")
        scrollable_frame.grid(row=1, column=0, sticky="nsew")

        # Create navigation menu buttons
        text_color = ThemeManager.theme["CTkLabel"]["text_color"]
        self.dolphin_button = customtkinter.CTkButton(scrollable_frame, corner_radius=0, height=40, width=50, image=self.assets.dolphin_logo, border_spacing=10, text="Dolphin",
                                                      fg_color="transparent", text_color=text_color,
                                                      anchor="w", command=self.dolphin_button_event)
        self.dolphin_button.grid(row=0, column=0, sticky="ew")

        self.yuzu_button = customtkinter.CTkButton(scrollable_frame, corner_radius=0, height=40, image=self.assets.yuzu_logo, border_spacing=10, text="Yuzu",
                                                   fg_color="transparent", text_color=text_color,
                                                   anchor="w", command=self.yuzu_button_event)
        self.yuzu_button.grid(row=1, column=0, sticky="ew")

        self.ryujinx_button = customtkinter.CTkButton(scrollable_frame, corner_radius=0, height=40, image=self.assets.ryujinx_logo, border_spacing=10, text="Ryujinx",
                                                      fg_color="transparent", text_color=text_color,
                                                      anchor="w", command=self.ryujinx_button_event)
        self.ryujinx_button.grid(row=2, column=0, sticky="ew")

        self.xenia_button = customtkinter.CTkButton(scrollable_frame, corner_radius=0, height=40, image=self.assets.xenia_logo, border_spacing=10, text="Xenia",
                                                    fg_color="transparent", text_color=text_color,
                                                    anchor="w", command=lambda: self.select_frame_by_name("xenia"))
        self.xenia_button.grid(row=3, column=0, sticky="ew")
        # Set column weights of scrollable_frame to make buttons expand
        scrollable_frame.grid_columnconfigure(0, weight=1)

        socials_frame = customtkinter.CTkFrame(self.navigation_frame, corner_radius=0, border_width=0, fg_color="transparent")
        socials_frame.grid(row=2, column=0, padx=(1, 0))
        socials_frame.grid_columnconfigure(0, weight=1)
    
        github_button = customtkinter.CTkLabel(socials_frame, height=0, width=0, text="", image=self.assets.github_icon)
        github_button.grid(row=0, column=0, padx=4, pady=20)
        github_button.bind("<Button-1>", lambda event: self.show_github())

        discord_button = customtkinter.CTkLabel(socials_frame, height=0, width=0, text="", image=self.assets.discord_icon)
        discord_button.grid(row=0, column=1, padx=4, pady=20)
        discord_button.bind("<Button-1>", lambda event: self.show_discord_invite())
        
        kofi_button = customtkinter.CTkLabel(socials_frame, height=0, width=0, text="", image=self.assets.kofi_icon)
        kofi_button.grid(row=0, column=2, padx=4, pady=20)
        kofi_button.bind("<Button-1>", lambda event: self.show_kofi_page())
        
        # Create settings button at the bottom
        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image=self.assets.settings_image, border_spacing=10, text="Settings",
                                                       fg_color="transparent", text_color=text_color,
                                                       anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=3, column=0, sticky="ew")

        self.yuzu_frame = YuzuFrame(self, paths=self.paths, settings=self.settings, versions=self.versions, cache=self.cache, assets=self.assets, event_manager=self.event_manager)
        self.dolphin_frame = DolphinFrame(self, paths=self.paths, settings=self.settings, versions=self.versions, cache=self.cache, assets=self.assets, event_manager=self.event_manager)
        self.ryujinx_frame = RyujinxFrame(self, paths=self.paths, settings=self.settings, versions=self.versions, cache=self.cache, assets=self.assets, event_manager=self.event_manager)
        self.xenia_frame = XeniaFrame(self, paths=self.paths, settings=self.settings, versions=self.versions, cache=self.cache, assets=self.assets, event_manager=self.event_manager)
        self.settings_frame = SettingsFrame(self, settings=self.settings, paths=self.paths, assets=self.assets, event_manager=self.event_manager)

    def show_github(self):
        if messagebox.askyesno(self, "GitHub", f"Would you like to visit the {constants.App.NAME.value} GitHub repository?\n\nBy visiting the GitHub repository, you can get the latest updates and features.\nYou can also leave a star to support me") == "yes":
            webbrowser.open(constants.App.GITHUB.value)
    
    def show_discord_invite(self):
        if messagebox.askyesno(self, "Discord Invite", f"Would you like to join the {constants.App.NAME.value} Discord server?\n\nBy joining the discord server, you can get help with any issues you may have, as well as get notified of new releases and features") == "yes":
            webbrowser.open(constants.App.DISCORD.value)
        
    def show_kofi_page(self):
        if messagebox.askyesno(self, "Support", f"Would you like to support the development of {constants.App.NAME.value} by donating on Ko-fi?\n\nIf you click yes, your default web browser will open the Ko-fi page.") == "yes":
            webbrowser.open(constants.App.KOFI.value)

    def dolphin_button_event(self):
        self.select_frame_by_name("dolphin")

    def yuzu_button_event(self):

        self.select_frame_by_name("yuzu")

    def ryujinx_button_event(self):
        self.select_frame_by_name("ryujinx")

    def settings_button_event(self):
        self.select_frame_by_name("settings")

    def select_frame_by_name(self, name):
        if not self.just_opened and (self.settings_changed()) and name != "settings":
            if messagebox.askyesno("Confirmation", "You have unsaved changes in the settings. If you leave now, the changes you made will be discarded. Continue?"):
                self.revert_settings()
            else:
                return
        self.settings_button.configure(fg_color=self.settings_button.cget("hover_color") if name == "settings" else "transparent")
        self.dolphin_button.configure(fg_color=self.dolphin_button.cget("hover_color") if name == "dolphin" else "transparent")
        self.yuzu_button.configure(fg_color=self.yuzu_button.cget("hover_color") if name == "yuzu" else "transparent")
        self.ryujinx_button.configure(fg_color=self.ryujinx_button.cget("hover_color") if name == "ryujinx" else "transparent")
        self.xenia_button.configure(fg_color=self.xenia_button.cget("hover_color") if name == "xenia" else "transparent")

        # show selected frame
        if name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
            self.settings_frame.select_settings_frame_by_name("app")
        else:
            self.settings_frame.grid_forget()
            self.settings_frame.select_settings_frame_by_name(None)

        if name == "dolphin":
            self.dolphin_frame.grid(row=0, column=1, sticky="nsew")
            self.dolphin_frame.select_frame_by_name("start")
        else:
            self.dolphin_frame.grid_forget()
            self.dolphin_frame.select_frame_by_name(None)
        if name == "yuzu":
            self.yuzu_frame.grid(row=0, column=1, sticky="nsew")
            self.yuzu_frame.select_frame_by_name("start")
        else:
            self.yuzu_frame.grid_forget()
            self.yuzu_frame.select_frame_by_name(None)
        if name == "ryujinx":
            self.ryujinx_frame.grid(row=0, column=1, sticky="nsew")
            self.ryujinx_frame.select_frame_by_name("start")
        else:
            self.ryujinx_frame.grid_forget()
            self.ryujinx_frame.select_frame_by_name(None)
        if name == "xenia":
            self.xenia_frame.grid(row=0, column=1, sticky="nsew")
            self.xenia_frame.select_frame_by_name("start")
        else:
            self.xenia_frame.grid_forget()
            self.xenia_frame.select_frame_by_name(None)

    def settings_changed(self):
        return self.settings_frame.settings_changed()

    def revert_settings(self):
        self.settings_frame.revert_settings()


    def on_closing(self):
       
        ongoing_events = [event["id"] for event in self.event_manager.events]
        if ongoing_events:
            messagebox.showwarning(self, "Warning", f"There are ongoing events. Please wait for them to finish before closing the application.\n\nOngoing events: {', '.join(ongoing_events)}")
            return
        temp_folder = os.path.join(os.getenv("TEMP"), "Emulator Manager")
        if os.path.exists(temp_folder):
            try:
                shutil.rmtree(temp_folder)
            except PermissionError:
                pass
        sysexit()

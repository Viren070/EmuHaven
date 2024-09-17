import os
import shutil
import webbrowser
import sys
from pathlib import Path


import customtkinter
from customtkinter import ThemeManager
from packaging import version

from core.config import constants
from core.config.assets import Assets
from core.config.cache import Cache
from core.config.paths import Paths
from core.config.settings import Settings
from core.logging.logger import Logger
from gui.handlers.thread_event_manager import ThreadEventManager
from core.network.github import get_latest_release_with_asset
from core.network import web
from core.config.versions import Versions
from gui.frames.dolphin.dolphin_frame import DolphinFrame
from gui.frames.ryujinx.ryujinx_frame import RyujinxFrame
from gui.frames.settings.settings_frame import SettingsFrame
from gui.frames.xenia.xenia_frame import XeniaFrame
from gui.frames.yuzu.yuzu_frame import YuzuFrame
from gui.libs.CTkMessagebox import messagebox


class EmuHaven(customtkinter.CTk):
    def __init__(self, paths: Paths, settings: Settings, versions: Versions, cache: Cache, assets: Assets, opening_menu=""):
        self.just_opened = True
        self.logger = Logger(__name__).get_logger()
        super().__init__()
        self.paths, self.settings, self.versions, self.cache, self.assets = paths, settings, versions, cache, assets
        self.event_manager = ThreadEventManager(self)
        self.version = version.parse(constants.App.VERSION.value)
        self.build_gui()
        self.just_opened = False
        self.select_frame_by_name(opening_menu)
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.after(200, self.check_currentdir_permissions)
        self.after(400, self.check_for_updates)
        self.after(600, self.show_announcements)

    def show_announcements(self):
        announcements_url = constants.GitHub.RAW_URL.value.format(
            owner=constants.App.GH_OWNER.value,
            repo=constants.App.GH_REPO.value,
            branch="main",
            path="announcements.json"
        )
        response = web.get(announcements_url)
        if not response["status"]:
            self.logger.error(f"Failed to get announcements: {response['message']}")
            return 
        try:
            announcements = response["response"].json()
        except Exception as error:
            self.logger.error(f"Failed to parse announcements:\n {response["response"].text}\n{error}")
            return
        if not announcements:
            return 
        for announcement_id, announcement in announcements.items():
            if announcement_id not in self.settings.announcements_read:
                messagebox.showinfo(self, announcement["title"], announcement["message"])
                self.settings.announcements_read.append(announcement_id)
        self.settings.save()
        
    def check_currentdir_permissions(self):
        self.logger.info("Checking current directory permissions")
        try:
            test = Path("test.txt")
            with open(test, "w", encoding="utf-8") as file:
                file.write("Test")
            test.unlink(missing_ok=True)
            self.logger.info("Current directory is writable")
        except PermissionError:
            messagebox.showerror(self, "Warning", "You do not have permission to write to the current directory. Please run the application as an administrator or move the application to a directory where you have write permissions.")
            self.destroy()

    def check_for_updates(self):
        # check if application is in executable mode or not
        if getattr(sys, "frozen", False) is False:
            return
        if self.settings.auto_app_updates is False:
            return
        latest_release = get_latest_release_with_asset(
            repo_owner=constants.App.GH_OWNER.value,
            repo_name=constants.App.GH_REPO.value,
            regex=constants.App.GH_ASSET_REGEX.value,
            include_prereleases=True,
        )

        if not latest_release["status"]:
            self.logger.error(f"Failed to get the latest release: {latest_release["message"]}")
            messagebox.showerror(self, "Error", f"Failed to get the latest release: {latest_release["message"]}")
            return

        current_version = self.version
        latest_version = version.parse(latest_release["release"]["version"])
        if current_version >= latest_version:
            self.logger.info(f"Current version {current_version} is greater than the latest version {latest_version}")
            return

        if messagebox.askyesno(self, "Update Available", f"An update is available. Would you like to download the latest version ({latest_version})?", icon="info") == "yes":
            webbrowser.open(f"https://github.com/{constants.App.GH_OWNER.value}/{constants.App.GH_REPO.value}/releases/tag/v{latest_version}")

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

        # Create frame in the middle
        frame = customtkinter.CTkFrame(self.navigation_frame, fg_color="transparent", corner_radius=0, border_width=0)
        frame.grid(row=1, column=0, sticky="nsew", padx=2)

        # Create navigation menu buttons
        text_color = ThemeManager.theme["CTkLabel"]["text_color"]
        self.dolphin_button = customtkinter.CTkButton(frame, corner_radius=0, height=50, image=self.assets.dolphin_logo, border_spacing=10, text="Dolphin",
                                                      fg_color="transparent", text_color=text_color,
                                                      anchor="w", command=self.dolphin_button_event)
        self.dolphin_button.grid(row=0, column=0, sticky="ew", padx=2)

        self.yuzu_button = customtkinter.CTkButton(frame, corner_radius=0, height=40, image=self.assets.yuzu_logo, border_spacing=10, text="Yuzu",
                                                   fg_color="transparent", text_color=text_color,
                                                   anchor="w", command=self.yuzu_button_event)
        self.yuzu_button.grid(row=1, column=0, sticky="ew", padx=2)

        self.ryujinx_button = customtkinter.CTkButton(frame, corner_radius=0, height=40, image=self.assets.ryujinx_logo, border_spacing=10, text="Ryujinx",
                                                      fg_color="transparent", text_color=text_color,
                                                      anchor="w", command=self.ryujinx_button_event)
        self.ryujinx_button.grid(row=2, column=0, sticky="ew", padx=2)

        self.xenia_button = customtkinter.CTkButton(frame, corner_radius=0, height=40, image=self.assets.xenia_logo, border_spacing=10, text="Xenia",
                                                    fg_color="transparent", text_color=text_color,
                                                    anchor="w", command=lambda: self.select_frame_by_name("xenia"))
        self.xenia_button.grid(row=3, column=0, sticky="ew", padx=2)
        # Set column weights of frame to make buttons expand
        frame.grid_columnconfigure(0, weight=1)

        socials_frame = customtkinter.CTkFrame(self.navigation_frame, corner_radius=0, border_width=0, fg_color="transparent")
        socials_frame.grid(row=2, column=0, padx=5, pady=10)
        socials_frame.grid_columnconfigure(0, weight=1)

        icon_frame = customtkinter.CTkFrame(socials_frame, corner_radius=0, border_width=0, fg_color="transparent")
        icon_frame.grid(row=0, column=0, padx=10, pady=5)

        github_button = customtkinter.CTkLabel(icon_frame, height=0, width=0, text="", image=self.assets.github_icon, )
        github_button.grid(row=0, column=0, padx=4, pady=0)
        github_button.bind("<Button-1>", lambda event: self.show_github())

        discord_button = customtkinter.CTkLabel(icon_frame, height=0, width=0, text="", image=self.assets.discord_icon)
        discord_button.grid(row=0, column=1, padx=10, pady=0)
        discord_button.bind("<Button-1>", lambda event: self.show_discord_invite())

        kofi_button = customtkinter.CTkLabel(socials_frame, height=0, width=0, text="", image=self.assets.kofi_button)
        kofi_button.grid(row=1, column=0, padx=10, pady=10)
        kofi_button.bind("<Button-1>", lambda event: self.show_kofi_page())

        # Create settings button at the bottom
        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, image=self.assets.settings_image, border_spacing=10, text="Settings",
                                                       fg_color="transparent", text_color=text_color,
                                                       anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=3, column=0, sticky="ew", padx=2, pady=2)

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
        if messagebox.askyesno(self, "Support", f"Would you like to support the development of {constants.App.NAME.value} by donating on Ko-fi?") == "yes":
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
            self.dolphin_frame.manage_games_frame.current_roms_frame.get_game_list_button_event(ignore_messages=True)
            self.dolphin_frame.grid(row=0, column=1, sticky="nsew")
            self.dolphin_frame.select_frame_by_name("start")
        else:
            self.dolphin_frame.grid_forget()
            self.dolphin_frame.select_frame_by_name(None)
        if name == "yuzu":
            self.yuzu_frame.firmware_keys_frame.request_fetch()
            self.yuzu_frame.grid(row=0, column=1, sticky="nsew")
            self.yuzu_frame.select_frame_by_name("start")
        else:
            self.yuzu_frame.grid_forget()
            self.yuzu_frame.select_frame_by_name(None)
        if name == "ryujinx":
            self.ryujinx_frame.firmware_keys_frame.request_fetch()
            self.ryujinx_frame.grid(row=0, column=1, sticky="nsew")
            self.ryujinx_frame.select_frame_by_name("start")
        else:
            self.ryujinx_frame.grid_forget()
            self.ryujinx_frame.select_frame_by_name(None)
        if name == "xenia":
            self.xenia_frame.manage_games_frame.current_roms_frame.get_game_list_button_event(ignore_messages=True)
            self.xenia_frame.grid(row=0, column=1, sticky="nsew")
            self.xenia_frame.select_frame_by_name("start")
        else:
            self.xenia_frame.grid_forget()
            self.xenia_frame.select_frame_by_name(None)

    def settings_changed(self):
        return self.settings_frame.settings_changed()

    def revert_settings(self):
        self.settings_frame.revert_settings()

    def close_app(self):
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
        self.destroy()

import os
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

import customtkinter
from CTkToolTip import CTkToolTip

from core.utils.github import get_rate_limit_status
from core.utils.thread_event_manager import ThreadEventManager
from gui.frames.settings.setting_modal import SettingModal
from gui.libs import messagebox
from gui.windows.github_login_window import GitHubLoginWindow


class AppSettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings, paths, assets, event_manager: ThreadEventManager):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.root_window = parent_frame.root_window
        self.updating_rate_limit = False
        self.event_manager = event_manager
        self.settings = settings
        self.parent_frame = parent_frame
        self.paths = paths
        self.assets = assets
        self.token_gen = None
        self.build_frame()

    def build_frame(self):
        self.settings_path = os.path.join(os.getenv("APPDATA"), "Emulator Manager", "config")
        self.settings_file = os.path.join(self.settings_path, 'settings.json')

        # create appearance and themes widgets for settings menu 'Appearance'
        self.grid_columnconfigure(0, weight=1)

        colour_themes = [str(theme.name).replace("-", " ").replace(".json", "").title() for theme in self.assets.get_list_of_themes()]
        colour_themes.append("Custom...")
        theme_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings,
                "id": "colour_theme_path",
                "type": "option_menu",
                "title": "Theme",
                "description": "Select a colour theme for the application.",
            },
            option_menu_options={
                "values": colour_themes,
            },
            custom_options={
                "update_function": self.change_colour_theme,
                "get_function": lambda: self.settings.colour_theme_path.stem.replace("-", " ").title()
            }
        )
        theme_setting.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        dark_mode_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings,
                "id": "dark_mode",
                "type": "switch",
                "title": "Dark Mode",
                "description": "Enable dark mode.",
            },
            custom_options={
                "update_function": self.set_dark_mode_setting,
            }
        )
        dark_mode_setting.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        delete_files_after_installing_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings,
                "id": "delete_files_after_installing",
                "type": "switch",
                "title": "Delete Files after installing",
                "description": "Delete downloaded files after installing.",
            },
        )
        delete_files_after_installing_setting.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        auto_app_updates_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings,
                "id": "auto_app_updates",
                "type": "switch",
                "title": "Auto App Updates",
                "description": "Automatically check for and install updates for applications.",
            },
        )
        auto_app_updates_setting.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        auto_emulator_updates_setting = SettingModal(
            master=self,
            settings=self.settings,
            setting_options={
                "object": self.settings,
                "id": "auto_emulator_updates",
                "type": "switch",
                "title": "Auto Emulator Updates",
                "description": "Automatically check for and install updates for emulators.",
            },
        )
        auto_emulator_updates_setting.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        self.actions_frame = customtkinter.CTkFrame(self, fg_color="transparent", corner_radius=10, border_width=2)
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid(row=14, sticky="ew", padx=10, pady=10)
        self.requests_left_label = customtkinter.CTkLabel(self.actions_frame, anchor="w", justify="left", text="API Requests Left: Unknown\nResets in: Unknown")
        self.requests_left_label.bind("<Button-1>", command=self.start_update_requests_left)
        CTkToolTip(self.requests_left_label, message="GitHub API Usage:\n"
                   "This shows the number of requests you can make using the GitHub REST API.\n"
                   "These requests are used to fetch release information.\n"
                   "Rate Limits: 60/hr (anonymous) or 5000/hr (with a token).\n"
                   "Click to refresh this information."
                   )
        self.requests_left_label.grid(row=8, column=0, padx=10, pady=10, sticky="w")
        button = customtkinter.CTkButton(self.actions_frame, text="Authorise with GitHub", command=self.open_token_window)
        button.grid(row=8, column=1, padx=10, pady=10, sticky="e")
        CTkToolTip(button, message="Provide a GitHub token or authorise the application through the OAuth.\nGenerated tokens last for 8 hours.\nNo data is stored, will need to be provided again if app is restarted.")

    def start_update_requests_left(self, event=None, show_error=True):
        if not self.updating_rate_limit:
            self.requests_left_label.configure(text="API Requests Left: Fetching...\nResets in: Fetching...", anchor="w")
            self.event_manager.add_event(
                event_id="fetch_rate_limit_status",
                func=self.update_requests_left,
                kwargs={"token": self.settings.token, "show_error": show_error},
                error_functions=[lambda: self.requests_left_label.configure(text="API Requests Left: Unknown\nResets in: Unknown"), lambda: messagebox.showerror(self.root_window, "API Rate Limit Status", "An unexpected error occurred while fetching the rate limit status.\nCheck the logs for more information and report this issue."), lambda: setattr(self, "updating_rate_limit", False)]
            )
        else:
            messagebox.showerror(self.root_window, "API Rate Limit Status", "Please wait, there is currently a fetch in progress. Or it has been disabled.")

    def update_requests_left(self, token, show_error=True):
        self.updating_rate_limit = True
        rate_limit_status = get_rate_limit_status(token)
        if not rate_limit_status["status"]:
            self.updating_rate_limit = False
            self.requests_left_label.configure(text="API Requests Left: Unknown\nResets in: Unknown")
            if show_error:
                return {
                    "message_func": messagebox.showerror,
                    "message_args": (self.root_window, "API Rate Limit Status", f"{rate_limit_status["message"]}")
                }
            return

        r_left = rate_limit_status["requests_remaining"]
        t_left = rate_limit_status["reset_time"]

        # Calculate the time difference       
        time_till_reset = datetime.fromtimestamp(int(t_left)) - datetime.now()

        # Extract hours, and minutes
        total_seconds = time_till_reset.seconds
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        # Build the relative time string
        if hours > 0:
            relative_time = f"{hours} hour{'s' if hours > 1 else ''}"
        elif minutes > 0:
            relative_time = f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            relative_time = "less than a minute"

        self.requests_left_label.configure(text=f"API Requests Left: {r_left}\nResets in: {relative_time}")
        self.updating_rate_limit = False

    def change_colour_theme(self, theme, var):
        current_theme = Path(customtkinter.ThemeManager._currently_loaded_theme)

        if theme == "Custom...":
            var.set(self.settings.colour_theme_path.stem.replace("-", " ").title())
            custom_theme = filedialog.askopenfilename(title="Select a customtkinter theme", filetypes=[("customtkinter theme", "*json")])
            if not custom_theme:
                return
            self.settings.colour_theme_path = Path(custom_theme)
        else:
            new_theme = self.assets.get_theme_path(theme.lower().replace(" ", "-"))
            if current_theme == new_theme:
                var.set(theme)
                return
            self.settings.colour_theme_path = new_theme

        self.settings.save()
        var.set(theme)
        messagebox.showinfo(self.root_window, "Theme Change", "Please restart the application to apply the new theme.")

    def set_dark_mode_setting(self, value, var):
        self.settings.dark_mode = value
        self.after(100, lambda: customtkinter.set_appearance_mode("dark" if value else "light"))
        self.settings.save()

    def open_token_window(self):
        if self.token_gen is None:
            self.token_gen = GitHubLoginWindow(self)
            self.token_gen.grab_set()
        else:
            self.token_gen.focus()

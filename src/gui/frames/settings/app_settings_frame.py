import os
from datetime import timedelta, datetime
from pathlib import Path
from threading import Thread
from tkinter import filedialog, ttk

import customtkinter
from CTkToolTip import CTkToolTip

from core import constants
from core.assets import Assets
from core.paths import Paths
from core.utils.github import get_rate_limit_status
from gui.libs import messagebox
from gui.libs.ext.CTkScrollableDropdown import CTkScrollableDropdown
from gui.windows.github_login_window import GitHubLoginWindow
from core.utils.thread_event_manager import ThreadEventManager


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
        
        self.appearance_mode_variable = customtkinter.StringVar()
        self.colour_theme_variable = customtkinter.StringVar()
        self.auto_app_updates_variable = customtkinter.BooleanVar()
        self.auto_emulator_updates_variable = customtkinter.BooleanVar()
        self.appearance_mode_variable.set(customtkinter.get_appearance_mode().title())
        self.colour_theme_variable.set(str(Path(customtkinter.ThemeManager._currently_loaded_theme).stem).replace("-", " ").title())
        self.delete_files_after_installing_variable = customtkinter.BooleanVar()
        self.delete_files_after_installing_variable.set(self.settings.delete_files_after_installing)
        self.auto_app_updates_variable.set(self.settings.auto_app_updates)
        self.auto_emulator_updates_variable.set(self.settings.auto_emulator_updates)


        appearance_modes = ["Dark", "Light"]
        customtkinter.CTkLabel(self, text="Appearance Mode: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        appearance_modes_option_menu = customtkinter.CTkOptionMenu(self, variable=self.appearance_mode_variable, values=["Dark", "Light"], command=self.change_appearance_mode)
        appearance_modes_option_menu.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        CTkScrollableDropdown(appearance_modes_option_menu, values=appearance_modes, command=self.change_appearance_mode, width=150, height=400, resize=True, button_height=35)
        ttk.Separator(self, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")

        colour_themes = [str(theme.name).replace("-", " ").replace(".json", "").title() for theme in self.assets.get_list_of_themes()]
        colour_themes.append("Custom...")
        customtkinter.CTkLabel(self, text="Theme: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        theme_option_menu = customtkinter.CTkOptionMenu(self, variable=self.colour_theme_variable, values=colour_themes, command=self.change_colour_theme)
        theme_option_menu.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        CTkScrollableDropdown(theme_option_menu, values=colour_themes, command=self.change_colour_theme, width=150, height=400, resize=True, button_height=35)
        ttk.Separator(self, orient='horizontal').grid(row=3, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self, text="Delete Files after installing").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkCheckBox(self, text="", variable=self.delete_files_after_installing_variable, onvalue=True, offvalue=False, command=self.change_delete_files_option).grid(row=8, column=2, padx=(50, 0), pady=10, sticky="ew")
        ttk.Separator(self, orient="horizontal").grid(row=9, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self, text="Auto App Updates").grid(row=10, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkCheckBox(self, text="", variable=self.auto_app_updates_variable, onvalue=True, offvalue=False, command=self.change_app_update_option).grid(row=10, column=2, padx=(50, 0), pady=10, sticky="ew")
        ttk.Separator(self, orient="horizontal").grid(row=11, columnspan=4, sticky="ew")

        customtkinter.CTkLabel(self, text="Auto Emulator Updates").grid(row=12, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkCheckBox(self, text="", variable=self.auto_emulator_updates_variable, onvalue=True, offvalue=False, command=self.change_emulator_update_option).grid(row=12, column=2, padx=(50, 0), pady=10, sticky="ew")
        ttk.Separator(self, orient="horizontal").grid(row=13, columnspan=4, sticky="ew")

        self.actions_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid(row=14, sticky="ew", columnspan=5, padx=10, pady=10)
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
    def change_colour_theme(self, theme):
        current_theme = Path(customtkinter.ThemeManager._currently_loaded_theme)

        if theme == "Custom...":
            self.colour_theme_variable.set(self.settings.colour_theme_path.stem.replace("-", " ").title())
            custom_theme = filedialog.askopenfilename(title="Select a customtkinter theme", filetypes=[("customtkinter theme", "*json")])
            if not custom_theme:
                return
            self.settings.colour_theme_path = Path(custom_theme)
        else:
            new_theme = self.assets.get_theme_path(theme.lower().replace(" ", "-"))
            if current_theme == new_theme:
                return
            self.settings.colour_theme_path = new_theme
    
        self.settings.save()
        self.colour_theme_variable.set(theme)
        messagebox.showinfo(self.root_window, "Theme Change", "Please restart the application to apply the new theme.")

    def change_appearance_mode(self, mode):
        self.appearance_mode_variable.set(mode)
        self.after(100, lambda: customtkinter.set_appearance_mode(mode.lower()))  # change appearance mode using customtkinters function
        self.settings.appearance_mode = mode.lower()
        self.settings.save()   # update settings.json if change was through settings menu

    def change_delete_files_option(self):
        self.settings.delete_files_after_installing = self.delete_files_after_installing_variable.get()
        self.settings.save()

    def change_app_update_option(self):
        self.settings.auto_app_updates = self.auto_app_updates_variable.get()
        self.settings.save()

    def change_emulator_update_option(self):
        self.settings.auto_emulator_updates = self.auto_emulator_updates_variable.get()
        self.settings.save()

    def open_token_window(self):
        if self.token_gen is None:
            self.token_gen = GitHubLoginWindow(self)
            self.token_gen.grab_set()
        else:
            self.token_gen.focus()

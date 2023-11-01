import os
from threading import Thread
from tkinter import filedialog, messagebox, ttk

import customtkinter
from CTkToolTip import CTkToolTip

from gui.windows.github_login_window import GitHubLoginWindow
from settings.app_settings import get_colour_themes
from utils.auth_token_manager import get_rate_limit_status
from utils.time_utils import calculate_relative_time


class AppSettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, fg_color="transparent")
        self.settings = settings 
        self.parent_frame = parent_frame
        self.update_status = True
        self.update_requests_thread = Thread(target=self.update_requests_left, args=(self.settings.app.token,))
        self.token_gen = None
        self.build_frame()
    def build_frame(self):
        self.settings_path = os.path.join(os.getenv("APPDATA"),"Emulator Manager", "config")
        self.settings_file = os.path.join(self.settings_path, 'settings.json')
        
        # create appearance and themes widgets for settings menu 'Appearance'
        self.grid_columnconfigure(0, weight=1)
        
        self.appearance_mode_variable = customtkinter.StringVar()
        self.colour_theme_variable = customtkinter.StringVar()
        self.use_yuzu_installer_variable = customtkinter.StringVar()
        self.use_yuzu_installer_variable.set(self.settings.yuzu.use_yuzu_installer)
        self.appearance_mode_variable.set(self._get_appearance_mode().title())
        self.colour_theme_variable.set(os.path.basename(customtkinter.ThemeManager._currently_loaded_theme).replace("-"," ").replace(".json", "").title())
        self.delete_files_variable = customtkinter.StringVar()
        self.delete_files_variable.set(self.settings.app.delete_files)
        colour_themes = get_colour_themes(os.path.join(self.parent_frame.parent_frame.root_dir, "assets", "themes"))
        colour_themes = [ theme.replace("-", " ").title() for theme in colour_themes ]
        colour_themes.append("Choose custom theme...")
        customtkinter.CTkLabel(self, text="Appearance Mode: ").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self, variable=self.appearance_mode_variable, values=["Dark", "Light"], command=self.change_appearance_mode).grid(row=0, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=1, columnspan=4, sticky="ew")
        
        customtkinter.CTkLabel(self, text="Theme: ").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkOptionMenu(self, variable=self.colour_theme_variable, values=colour_themes, command=self.change_colour_theme).grid(row=2, column=2, padx=10, pady=10, sticky="e")
        ttk.Separator(self, orient='horizontal').grid(row=3, columnspan=4, sticky="ew") 
        
        customtkinter.CTkLabel(self, text="Delete Files after installing").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        customtkinter.CTkCheckBox(self, text="", variable=self.delete_files_variable, onvalue="True", offvalue="False", command=self.change_delete_files_option).grid(row=8, column=2, padx=(100,0), pady=10, sticky="ew")
        ttk.Separator(self, orient="horizontal").grid(row=9, columnspan=4, sticky="ew")
        
        self.actions_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid(row=10,sticky="ew", columnspan=5, padx=10, pady=10)
        self.requests_left_label = customtkinter.CTkLabel(self.actions_frame, anchor="w", justify="left",text="API Requests Left: Unknown\nResets in: Unknown")
        self.requests_left_label.bind("<Button-1>", command=self.start_update_requests_left)
        CTkToolTip(self.requests_left_label, message=
                    "GitHub API Usage:\n"
                    "This shows the number of requests you can make using the GitHub REST API.\n"
                    "These requests are used to download Dolphin and Yuzu.\n"
                    "Rate Limits: 60/hr (anonymous) or 5000/hr (with a token).\n"
                    "Click to refresh this information."
            )
        self.start_update_requests_left(show_error=False)
        self.requests_left_label.grid(row=8, column=0, padx=10, pady=10, sticky="w")
        button=customtkinter.CTkButton(self.actions_frame, text="Login with GitHub", command=self.open_token_window)
        button.grid(row=8, column=1, padx=10, pady=10, sticky="e")
        CTkToolTip(button, message="Optional feature to increase API request limit to 5000/hr for 8 hours. No data is stored.\nYou will have to log in again the next time you open the app")
        
    def start_update_requests_left(self, event=None, show_error=True):
        if self.update_status and not self.update_requests_thread.is_alive():
            self.requests_left_label.configure(text="API Requests Left: Fetching...\nResets in: Fetching...", anchor="w")
            self.update_requests_thread = Thread(target=self.update_requests_left, args=(self.settings.app.token, show_error))
            self.update_requests_thread.start()
        else:
            messagebox.showerror("API Rate Limit Status", "Please wait, there is currently a fetch in progress. Or it has been disabled.")
    def update_requests_left(self, token, show_error=True):
        rate_limit_status = get_rate_limit_status(token)
        if not all(rate_limit_status):
            self.requests_left_label.configure(text="API Requests Left: Unknown\nResets in: Unknown")
            if show_error:
                messagebox.showerror("Requests Error", rate_limit_status[1])
            return
        rate_limit_status = rate_limit_status[1]
        r_left = rate_limit_status["remaining"]
        t_left = rate_limit_status["reset"]
        self.requests_left_label.configure(text=f"API Requests Left: {r_left}\nResets in: {calculate_relative_time(int(t_left))}")

    def change_colour_theme(self, theme):
        if customtkinter.ThemeManager._currently_loaded_theme.replace("-"," ").title() == theme: # if current theme is the same as the proposed theme, return
            return
        if theme == "Choose custom theme...":
            self.colour_theme_variable.set(os.path.basename(customtkinter.ThemeManager._currently_loaded_theme).replace("-"," ").replace(".json", "").title())
            theme = filedialog.askopenfilename(title="Select a customtkinter theme", filetypes=[("customtkinter theme", "*json")])
            if not theme:
                return
            self.settings.app.colour_theme = theme
        else:
           
            self.settings.app.colour_theme = theme.lower().replace(" ", "-")
        self.update_settings()
        if messagebox.askyesno("Change Theme","The application must be restarted for these changes to take effect, restart now?"):    
            self.parent_frame.parent_frame.restart()
        # destroy current window (because changing colour theme directly does not work)
        # self.parent_frame.parent_frame.destroy()

        
    def change_appearance_mode(self, mode):
        customtkinter.set_appearance_mode(mode.lower()) # change appearance mode using customtkinters function 
        self.settings.app.appearance_mode = mode.lower()
        self.update_settings()   # update settings.json if change was through settings menu
        
    def change_delete_files_option(self):
        self.settings.app.delete_files = self.delete_files_variable.get()
        self.update_settings()
        
    def open_token_window(self):
        if self.token_gen is None:
            self.token_gen = GitHubLoginWindow(self)
            self.token_gen.grab_set()
        else:
            self.token_gen.focus()
        
    def update_settings(self):
        self.settings.update_file()
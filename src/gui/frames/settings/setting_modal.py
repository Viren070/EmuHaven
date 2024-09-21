import textwrap
from pathlib import Path
from tkinter import filedialog

from customtkinter import (BooleanVar, CTkButton, CTkEntry, CTkFont, CTkFrame,
                           CTkLabel, CTkOptionMenu, CTkSwitch, StringVar)

from core.logging.logger import Logger
from gui.libs.CTkMessagebox import messagebox
from gui.libs.CTkScrollableDropdown import CTkScrollableDropdown


class SettingModal(CTkFrame):
    def __init__(self, master, settings, setting_options, path_options=None, option_menu_options=None, custom_options=None):
        super().__init__(master=master, corner_radius=10, border_width=3)
        self.logger = Logger(__name__).get_logger()
        self.settings = settings
        self.settings_object = setting_options.get("object")
        self.setting_id = setting_options.get("id")
        self.setting_type = setting_options.get("type")
        self.setting_title = setting_options.get("title")
        self.setting_description = setting_options.get("description")
        if self.setting_type == "path":
            if path_options is None:
                raise ValueError("path options must be provided for path settings")
            self.path_type = path_options.get("type")
            self.filedialog_title = path_options.get("title")
            self.filedialog_filetypes = path_options.get("filetypes")
            if (self.path_type is None or self.filedialog_title is None):
                raise ValueError("path type and filedialog title must be provided for path settings")

        if self.setting_type == "option_menu" and option_menu_options is None:
            raise ValueError("option_menu_options must be provided for option_menu settings")
        self.option_menu_options = option_menu_options if option_menu_options is not None else {}
        self.dir_cycle = []
        self.dir_cycle_index = 0
        self.custom_options = custom_options if custom_options is not None else {}
        self.setting_var = StringVar()
        self.is_updating = False
        self.typing_delay = 1000
        self.typing_timer = None
        self.build_frame()

    def build_frame(self):
        # give 1st column a weight of 1 so it fills all available space
        self.grid_columnconfigure(0, weight=1)
        # create fonts
        self.title_font = CTkFont(family="Helvetica", size=16, weight="bold")
        self.description_font = CTkFont(family="Helvetica", size=14)

        install_directory_title = CTkLabel(self, text=self.setting_title, font=self.title_font)
        install_directory_title.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")

        self.install_directory_description = CTkLabel(self, justify="left", text=self.setting_description, font=self.description_font)
        self.install_directory_description.grid(row=1, column=0, padx=10, pady=(0, 7), sticky="w")

        self.bind("<Configure>", self.on_resize)
        self.add_setting_widget()

    def add_setting_widget(self):
        match self.setting_type:
            case "path":
                setting_frame = CTkFrame(self, fg_color="transparent", border_width=0)
                setting_frame.grid(row=2, column=0, pady=(0, 3), padx=5, sticky="ew")
                setting_frame.grid_columnconfigure(0, weight=1)
                self.setting_var.set(self.get_setting_value())
                self.update_dir_cycle()

                self.entry_widget = CTkEntry(setting_frame, textvariable=self.setting_var, corner_radius=7, font=("Helvetica", 16), height=35)
                self.entry_widget.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

                browse_button = CTkButton(setting_frame, text="Browse", width=100, height=35, corner_radius=7, command=self.update_with_explorer, font=("Helvetica", 14))
                browse_button.grid(row=0, column=1, padx=5, pady=(0, 5), sticky="e")

                self.entry_widget.bind("<Return>", self.update_setting_value)
                self.entry_widget.bind("<KeyRelease>", self.on_key_release)
                self.entry_widget.bind("<Up>", lambda event: self.cycle_dir(-1))
                self.entry_widget.bind("<Down>", lambda event: self.cycle_dir(1))
                self.entry_widget.bind("<Control-Up>", lambda event: self.up_dir())

            case "switch":
                switch_frame = CTkFrame(self, fg_color="transparent", border_width=0)
                switch_frame.grid(row=0, column=1, rowspan=2, pady=5, padx=5, sticky="ew")

                self.setting_var = BooleanVar()
                current_value = self.get_setting_value()
                if current_value is None:
                    current_value = False
                self.setting_var.set(current_value)

                switch_widget = CTkSwitch(switch_frame, text="", border_width=1, variable=self.setting_var, onvalue=True, offvalue=False, command=self.update_setting_value, switch_height=24, switch_width=54, width=30)
                switch_widget.grid(row=0, column=1, padx=20, pady=2, sticky="e")

            case "option_menu":
                option_menu_frame = CTkFrame(self, fg_color="transparent", border_width=0)
                option_menu_frame.grid(row=0, column=1, rowspan=2, pady=5, padx=5, sticky="ew")

                self.setting_var.set(self.get_setting_value())

                values = self.option_menu_options.get("values")
                option_widget = CTkOptionMenu(option_menu_frame, variable=self.setting_var, width=150, height=34, anchor="center", font=("Helvetica", 14))
                option_widget.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
                CTkScrollableDropdown(option_widget, values=values, width=160, height=400, resize=True, button_height=35, command=self.update_setting_value, font=("Helvetica", 14))

    def update_dir_cycle(self):
        current_value = Path(self.setting_var.get().strip()).resolve()
        self.dir_cycle = [current_value] + [item.resolve() for item in current_value.iterdir() if item.is_dir()]
        self.dir_cycle.sort()
        self.dir_cycle_index = 0

    def up_dir(self):
        self.setting_var.set(str(Path(self.setting_var.get()).parent))

    def cycle_dir(self, direction):
        if len(self.dir_cycle) == 0:
            return
        self.dir_cycle_index += direction
        if self.dir_cycle_index < 0:
            self.dir_cycle_index = len(self.dir_cycle) - 1
        if self.dir_cycle_index >= len(self.dir_cycle):
            self.dir_cycle_index = 0
        self.setting_var.set(str(self.dir_cycle[self.dir_cycle_index]))

    def on_key_release(self, *args):
        if self.typing_timer is not None:
            self.after_cancel(self.typing_timer)
        self.typing_timer = self.after(self.typing_delay, self.update_setting_value)

    def update_setting_value(self, *args):
        if self.is_updating:
            return
        self.is_updating = True

        if self.setting_type == "path":
            try:
                value = Path(self.setting_var.get().strip()).resolve()
            except Exception as error:
                messagebox.showerror(self.winfo_toplevel(), self.setting_id.replace("_", " ").title(), f"The path you entered is invalid.\n\n{error}")
                self.is_updating = False
                self.update_entry_widget()
                return
            if not value.exists():
                messagebox.showerror(self.winfo_toplevel(), self.setting_id.replace("_", " ").title(), "The path you entered does not exist.")
                self.is_updating = False
                self.update_entry_widget()
                return
            self.update_dir_cycle()
        elif self.setting_type == "option_menu":
            value = args[0]
        else:
            value = self.setting_var.get()

        self.logger.info("Updating setting %s to value: %s", self.setting_id, value)
        if self.custom_options.get("update_function") is not None:
            try:
                self.custom_options.get("update_function")(value, self.setting_var)
            except Exception as error:
                messagebox.showerror(self.winfo_toplevel(), self.setting_id.replace("_", " ").title(), f"An error occurred while updating the setting.\n\n{error}")
            self.is_updating = False
            return

        setattr(self.settings_object, self.setting_id, value)
        self.setting_var.set(value)
        self.settings.save()
        self.is_updating = False

    def update_entry_widget(self):
        self.entry_widget.delete(0, 'end')
        self.entry_widget.insert(0, self.get_setting_value())

    def get_setting_value(self):
        if self.custom_options.get("get_function") is not None:
            return self.custom_options.get("get_function")()
        return getattr(self.settings_object, self.setting_id)

    def update_with_explorer(self, dialogtype=None):
        if self.path_type == "directory":
            new_directory = filedialog.askdirectory(initialdir=self.entry_widget.get(), title=self.filedialog_title)
            if new_directory is None or new_directory == "":
                return
            self.entry_widget.delete(0, 'end')
            self.entry_widget.insert(0, new_directory)
            self.update_setting_value()

        if self.path_type == "file":
            initialdir = Path(self.entry_widget.get()).parent
            new_path = filedialog.askopenfilename(initialdir=initialdir, title=self.filedialog_title, filetypes=self.filedialog_filetypes)
            if new_path is None or new_path == "":
                return
            self.entry_widget.delete(0, 'end')
            self.entry_widget.insert(0, new_path)
            self.update_setting_value()
            return

    def on_resize(self, event):
        self.update_description_textwrap(event.width)

    def update_description_textwrap(self, width):

        char_width = 8
        available_width = width - 20
        max_length = available_width // char_width
        if max_length < 0:
            max_length = 30
        self.install_directory_description.configure(text=textwrap.fill(self.setting_description, max_length), wraplength=available_width)

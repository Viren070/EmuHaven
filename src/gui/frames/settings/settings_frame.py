import customtkinter
from customtkinter import ThemeManager
from PIL import Image

from gui.frames.settings.app_settings_frame import AppSettingsFrame
from gui.frames.settings.dolphin_settings_frame import DolphinSettingsFrame
from gui.frames.settings.yuzu_settings_frame import YuzuSettingsFrame
from gui.frames.settings.ryujinx_settings_frame import RyujinxSettingsFrame
from gui.frames.settings.xenia_settings_frame import XeniaSettingsFrame

class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame, corner_radius=0, bg_color="transparent", width=20)
        self.settings = settings
        self.parent_frame = parent_frame
        self.build_gui()

    def build_gui(self):
        self.lock_image = customtkinter.CTkImage(light_image=Image.open(self.settings.get_image_path("padlock_light")),
                                                 dark_image=Image.open(self.settings.get_image_path("padlock_dark")), size=(20, 20))
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # create settings navigation frame
        self.settings_navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, width=100, border_width=2)
        self.settings_navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.settings_navigation_frame.grid_rowconfigure(10, weight=1)

        # create settings navigation menu buttons
        text_color = ThemeManager.theme["CTkLabel"]["text_color"]
        self.app_settings_button = customtkinter.CTkButton(self.settings_navigation_frame, corner_radius=0, width=90, height=25, border_spacing=10, text="App",
                                                           fg_color="transparent", text_color=text_color,
                                                           anchor="w", command=self.app_settings_button_event)
        self.app_settings_button.grid(row=1, column=0, padx=2, pady=(2, 0), sticky="ew")

        self.dolphin_settings_button = customtkinter.CTkButton(self.settings_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Dolphin",
                                                               fg_color="transparent", text_color=text_color,
                                                               anchor="w", command=self.dolphin_settings_button_event)
        self.dolphin_settings_button.grid(row=2, column=0, padx=2, sticky="ew")

        self.yuzu_settings_button = customtkinter.CTkButton(self.settings_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Yuzu",
                                                            fg_color="transparent", text_color=text_color,
                                                            anchor="w", command=self.yuzu_settings_button_event)
        self.yuzu_settings_button.grid(row=3, column=0, padx=2, sticky="ew")

        self.ryujinx_settings_button = customtkinter.CTkButton(self.settings_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Ryujinx",
                                                               fg_color="transparent", text_color=text_color,
                                                               anchor="w", command=self.ryujinx_settings_button_event)
        self.ryujinx_settings_button.grid(row=4, column=0, padx=2, sticky="ew")

        self.xenia_settings_button = customtkinter.CTkButton(self.settings_navigation_frame, corner_radius=0, width=100, height=25, border_spacing=10, text="Xenia",
                                                                fg_color="transparent", text_color=text_color,
                                                                anchor="w", command=self.xenia_settings_button_event)
        self.xenia_settings_button.grid(row=5, column=0, padx=2, sticky="ew")

        self.dolphin_settings_frame = DolphinSettingsFrame(self, self.settings)
        self.yuzu_settings_frame = YuzuSettingsFrame(self, self.settings)
        self.ryujinx_settings_frame = RyujinxSettingsFrame(self, self.settings)
        self.app_settings_frame = AppSettingsFrame(self, self.settings)
        self.xenia_settings_frame = XeniaSettingsFrame(self, self.settings)

    def dolphin_settings_button_event(self):
        self.select_settings_frame_by_name("dolphin")

    def yuzu_settings_button_event(self):
        self.select_settings_frame_by_name("yuzu")

    def ryujinx_settings_button_event(self):
        self.select_settings_frame_by_name("ryujinx")

    def xenia_settings_button_event(self):
        self.select_settings_frame_by_name("xenia")

    def app_settings_button_event(self):
        self.select_settings_frame_by_name("app")

    def select_settings_frame_by_name(self, name):
        # set button color for selected button
        self.yuzu_settings_button.configure(fg_color=self.yuzu_settings_button.cget("hover_color") if name == "yuzu" else "transparent")
        self.dolphin_settings_button.configure(fg_color=self.dolphin_settings_button.cget("hover_color") if name == "dolphin" else "transparent")
        self.ryujinx_settings_button.configure(fg_color=self.ryujinx_settings_button.cget("hover_color") if name == "ryujinx" else "transparent")
        self.app_settings_button.configure(fg_color=self.app_settings_button.cget("hover_color") if name == "app" else "transparent")
        self.xenia_settings_button.configure(fg_color=self.xenia_settings_button.cget("hover_color") if name == "xenia" else "transparent")

        # show selected frame
        if name == "dolphin":
            self.dolphin_settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.dolphin_settings_frame.grid_forget()
        if name == "yuzu":
            self.yuzu_settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.yuzu_settings_frame.grid_forget()
        if name == "ryujinx":
            self.ryujinx_settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.ryujinx_settings_frame.grid_forget()
        if name == "xenia":
            self.xenia_settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.xenia_settings_frame.grid_forget()
        if name == "app":
            self.app_settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.app_settings_frame.grid_forget()

    def settings_changed(self):
        return (self.yuzu_settings_frame.settings_changed() or self.dolphin_settings_frame.settings_changed())

    def revert_settings(self):
        self.yuzu_settings_frame.update_entry_widgets()
        self.dolphin_settings_frame.update_entry_widgets()

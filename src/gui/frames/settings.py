import customtkinter 

class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, settings):
        super().__init__(parent_frame)
        self.settings = settings 
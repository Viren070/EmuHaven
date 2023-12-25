import customtkinter 
from gui.frames.progress_frame import ProgressFrame

class ProgressWindow(customtkinter.CTk):
    def __init__(self, title):
        super().__init__()
        self.title(title)
        self.resizable(False, False)
        self.progress_frame = ProgressFrame(self)
        self.progress_frame.pack(fill="both", expand=True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()

    def on_close(self):
        self.destroy()

    def configure_early_access_buttons(*args, **kwargs):
        pass

    def __getattr__(self, name):
        # Handle any function call without raising an error
        def dummy_function(*args, **kwargs):
            pass
        return dummy_function

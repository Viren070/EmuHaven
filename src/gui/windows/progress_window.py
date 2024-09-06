import customtkinter


class ProgressWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, title, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)
        self.resizable(False, False)
        self.progress_frame = ProgressFrame(self)
        self.progress_frame.pack(fill="both", expand=True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()
        self.focus_set()

    def on_close(self):
        self.grab_release()
        self.destroy()

    def __getattr__(self, name):
        # Handle any function call without raising an error
        def dummy_function(*args, **kwargs):
            pass
        return dummy_function

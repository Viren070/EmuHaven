from tkinter import filedialog
from typing import Union, Tuple, Optional
from pathlib import Path

from customtkinter import CTkLabel, CTkEntry, CTkButton, ThemeManager, CTkToplevel, CTkFont, CTkFrame


class PathDialog(CTkToplevel):
    """
    Dialog with extra window, message, entry widget, cancel and ok button.
    For detailed information check out the documentation.
    """

    def __init__(self,
                 filetypes=None,
                 directory=None,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 entry_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 entry_border_color: Optional[Union[str, Tuple[str, str]]] = None,
                 entry_text_color: Optional[Union[str, Tuple[str, str]]] = None,

                 title: str = "CTkDialog",
                 font: Optional[Union[tuple, CTkFont]] = None,
                 text: str = "CTkDialog"):

        super().__init__(fg_color=fg_color)
        self._fg_color = ThemeManager.theme["CTkToplevel"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)
        self._text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else self._check_color_type(button_hover_color)
        self._button_fg_color = ThemeManager.theme["CTkButton"]["fg_color"] if button_fg_color is None else self._check_color_type(button_fg_color)
        self._button_hover_color = ThemeManager.theme["CTkButton"]["hover_color"] if button_hover_color is None else self._check_color_type(button_hover_color)
        self._button_text_color = ThemeManager.theme["CTkButton"]["text_color"] if button_text_color is None else self._check_color_type(button_text_color)
        self._entry_fg_color = ThemeManager.theme["CTkEntry"]["fg_color"] if entry_fg_color is None else self._check_color_type(entry_fg_color)
        self._entry_border_color = ThemeManager.theme["CTkEntry"]["border_color"] if entry_border_color is None else self._check_color_type(entry_border_color)
        self._entry_text_color = ThemeManager.theme["CTkEntry"]["text_color"] if entry_text_color is None else self._check_color_type(entry_text_color)

        self.directory_mode = directory
        self._user_input: Union[str, None] = None
        self._running: bool = False
        self._title = title
        self._text = text
        self._font = font
        self._filetypes = filetypes

        self.title(self._title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self._label = CTkLabel(master=self,
                               width=300,
                               wraplength=300,
                               fg_color="transparent",
                               text_color=self._text_color,
                               text=self._text,
                               font=self._font)
        self._label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Create a frame for the entry and browse button
        entry_frame = CTkFrame(master=self, width=300, fg_color="transparent", border_width=0)
        entry_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=4)  # Entry takes up 4/5 of the frame
        entry_frame.grid_columnconfigure(1, weight=1)  # Browse button takes up 1/5 of the frame

        self._entry = CTkEntry(master=entry_frame,
                               width=1,  # Adjust width as needed
                               fg_color=self._entry_fg_color,
                               border_color=self._entry_border_color,
                               text_color=self._entry_text_color,
                               font=self._font)
        self._entry.grid(row=0, column=0, padx=0, pady=0, sticky="ew")

        self._browse_button = CTkButton(master=entry_frame,
                                        width=1,  # Adjust width as needed
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text='Browse',
                                        font=self._font,
                                        command=self._browse_event)
        self._browse_button.grid(row=0, column=1, padx=5, pady=0, sticky="ew")

        ok_cancel_frame = CTkFrame(master=self, fg_color="transparent", border_width=0)
        ok_cancel_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        ok_cancel_frame.grid_columnconfigure(0, weight=1)  # Center "Ok" button horizontally
        ok_cancel_frame.grid_columnconfigure(1, weight=1)  # Center "Cancel" button horizontally

        self._ok_button = CTkButton(master=ok_cancel_frame,
                                    width=100,
                                    border_width=0,
                                    fg_color=self._button_fg_color,
                                    hover_color=self._button_hover_color,
                                    text_color=self._button_text_color,
                                    text='Ok',
                                    font=self._font,
                                    command=self._ok_event)
        self._ok_button.grid(row=0, column=1, padx=20, pady=0, sticky="w")

        self._cancel_button = CTkButton(master=ok_cancel_frame,
                                        width=100,
                                        border_width=0,
                                        fg_color=self._button_fg_color,
                                        hover_color=self._button_hover_color,
                                        text_color=self._button_text_color,
                                        text='Cancel',
                                        font=self._font,
                                        command=self._on_closing)
        self._cancel_button.grid(row=0, column=0, padx=20, pady=0, sticky="e")

        self.after(150, lambda: self._entry.focus())  # set focus to entry with slight delay, otherwise, it won't work
        self._entry.bind("<Return>", self._ok_event)

    def _browse_event(self):
        self.withdraw()
        if self.directory_mode:
            path = filedialog.askdirectory()
        else:
            extensions = ["*" + ext[1:] for ext in self._filetypes]
            path = filedialog.askopenfilename(filetypes=[("Custom file", extensions)])
        self.deiconify()
        self.lift()
        if path is None or path == "":
            return
        self._entry.delete(0, 'end')
        self._entry.insert(0, path)

    def _ok_event(self, event=None):
        if self._entry.get() == "":
            return
        self._user_input = self._entry.get()
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        if self._user_input is None:
            return {
                "status": False,
                "cancelled": True
            }
        path = Path(self._user_input)
        
        if not path.exists() or (self._filetypes is not None and path.suffix.lower() not in self._filetypes):
            return {
                "status": False,
                "message": "Invalid path or filetype selected",
                "cancelled": False
            }
        
        if self.directory_mode and not path.is_dir():
            return {
                "status": False,
                "message": "Invalid directory selected",
                "cancelled": False
            }
        
        return {
            "status": True,
            "path": path,
            "cancelled": False
        }

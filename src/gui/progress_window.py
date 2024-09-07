import customtkinter

from gui.progress_frame import ProgressFrame


class ProgressWindow(customtkinter.CTkToplevel):
    def __init__(self, master, handler):
        super().__init__(master, border_width=1)
        self.grid_columnconfigure(0, weight=1)
        self._progress_frame = ProgressFrame(self, handler)
        self._progress_frame.grid(row=0, column=0, sticky="ew")

    def set_title(self, title):
        self._progress_frame.operation_title.configure(text=title)

    def update_progress(self, units_complete, total_units, measurement_unit):
        self._progress_frame.update_progress(units_complete, total_units, measurement_unit)

    def set_speed(self, speed, measurement_unit, time_measurement="s"):
        self._progress_frame.set_speed(speed, measurement_unit, time_measurement)

    def set_eta(self, eta):
        self._progress_frame.set_eta(eta)

    def set_status(self, status):
        self._progress_frame.set_status(status)

    def set_cancel_button_state(self, state):
        self._progress_frame.set_cancel_button_state(state)

    def cancel_button_event(self):
        self._progress_frame.cancel_button_event()
    
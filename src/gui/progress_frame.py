from time import perf_counter


import customtkinter


class ProgressFrame(customtkinter.CTkFrame):
    def __init__(self, master, handler):
        super().__init__(master, border_width=1)
        self.handler = handler
        self.grid_columnconfigure(0, weight=1)
        self.smoothing_factor = 0.3
        self.cancel_download_raised = False


        self.operation_title = customtkinter.CTkLabel(self)
        self.progress_label = customtkinter.CTkLabel(self)
        self.progress_bar = customtkinter.CTkProgressBar(
            self, orientation="horizontal", mode="determinate"
        )
        self.percentage_label = customtkinter.CTkLabel(self, text="0%")
        self.speed_label = customtkinter.CTkLabel(self, text="0 MB/s")

        self.status_label = customtkinter.CTkLabel(
            self, width=100, text="Status: Downloading..."
        )
        self.eta_label = customtkinter.CTkLabel(self, text="Time Left: 00:00:00")
        self.cancel_operation_button = customtkinter.CTkButton(
            self, text="Cancel", command=self.cancel_button_event
        )

        self.operation_title.grid(row=0, column=0, sticky="W", padx=10, pady=5)

        self.progress_label.grid(row=1, column=0, sticky="W", padx=10)
        self.progress_bar.grid(row=2, column=0, columnspan=6, padx=(10, 45), pady=5, sticky="EW")
        self.percentage_label.grid(row=2, column=5, sticky="E", padx=10)
        self.speed_label.grid(row=1, column=5, sticky="E", padx=10)
        self.status_label.grid(row=3, column=0, sticky="W", padx=10, pady=5)
        self.eta_label.grid(row=0, column=5, sticky="E", pady=5, padx=10)
        self.cancel_operation_button.grid(row=3, column=5, pady=10, padx=10, sticky="E")

    def set_title(self, title):
        self.operation_title.configure(text=title)

    def update_progress(self, units_complete, total_units, measurement_unit):
        self.progress_label.configure(text=f"{units_complete:.0f}{measurement_unit} / {total_units:.0f}{measurement_unit}")
        progress = units_complete / total_units if total_units > 0 else 0
        self.progress_bar.set(progress)
        self.percentage_label.configure(text=f"{progress*100:.0f}%")

    def set_speed(self, speed, measurement_unit, time_measurement="s"):
        self.speed_label.configure(text=f"{speed:.0f}{measurement_unit}/{time_measurement}")

    def set_eta(self, eta):
        self.eta_label.configure(text=f"Time Left: {eta}")

    def set_status(self, status):
        self.status_label.configure(text=f"Status: {status}")

    def set_cancel_button_state(self, state):
        self.cancel_operation_button.configure(state=state)

    def cancel_button_event(self):
        self.handler.send_cancel_signal_to_operation()
    
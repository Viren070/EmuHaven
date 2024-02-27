import os
import time
import webbrowser
from threading import Thread
from tkinter import messagebox

import customtkinter

from utils.auth_token_manager import request_device_code, request_token, is_token_valid


class GitHubLoginWindow(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("GitHub Login")
        self.settings = master.settings
        self.geometry("500x250")
        self.resizable(False, False)
        self.poll_token = True
        self.master = master
        self.token_response = None
        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widgets()
        self.token_path = os.path.join(os.getenv("APPDATA"), "Emulator Manager", ".token")

    def on_closing(self):
        self.master.token_gen = None
        self.poll_token = False
        self.token_response = "EXIT"
        self.destroy()

    def create_widgets(self):
        # Label for token entry
        self.token_label = customtkinter.CTkLabel(self, text="Enter your token:")
        self.token_label.pack(pady=10)

        # Frame for token entry and button
        self.token_frame = customtkinter.CTkFrame(self)
        self.token_frame.pack(pady=10)

        # Entry widget for token
        self.token_entry = customtkinter.CTkEntry(self.token_frame, width=300)
        self.token_entry.pack(side='left', padx=10)

        # Button for token submission
        self.token_button = customtkinter.CTkButton(self.token_frame, text="Submit", command=self.submit_token_event, width=10)
        self.token_button.pack(side='left')

        # Label for authorization button
        self.auth_label = customtkinter.CTkLabel(self, text="Or click 'Authorise' to start the authentication process:")
        self.auth_label.pack(pady=10)

        # Authorization button
        self.login_button = customtkinter.CTkButton(self, text="Authorise", command=self.start_authentication)
        self.login_button.pack(pady=10)


    def submit_token_event(self):
        self.token_button.configure(state="disabled")
        Thread(target=self.submit_token).start()
        
    def submit_token(self):
        token = self.token_entry.get()
        if is_token_valid(token):
            self.settings.app.token = token
            self.master.token_gen = None
            self.master.start_update_requests_left()
            messagebox.showinfo("GitHub Authorisation", "Successfully authenticated!")
            self.grab_release()
            self.bring_window_to_top(self.master.parent_frame.parent_frame)
            self.destroy()
            return 
        
        messagebox.showerror("Invalid Token", "The token you entered is invalid. Please try again.")
        self.token_button.configure(state="normal")

    def start_authentication(self):
        self.login_button.configure(state="disabled", text="Getting Code...")
        self.token_button.configure(state="disabled")
        device_code_thread = Thread(target=self.get_device_code_and_token)
        device_code_thread.start()

    def get_device_code_and_token(self):
        device_code_response = request_device_code()
        if not all(device_code_response):
            messagebox.showerror("Requests Error", device_code_response[1])
            self.login_button.configure(state="normal", text="Authorise")
            self.auth_label.configure(text="Click the 'Authorise' button to start the authentication process.")
            self.token_button.configure(state="normal")
            return
        device_code_response = device_code_response[1]
        verification_uri = device_code_response["verification_uri"]
        user_code = device_code_response["user_code"]
        device_code = device_code_response["device_code"]
        interval = device_code_response["interval"]
        self.login_button.configure(state="disabled", text="Authorising...")
        self.countdown_on_widget(5, self.auth_label, f"You will be redirected in {{}} seconds to {verification_uri}\nPlease enter the code: {user_code}. It has been copied to your clipboard", f"You are being redirected to {verification_uri}...\nPlease enter the code: {user_code}. It has been copied to your clipboard")
        if not self.poll_token:
            return
        self.clipboard_clear()
        self.clipboard_append(user_code)
        webbrowser.open(verification_uri, new=0)
        self.auth_label.configure(text=f"Please enter the code at {user_code} at\n{verification_uri} \nIt has been copied to your clipboard.")
        self.login_button.configure(state="disabled", text="Authorising...")
        # Poll for the access token
        token_poll_thread = Thread(target=self.poll_for_token, args=(device_code, interval, ))

        self.countdown_on_widget(15, self.login_button, "Checking in {}s")

        token_poll_thread.start()
        self.check_token_status(token_poll_thread)

    def countdown_on_widget(self, countdown_time, widget, default_text, final_text=None):
        left = countdown_time
        widget.configure(text=default_text.format(left))
        while left > 0:
            time.sleep(1)
            if not self.poll_token:
                return
            left -= 1
            widget.configure(text=default_text.format(left))
        if final_text:
            widget.configure(text=final_text)

    def poll_for_token(self, device_code, interval):
        requests_made = 2
        while self.poll_token:
            token_response = request_token(device_code)
            requests_made += 1
            if interval < 15:
                interval = 15
            print(f"requests made with interval {interval}s: {requests_made}")
            if requests_made > 5:
                messagebox.showerror("Authorisation Error", "Failed to authorise in time. Attempting to authorise also uses some of your API requests. You can still login if you have 0 requests left.")
                return
            if not all(token_response):
                messagebox.showerror("Requests Error", token_response[1])
                self.token_response = None
                return
            token_response = token_response[1]
            if "access_token" in token_response:
                self.token_response = token_response["access_token"]
                return
            elif "error" in token_response:
                error = token_response["error"]
                if error == "authorization_pending":
                    self.countdown_on_widget(interval, self.login_button, "Checking in {}s", "Checking...")
                elif error == "slow_down":
                    self.countdown_on_widget(interval+10, self.login_button, "Checking in {}s", "Checking...")
                else:
                    self.token_response = None
                    return
            else:
                self.token_response = None
        return

    def check_token_status(self, token_poll_thread):
        token_poll_thread.join()

        # Polling thread has finished, handle the result
        if self.token_response == "EXIT":
            return
        elif self.token_response is not None:
            # Authentication successful
            self.grab_release()
            self.bring_window_to_top(self.master.parent_frame.parent_frame)
            self.login_button.configure(text="Success!")
            messagebox.showinfo("GitHub Authorisation", "Successfully authenticated!")
            self.settings.app.token = self.token_response
            self.master.token_gen = None
            self.master.start_update_requests_left()
            self.destroy()
        else:
            # Authentication failed
            self.bring_window_to_top(self)
            messagebox.showerror("Authentication Error", "Failed to authorise")
            self.login_button.configure(state="normal", text="Authorise")
            self.auth_label.configure(text="Click the 'Authorise' button to start the authentication process.")

    def bring_window_to_top(self, window):
        window.deiconify()  # Restore the window if minimized
        window.focus_force()  # Bring the window into focus
        window.lift()  # Raise the window to the top
        window.attributes('-topmost', True)  # Set it as topmost
        window.attributes('-topmost', False)

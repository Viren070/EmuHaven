import os
import time
import webbrowser
from threading import Thread

import customtkinter

from core.utils.github import (is_token_valid, request_device_code,
                               request_token)
from gui.libs import messagebox


class GitHubLoginWindow(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("GitHub Login")
        self.settings = master.settings
        self.event_manager = master.event_manager
        self.geometry("500x250")
        self.resizable(False, False)
        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widgets()

    def on_closing(self):
        if self.event_manager.is_event_running("get_device_code") or self.event_manager.is_event_running("get_token"):
            messagebox.showinfo(self, "Info", "Please wait for the current process to complete.")
            return
        self.destroy()

    def create_widgets(self):
        # Label for token entry
        self.token_label = customtkinter.CTkLabel(self, text="Enter your token:")
        self.token_label.pack(pady=10)

        # Frame for token entry and button
        self.token_frame = customtkinter.CTkFrame(self,fg_color="transparent", border_width=0)
        self.token_frame.pack(pady=10)

        # Entry widget for token
        self.token_entry = customtkinter.CTkEntry(self.token_frame, width=300)
        self.token_entry.pack(side='left', padx=10)

        # Button for token submission
        self.submit_token_button = customtkinter.CTkButton(self.token_frame, text="Submit", command=self.submit_token_button_event, width=10)
        self.submit_token_button.pack(side='left')

        # Label for authorization button
        self.auth_label = customtkinter.CTkLabel(self, text="Or click 'Authorise' to start the authentication process:")
        self.auth_label.pack(pady=10)

        # Authorization button
        self.oauth_start_button = customtkinter.CTkButton(self, text="Authorise", command=self.start_oauth_flow_button_event)
        self.oauth_start_button.pack(pady=10)

    def configure_widgets(self, state):
        self.token_entry.configure(state=state)
        self.submit_token_button.configure(state=state)
        self.oauth_start_button.configure(state=state)

    def submit_token_button_event(self):
        self.configure_widgets("disabled")
        token = self.token_entry.get()
        self.event_manager.add_event(
            event_id="process_token",
            func=self.process_token,
            kwargs={"token": token},
            completion_funcs_with_result=[self.on_token_processed],
            error_functions=[lambda: messagebox.showerror(self, "Error", "Failed to process token.")],
            completion_functions=[lambda: self.configure_widgets("normal")]
        )
        
    def process_token(self, token):
        if not token or len(token) < 5:
            return {
                "result": (False,),
            }
        return {
            "result": (is_token_valid(token),),
        }
        
    def on_token_processed(self, result):
        if result:
            self.settings.token = self.token_entry.get()
            self.settings.save_settings()
            messagebox.showsuccess(self, "Success", "Token processed successfully.")
            self.destroy()
        else:
            messagebox.showerror(self, "Error", "Invalid token.")
    
    def start_oauth_flow_button_event(self):
        self.configure_widgets("disabled")
        self.event_manager.add_event(
            event_id="get_device_code",
            func=self.get_device_code,
            error_functions=[lambda: messagebox.showerror(self, "Error", "An unexpected error occured during the authorisation process.")],
            completion_funcs_with_result=[self.on_device_code_received],
            completion_functions=[lambda: self.configure_widgets("normal")]   
        )

    def get_device_code(self):
        device_code_result = request_device_code()
        if not device_code_result["status"]:
            return {
                "message": {
                    "function": messagebox.showerror,
                    "arguments": (self, "Error", device_code_result["message"])
                }
            }
        device_code_response = device_code_result["response"].json()
        verification_uri = device_code_response["verification_uri"]
        user_code = device_code_response["user_code"]
        device_code = device_code_response["device_code"]
        interval = device_code_response["interval"]
        return {
            "result": (verification_uri, user_code, device_code, interval),
        }
        
    def on_device_code_received(self, verification_uri, user_code, device_code, interval):
        self.configure_widgets("disabled")
        self.oauth_start_button.configure(state="disabled", text="Authorising...")
        self.auth_label.configure(text=f"You are being redirected to {verification_uri}...\nPlease enter the code: {user_code}. It has been copied to your clipboard")
        self.after(2000, webbrowser.open, verification_uri)
        self.clipboard_clear()
        self.clipboard_append(user_code)
        self.event_manager.add_event(
            event_id="get_token",
            func=self.get_token,
            kwargs={"device_code": device_code, "interval": interval},
            completion_funcs_with_result=[self.on_token_received],
            error_functions=[lambda: messagebox.showerror(self, "Error", "An unexpected error occured during the authorisation process.")],
            completion_functions=[lambda: self.configure_widgets("normal")]
        )
        
    def get_token(self, device_code, interval):
        start_time = time.time()
        while time.time() - start_time < 900:
            token_result = request_token(device_code)
            if not token_result["status"]:
                return {
                    "message": {
                        "function": messagebox.showerror,
                        "arguments": (self, "Error", token_result["message"])
                    }
                }
            token_result = token_result["response"].json()
            if token_result.get("access_token"):
                return {
                    "result": (token_result["access_token"],)
                }
            
            if token_result.get("error") == "authorization_pending":
                time.sleep(interval)
            elif token_result.get("error") == "slow_down":
                interval += 5
                time.sleep(interval)

        return {
            "message": {
                "function": messagebox.showerror,
                "arguments": (self, "Error", "Timed out waiting for authorisation.")
            }
        }
                
    def on_token_received(self, token):
        self.settings.token = token
        self.settings.save()
        messagebox.showsuccess(self, "Success", "Token received successfully.")
        
        
            
        

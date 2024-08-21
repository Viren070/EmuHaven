from CTkMessagebox import CTkMessagebox


def show_messagebox(title, message, icon, option_1="OK", option_2=None, option_3=None):
    output = CTkMessagebox(
        title=title,
        message=message,
        icon=icon,
        option_1=option_1,
        option_2=option_2,
        option_3=option_3,
        fade_in_duration=150,
        width=450,
        justify="center",
        sound=True,
        wraplength=350,
    ).get()
    return output if output is None else output.lower()


def showinfo(title, message, option_1="OK"):
    return show_messagebox(title=title, message=message, icon="info", option_1=option_1)


def showsuccess(title, message):
    return show_messagebox(title, message, "check", "OK")


def showwarning(title, message):
    return show_messagebox(title, message, "warning", "OK")


def showerror(title, message):
    return show_messagebox(title, message, "cancel", "OK")


def askyesno(title, message):
    return show_messagebox(title, message, "question", "Yes", "No")


def askokcancel(title, message, icon="question"):
    return show_messagebox(title, message, icon=icon, option_1="OK", option_2="Cancel")


def askretrycancel(title, message, icon="question"):
    return show_messagebox(title, message, icon=icon, option_1="Retry", option_2="Cancel")


def askyesnocancel(title, message):
    return show_messagebox(title, message, "question", "Yes", "No", "Cancel")

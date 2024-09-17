from CTkMessagebox import CTkMessagebox


def show_messagebox(master, title, message, icon, option_1="OK", option_2=None, option_3=None):
    output = CTkMessagebox(
        master=master,
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


def showinfo(master, title, message, option_1="OK"):
    return show_messagebox(master=master, title=title, message=message, icon="info", option_1=option_1)


def showsuccess(master, title, message):
    return show_messagebox(master=master, title=title, message=message, icon="check", option_1="OK")


def showwarning(master, title, message):
    return show_messagebox(master=master, title=title, message=message, icon="warning", option_1="OK")


def showerror(master, title, message):
    return show_messagebox(master=master, title=title, message=message, icon="cancel", option_1="OK")


def askyesno(master, title, message, icon="question"):
    return show_messagebox(master=master, title=title, message=message, icon=icon, option_1="Yes", option_2="No")


def askokcancel(master, title, message, icon="question"):
    return show_messagebox(master=master, title=title, message=message, icon=icon, option_1="OK", option_2="Cancel")


def askretrycancel(master, title, message, icon="question"):
    return show_messagebox(master=master, title=title, message=message, icon=icon, option_1="Retry", option_2="Cancel")


def askyesnocancel(master, title, message, icon="question"):
    return show_messagebox(master=master, title=title, message=message, icon=icon, option_1="Yes", option_2="No", option_3="Cancel")

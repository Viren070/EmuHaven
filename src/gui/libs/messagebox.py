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
        justify="center",
        sound=True
    ).get()
    return output if output is None else output.lower()


def show_info(title, message, option_1="OK"):
    return show_messagebox(title=title, message=message, icon="info", option_1=option_1)


def show_success(title, message):
    return show_messagebox(title, message, "check", "OK")


def show_warning(title, message):
    return show_messagebox(title, message, "warning", "OK")


def show_error(title, message):
    return show_messagebox(title, message, "cancel", "OK")


def ask_yesno(title, message):
    return show_messagebox(title, message, "question", "Yes", "No")


def ask_okcancel(title, message, icon="question"):
    return show_messagebox(title, message, icon=icon, option_1="OK", option_2="Cancel")


def ask_retrycancel(title, message, icon="question"):
    return show_messagebox(title, message, icon=icon, option_1="Retry", option_2="Cancel")


def ask_yesnocancel(title, message):
    return show_messagebox(title, message, "question", "Yes", "No", "Cancel")

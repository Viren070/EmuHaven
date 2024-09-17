class ProgressHandler:
    """
    Template class for progress handlers.

    Progress handlers are used to report progress, success, and errors to the user.
    They are used by functions that take a long time to complete, so that the user
    can see what is happening.

    The default implementation of this class does nothing. Subclasses should override
    the methods.

    Subclasses can use a GUI based progress handler to show a progress bar, or a text
    based progress handler to show a text display.

    Subclasses can also use a progress handler to implement a cancel button, so that
    the user can cancel the operation if it is taking too long. The should_cancel method
    will be called periodically to check if the user has pressed the cancel button within
    the functions and the cancel method will be called from these functions.
    """
    def report_progress(self, value):
        pass

    def report_success(self):
        pass

    def report_error(self, error):
        pass

    def set_total_units(self, total_units):
        pass

    def is_total_units_set(self):
        return True

    def should_cancel(self):
        pass

    def cancel(self):
        pass

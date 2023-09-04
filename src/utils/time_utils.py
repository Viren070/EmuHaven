
import datetime 
def calculate_relative_time(reset_timestamp):
    # Convert the timestamp to a datetime object
    reset_datetime = datetime.datetime.fromtimestamp(int(reset_timestamp))

    # Get the current datetime
    current_datetime = datetime.datetime.now()

    # Calculate the time difference
    time_difference = reset_datetime - current_datetime

    # Extract days, hours, and minutes
    days = time_difference.days
    seconds = time_difference.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Build the relative time string
    if days > 0:
        relative_time = f"{days} day{'s' if days > 1 else ''}"
    elif hours > 0:
        relative_time = f"{hours} hour{'s' if hours > 1 else ''}"
    elif minutes > 0:
        relative_time = f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        relative_time = "less than a minute"

    return f"{relative_time}"
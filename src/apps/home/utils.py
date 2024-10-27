import datetime

def format_number(number: int) -> str:
    formatted_balance = "{:,}".format(number)
    return formatted_balance


def convert_unix_to_local(unix_time):
    """
    Convert Unix timestamp to normal date-time.

    Args:
        unix_time (int): Unix timestamp.

    Returns:
        datetime.datetime: Date-time object.
    """
    return datetime.datetime.utcfromtimestamp(unix_time).date()

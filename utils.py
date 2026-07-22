import re
import warnings
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from datetime import datetime


def iso_to_mysql_datetime(iso_string):
    """
    Function to convert BlueSky datetime format (ISO) to MySQL datetime
    """
    if iso_string is None:
        return None

    try:
        # check if time zone ('Z') is included:
        if iso_string.endswith('Z'):
            # remove 'Z' und format the date, '00:00' is also UTC-time:
            dt = datetime.fromisoformat(iso_string[:-1] + '+00:00')
        else:
            # parsing in case of no information about time zone:
            dt = datetime.fromisoformat(iso_string)

        # format to MySQL DATETIME:
        mysql_datetime = dt.strftime("%Y-%m-%d %H:%M:%S")

        return mysql_datetime

    # catch error if sth with datetime formatting went wrong:
    except ValueError as e:
        print(f"Error converting iso to MySQL datetime: {e}")
        return None


def clean_html(html):
    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
    return (
        " ".join(BeautifulSoup(html, "html.parser").stripped_strings)
    )


def is_noise(tag):
    """
    This function returns `True` if a hashtag contains only
    'noise', i.e., does not contain meaningful information.
    tag = tag.lstrip('#')
    """

    if not tag:
        return True

    # explicit emoji handling (simple Unicode range fallback)
    if any(ord(c) > 10000 for c in tag):
        return False

    # pure digits
    if tag.isdigit():
        return True

    # structured junk
    if re.fullmatch(r'[a-f0-9]{8,}', tag, re.IGNORECASE):
        return True

    # tiny junk tokens
    if len(tag) <= 1:
        return True

    return False

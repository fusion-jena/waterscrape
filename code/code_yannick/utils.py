from bs4 import BeautifulSoup
from datetime import datetime


def iso_to_mysql_datetime(iso_string):
    """
    Function to convert BlueSky datetime format (ISO) to MySQL datetime
    """
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
    # import warnings
    # from bs4 import MarkupResemblesLocatorWarning
    # warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
    return (
        " ".join(BeautifulSoup(html, "html.parser").stripped_strings)
    )

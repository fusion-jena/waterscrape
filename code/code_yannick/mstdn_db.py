import requests
import json
import time
import mysql.connector
import os
from datetime import datetime
from dotenv import load_dotenv

from topics.hierarchy import get_keyword_variations
from utils import iso_to_mysql_datetime, clean_html


search_url = "https://mastodon.social/api/v2/search"
auth_url = "https://mastodon.social/api/v1/apps/verify_credentials"


def insert_account(cursor, status):
    account = status.get('account')
    account_id = account.get('id')

    # check if account_id already exists in ThWIC-DB:
    cursor.execute("SELECT * FROM accounts WHERE account_id=%s", (account_id,))
    account_exists = cursor.fetchone()

    # INSERT into accounts table if account doesn't already exist:
    if not account_exists:
        cursor.execute(
            "INSERT INTO accounts (account_id, is_bot, created_at, description, followers_count, following_count, statuses_count, last_status_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                account_id,
                account.get('bot'),
                iso_to_mysql_datetime(account.get('created_at')),
                account.get('note'),
                account.get('followers_count'),
                account.get('following_count'),
                account.get('statuses_count'),
                iso_to_mysql_datetime(account.get('last_status_at'))
            )
        )
        print(f"Account inserted: {account_id}")


def insert_post(cursor, status, keywords, keyword_category):
    # INSERT into posts table:
    # check if post already exists in ThWIC-DB:
    post_id = status.get('id')
    cursor.execute("SELECT * FROM posts WHERE post_id=%s", (post_id,))
    post_exists = cursor.fetchone()

    account = status.get('account')
    account_id = account.get('id')

    # post will only be inserted if it doesn't already exist in ThWIC-DB:
    if not post_exists:
        # extract domain from acct or set to mastodon.social
        acct = account.get('acct')
        if '@' in acct:
            domain = acct.split('@')[1]
        else:
            domain = 'mastodon.social'

        # insert in ThWIC-DB:
        content = status.get('content')
        content = clean_html(content)

        cursor.execute(
            "INSERT INTO posts (post_id, created_at, in_reply_to_id, is_sensitive, visibility, replies_count, reblogs_count, likes_count, content, languages, from_platform, instance_name, keyword_category, keywords, date_first_request, account_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                post_id,
                iso_to_mysql_datetime(status.get('created_at')),
                status.get('in_reply_to_id'),
                status.get('sensitive'),
                status.get('visibility'),
                status.get('replies_count'),
                status.get('reblogs_count'),
                status.get('favourites_count'),
                content,
                status.get("language"),
                'Mastodon',
                domain,
                keyword_category,
                keywords,
                datetime.now(),
                account_id
            )
        )
        print(f"Post inserted: {post_id}")


def insert_hashtag(cursor, status):
    post_id = status.get('id')
    tags = [tag["name"] for tag in status["tags"]]

    for tag in tags:
        cursor.execute("SELECT * FROM hashtags WHERE hashtag=%s", (tag,))
        tag_exists = cursor.fetchone()

        if not tag_exists:

            cursor.execute(
                (
                    "INSERT INTO hashtags "

                    "(hashtag)"
                    "VALUES (%s)"
                ),
                (
                    tag,
                )
            )

            hashtag_id = cursor.lastrowid
            cursor.execute(
                (
                    "INSERT INTO post_hashtags (post_id, hashtag_id) "
                    "VALUES (%s, %s)"
                ),
                (
                    post_id, hashtag_id
                )
            )
            print(f"Hashtag inserted: {hashtag_id}")


def insert_poll(cursor, status):
    post_id = status.get('id')

    # INSERT into polls table:
    if status.get('poll'):
        poll = status.get('poll')
        poll_id = poll.get('id')

        # check if poll is already in ThWIC-DB:
        cursor.execute("SELECT * FROM polls WHERE poll_id=%s", (poll_id,))
        poll_exists = cursor.fetchone()

        # insert poll in ThWIC-DB if it doesn't already exist there:
        if not poll_exists:
            cursor.execute(
                "INSERT INTO polls (poll_id, poll_expires_at, multiple_choice, votes_count, voters_count, options, post_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    poll_id,
                    iso_to_mysql_datetime(poll.get('expires_at')),
                    poll.get('multiple'),
                    poll.get('votes_count'),
                    poll.get('voters_count'),
                    json.dumps(poll.get('options')),
                    post_id
                )
            )
            print(f"Poll inserted: {poll_id}")


def insert_media(cursor, status):
    post_id = status.get('id')
    # INSERT into attachments table:
    # every attachment of the post should be considered:
    for attachment in status.get('media_attachments', []):
        attachment_id = attachment.get('id')

        # check if attachment already exists in ThWIC-DB:
        cursor.execute("SELECT * FROM media_attachments WHERE id_attachment=%s", (attachment_id,))
        attachment_exists = cursor.fetchone()

        # if the attachment doesn't already exist in ThWIC-DB, insert into DB:
        if not attachment_exists:
            cursor.execute(
                "INSERT INTO media_attachments (id_attachment, attachment_type, post_id) VALUES (%s, %s, %s)",
                (
                    attachment_id,
                    attachment.get('type'),
                    post_id
                )
            )
            print(f"Attachment inserted: {attachment_id}")


def extract_mastodon_db(keywords, keyword_category=None):
    if not keyword_category:
        from topics.hierarchy import get_keyword_dict
        keyword_dict = get_keyword_dict()
        keyword_category = keyword_dict[keywords]

    keyword_list = get_keyword_variations(keywords)

    load_dotenv()

    # Connect to ThWIC-DB:
    db_connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = db_connection.cursor()

    # Mastodon Authorization: the access_token can be copied from the Mastodon GUI
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    # save Authorization data:
    response = requests.get(auth_url, headers=headers)

    # Check if Authorization was successful:
    if response.status_code == 200:
        print("Authorization Request successful:")
        print(response.json())
    else:
        print("Authorization-Error:", response.status_code)
        return

    # Parameters for pagination:
    offset = 0  # number of entries to skip in the Mastodon DB, increases with every search request
    limit = 40  # max number of posts from one API-Request
    retry_attempts = 4

    # "until no further search results are found":
    i = 0
    n_limit = 1_000
    while True and i < n_limit:
        i += 1
        params = {
            'q': keywords,
            'offset': offset,
            'limit': limit,  # max number of posts retrieved from one single API-Request
            'type': 'statuses'  # type is needed because otherwise you could also search for the keywords in hashtags
            # and accounts
        }

        response = requests.get(search_url, headers=headers, params=params)

        # check for errors, else extract and push in DB:
        if response.status_code == 429:
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            wait_time = reset_time - int(time.time())
            print(f"Maximal Rate Limit. Wait {wait_time} seconds.")
            time.sleep(wait_time)
            continue
        # successful request:
        elif response.status_code == 200:
            print(f"Request successful with Offset {offset}:")

            # Get all the posts (= statuses) from one API-Request:
            json_data = response.json()
            statuses = json_data.get("statuses", [])

            # Make sure that it is not a server-side error if no further statuses are returned for specific offset:
            retry_count = 0
            while not statuses and retry_count < retry_attempts:
                print(f"no results returned, retrying... Attempt {retry_count + 1}/{retry_attempts}")
                time.sleep(2)  # small delay before retry
                response = requests.get(search_url, headers=headers, params=params)
                json_data = response.json()
                statuses = json_data.get('statuses', [])
                retry_count += 1

            if not statuses:
                print(f"no further search-results with offset {offset} after {retry_attempts} retries.")
                break

            # posts of an API-Request will be pushed into the ThWIC-DB:
            for status in statuses:
                for kw in keyword_list:
                    # extract account information:
                    try:
                        insert_account(cursor, status)
                        insert_post(cursor, status, kw, keyword_category)
                        insert_hashtag(cursor, status)
                        insert_poll(cursor, status)
                        insert_media(cursor, status)

                        # save the Accounts/Posts/Attachments/Polls in ThWIC-DB:
                        db_connection.commit()

                    # handle Errors that occur when inserting into ThWIC-DB:
                    except mysql.connector.Error as err:
                        print(f"Error inserting in DB: {err}")
                        db_connection.rollback()

            # increase offset for pagination, to get the next posts:
            offset += len(statuses)

        # further error-handling which was usually not necessary during data collection:
        elif response.status_code == 500:
            print(f"Internal Server Error for Request with Offset {offset}.")
            break
        elif response.status_code == 503:
            print(f"Service temporarily not available. Wait 60 seconds.")
            time.sleep(60)
            continue
        else:
            print(f"Error for Request with Offset {offset}: {response.status_code}")
            break

    db_connection.close()
    print(f"final offset (= first offset with zero results): {offset}")
    print(f"status code: {response.status_code}")

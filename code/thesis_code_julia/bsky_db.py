import requests
import mysql.connector
from datetime import datetime


# Function to convert BlueSky datetime format (ISO) to MySQL datetime:
def iso_to_mysql_datetime(iso_string):
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


def extract_bsky_db(keywords, keyword_category):
    print('started method extract_bsky')

    # Connect to ThWIC-DB:
    db_connection = mysql.connector.connect(
        host="mysql8p2.uni-jena.de",
        port="3306",
        user="i86hoxb7_thwicsonar",
        password="...",  # insert DB password here
        database="i86hoxb7_thwicsonar"
    )
    cursorDB = db_connection.cursor()

    # BlueSky Authorization: the app password is copied from my bsky account

    BLUESKY_HANDLE = "jubo.bsky.social"
    BLUESKY_APP_PASSWORD = "xc7o-c6sn-akwd-fnpx"

    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD},
    )

    # Check if Authorization was successful:
    if resp.status_code == 200:
        print("Authorization Request successful:")
        print(resp.json())
    else:
        print("Authorization-Error:", resp.status_code)
        return

    # save Authorization data in session variable:
    session = resp.json()

    # Start Search-Request for the keywords given as function parameters:
    base_url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"

    # Parameters for pagination:
    cursor = 0  # number of entries to skip in the BlueSky DB, increases with every search request
    limit = 100  # max number of posts retrieved from one single API-Request

    # "until no further search results are found":
    while True:
        params = {
            "q": keywords,
            "limit": limit,
            "cursor": cursor
        }
        headers = {"Authorization": "Bearer " + session["accessJwt"]}

        resp = requests.get(base_url, params=params, headers=headers)

        print(f"Anfrage erfolgreich mit Cursor {cursor}:")

        # get alle posts from one API-Request:
        json_data = resp.json()
        posts = json_data.get('posts', [])

        if not posts:
            print(f"No further search-results with offset {cursor}.")
            break

        # information of an API-Request will be pushed into the ThWIC-DB:
        for post in posts:
            account = post.get('author')
            account_id = account.get('did')
            record = post.get('record')
            embed = record.get('embed')
            post_id = post.get('cid')

            try:
                # check if account_id already exists in ThWIC-DB:
                cursorDB.execute("SELECT * FROM accounts WHERE account_id=%s", (account_id,))
                account_exists = cursorDB.fetchone()

                # INSERT into accounts table if account doesn't already exist:
                if not account_exists:
                    cursorDB.execute(
                        "INSERT INTO accounts (account_id, is_bot, created_at, description, followers_count, following_count, statuses_count, last_status_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            account_id,
                            None,
                            iso_to_mysql_datetime(account.get('createdAt')),
                            None,
                            None,
                            None,
                            None,
                            None
                        )
                    )
                    print(f"Account inserted: {account_id}")

                # INSERT into posts table:
                # check if post already exists in ThWIC-DB:
                cursorDB.execute("SELECT * FROM posts WHERE post_id=%s", (post_id,))
                post_exists = cursorDB.fetchone()

                # post will only be inserted if it doesn't already exist in ThWIC-DB:
                if not post_exists:
                    # extract further information for ThWIC-DB:
                    domain = account.get('handle')
                    reply = record.get('reply')
                    labels = bool(post.get('labels'))

                    if reply:
                        parent_reply = reply.get('parent')
                        parent_reply_uri = parent_reply.get('uri')
                    else:
                        parent_reply_uri = None

                    # insert in ThWIC-DB:
                    cursorDB.execute(
                        "INSERT INTO posts (post_id, created_at, in_reply_to_id, is_sensitive, visibility, replies_count, reblogs_count, likes_count, content, from_platform, instance_name, keyword_category, keywords, date_first_request, account_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            post_id,
                            iso_to_mysql_datetime(record.get('createdAt')),
                            parent_reply_uri,  # URI includes the ID (as DID)
                            labels,
                            None,
                            post.get('replyCount'),
                            post.get('repostCount'),
                            post.get('likeCount'),
                            record.get('text'),
                            'BlueSky',
                            domain,
                            keyword_category,
                            keywords,
                            datetime.now(),
                            account_id
                        )
                    )
                    print(f"Post inserted: {post_id}")

                # INSERT into media_attachments table:
                if embed is not None:  # media attachments are saved as embeds in BlueSky
                    for attachment in embed:
                        # for every attachment, the ID and the type of the attachment is extracted,
                        # the JSON structure of the attachment types differ, so they have to be handled separately:
                        attachment_type = embed.get('$type')

                        if attachment_type == 'app.bsky.embed.images':
                            type = 'image'
                            image_info = embed.get('images')

                            for image_item in image_info:
                                image = image_item.get('image', {})
                                ref = image.get('ref', {})
                                link = ref.get('$link')
                                attachment_id = link

                        elif attachment_type == 'app.bsky.embed.external':
                            type = 'external'
                            external_info = embed.get('external')
                            external_ref_info = external_info.get('thumb')

                            if external_ref_info is not None:
                                ref_external = external_ref_info.get('ref')
                                if ref_external is not None:
                                    link_external = ref_external.get('$link')
                                    attachment_id = link_external
                                else:
                                    print("No reference found in external embed, skipping this attachment.")
                            else:
                                # if the external attachment is no link, the json structure is unknown so it
                                # won't be inserted into ThWIC-DB:
                                print("No thumb found in external embed, skipping this attachment.")

                        elif attachment_type == 'app.bsky.embed.record':
                            type = 'post'
                            record_info = embed.get('record')
                            attachment_id = record_info.get('cid')
                        else:
                            attachment_type = None

                        if attachment_type is not None:  # ("if the post has an attachment":)
                            cursorDB.execute("SELECT * FROM media_attachments WHERE id_attachment=%s", (attachment_id,))
                            attachment_exists = cursorDB.fetchone()
                            # if the attachment doesn't already exist in ThWIC-DB, insert into DB:
                            if not attachment_exists:
                                cursorDB.execute(
                                    "INSERT INTO media_attachments (id_attachment, attachment_type, post_id) VALUES (%s, %s, %s)",
                                    (
                                        attachment_id,
                                        type,
                                        post_id
                                    )
                                )
                                print(f"Attachment inserted: {attachment_id} type: {type}")

                # save the Accounts/Posts/Attachments in ThWIC-DB:
                db_connection.commit()

            # handle Errors that occur when inserting into ThWIC-DB:
            except mysql.connector.Error as err:
                print(f"Error inserting in DB: {err}")
                db_connection.rollback()

        # increase cursor for pagination, to get the next posts:
        cursor += len(posts)




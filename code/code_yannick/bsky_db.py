import os
import requests
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime
from html import unescape

from topics.hierarchy import get_keyword_variations
from utils import iso_to_mysql_datetime, clean_html, is_noise


base_url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"
profile_url = "https://bsky.social/xrpc/app.bsky.actor.getProfile"


def insert_account(cursorDB, post, headers):
    account = post.get("author")
    account_id = account.get("did")

    profile = requests.get(
        profile_url, params={"actor": account_id}, headers=headers
    ).json()

    # Check if account_id already exists in ThWIC-DB:
    cursorDB.execute(
        "SELECT * FROM accounts WHERE account_id=%s", (account_id,)
    )
    account_exists = cursorDB.fetchone()

    # INSERT into accounts table if account doesn't already exist:
    if not account_exists:
        cursorDB.execute(
            "INSERT INTO accounts "

            "(account_id, is_bot, created_at, description, followers_count, "
            "following_count, statuses_count, last_status_at) "

            "VALUES "
            "(%s, %s, %s, %s, %s, %s, %s, %s)",

            (
                account_id,
                None,
                iso_to_mysql_datetime(account.get('createdAt')),
                profile.get("description"),
                profile.get("followersCount"),
                profile.get("followsCount"),
                profile.get("postsCount"),
                None
            )
        )
        print(f"Account inserted: {account_id}")


def insert_post(cursorDB, post, keywords, keyword_category):
    record = post["record"]
    account = post.get("author")
    post_id = post.get("cid")
    account_id = account.get("did")

    domain = account.get("handle")
    reply = record.get("reply")
    labels = bool(post.get("labels"))

    parent_reply_uri = reply.get("parent", {}).get("uri") if reply else None

    content = clean_html(record.get('text'))
    langs = record.get("langs")

    if type(langs) is list:
        langs = ",".join(langs)

    cursorDB.execute(
        (
            "INSERT IGNORE INTO posts "
            "(post_id, created_at, in_reply_to_id, is_sensitive, "
            "visibility, replies_count, reblogs_count, likes_count, "
            "content, languages, from_platform, instance_name, keyword_category, "
            "keywords, date_first_request, account_id) "
            "VALUES "
            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        ),
        (
            post_id,
            iso_to_mysql_datetime(record.get('createdAt')),
            parent_reply_uri,
            labels,
            None,
            post.get("replyCount"),
            post.get("repostCount"),
            post.get("likeCount"),
            content,
            langs,
            "BlueSky",
            domain,
            keyword_category,
            keywords,
            datetime.now(),
            account_id
        )
    )

    if cursorDB.rowcount == 1:
        print(f"Post inserted: {post_id}")
        if langs:
            lang_rows = [(post_id, lang.strip()) for lang in langs.split(",") if lang.strip()]
            cursorDB.executemany(
                "INSERT IGNORE INTO post_languages (post_id, language) VALUES (%s, %s)",
                lang_rows
            )
    else:
        print(f"Post skipped (already exists): {post_id}")


def insert_hashtag(cursorDB, post, keywords, keyword_category):
    record = post["record"]

    post_id = post.get("cid")
    # TODO: Handle and save hashtags
    if record.get("facets"):
        feats = [facet.get("features") for facet in record.get("facets")]
        # # Only take the first list element, as it shouldn't be possible
        # # to have multiple hashtags within the same position range (?)
        tags = [feat[0]["tag"] for feat in feats if "tag" in feat[0]]
    else:
        tags = []

    for tag in tags:

        if not tag:
            continue

        tag = unescape(tag).strip().lower().lstrip("#")

        if is_noise(tag) or not tag:
            continue

        cursorDB.execute(
            "SELECT hashtag_id FROM hashtags WHERE hashtag=%s",
            (tag,)
        )
        row = cursorDB.fetchone()

        if row:
            hashtag_id = row["hashtag_id"]
        else:
            cursorDB.execute(
                "INSERT INTO hashtags (hashtag) VALUES (%s)",
                (tag,)
            )
            hashtag_id = cursorDB.lastrowid

        cursorDB.execute(
            """
            INSERT IGNORE INTO post_hashtags (post_id, hashtag_id)
            VALUES (%s, %s)
            """,
            (post_id, hashtag_id)
        )

        print(f"Linked #{tag} → post {post_id}")


def insert_media(cursorDB, post):
    post_id = post.get("cid")
    record = post.get("record")
    embed = record.get("embed")

    # INSERT into media_attachments table:
    if embed is not None:  # media attachments are saved as embeds in BlueSky
        for attachment in embed:
            # For every attachment, the ID and the type is extracted,
            # the JSON structure of the attachment types differ,
            # so they have to be handled separately

            attachment_type = embed.get("$type")

            if attachment_type == "app.bsky.embed.images":
                type_ = "image"
                image_info = embed.get("images")

                for image_item in image_info:
                    image = image_item.get("image", {})
                    ref = image.get("ref", {})
                    link = ref.get("$link")
                    attachment_id = link

            elif attachment_type == "app.bsky.embed.external":
                type_ = "external"
                external_info = embed.get("external")
                external_ref_info = external_info.get("thumb")

                if external_ref_info is not None:
                    ref_external = external_ref_info.get("ref")
                    if ref_external is not None:
                        link_external = ref_external.get("$link")
                        attachment_id = link_external
                    else:
                        print(
                            "No reference found in external embed, "
                            "skipping this attachment."
                        )
                        continue
                else:
                    # If the external attachment is no link,
                    # the json structure is unknown so it won't
                    # be inserted into ThWIC-DB
                    print(
                        "No thumb found in external embed, "
                        "skipping this attachment."
                    )
                    continue

            elif attachment_type == "app.bsky.embed.record":
                type_ = "post"
                record_info = embed.get("record")
                attachment_id = record_info.get("cid")
            else:
                attachment_type = None
                attachment_id = None

            if attachment_type is not None and attachment_id is not None:
                cursorDB.execute(
                    "SELECT * FROM media_attachments "
                    "WHERE id_attachment=%s", (attachment_id,)
                )
                attachment_exists = cursorDB.fetchone()

                if not attachment_exists:
                    cursorDB.execute(
                        "INSERT INTO media_attachments "
                        "(id_attachment, attachment_type, post_id) "
                        "VALUES (%s, %s, %s)",
                        (
                            attachment_id,
                            type_,
                            post_id
                        )
                    )
                    print(
                        f"Attachment inserted: {attachment_id} type: {type_}"
                    )


def extract_bsky_db(keywords, keyword_category=None):
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
    cursorDB = db_connection.cursor(dictionary=True)

    BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
    BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

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

    # Save Authorization data in session variable:
    session = resp.json()

    # Start Search-Request for the keywords given as function parameters:

    # No. of entries to skip in the BlueSky DB
    cursor = 0  # Increases with every search request
    limit = 100  # Max no. of posts retrieved from one single API-Request

    # "until no further search results are found":
    i = 0
    n_limit = 1_000
    while True and i < n_limit:
        i += 1
        params = {
            "q": keywords,
            "limit": limit,
            "cursor": cursor,
            # "tag": tag,
        }
        # TODO: Do we really need to reassign on every iteration ?
        headers = {"Authorization": "Bearer " + session["accessJwt"]}

        resp = requests.get(base_url, params=params, headers=headers)

        print(f"Request successful with {cursor}:")

        # Get all posts from one API-Request:
        json_data = resp.json()
        posts = json_data.get("posts", [])

        if not posts:
            print(f"No further search results with offset {cursor}.")
            break

        # Information of an API-Request will be pushed into the ThWIC-DB:
        for post in posts:
            for kw in keyword_list:
                try:
                    insert_account(cursorDB, post, headers)
                    insert_post(cursorDB, post, kw, keyword_category)
                    # keywords might not be necessary ?
                    insert_hashtag(cursorDB, post, kw, keyword_category)
                    insert_media(cursorDB, post)

                    # Save the Accounts/Posts/Attachments in ThWIC-DB:
                    db_connection.commit()

                except mysql.connector.Error as err:
                    print(f"Error inserting in DB: {err}")
                    db_connection.rollback()

        # Increase cursor for pagination, to get the next posts:
        cursor += len(posts)

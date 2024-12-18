from bsky_db import extract_bsky_db
from mstdn_db import extract_mastodon_db

if __name__ == '__main__':

    # choose the function and insert keyword(s) you want to search for
    # and the category it belongs to as method parameters:

    extract_bsky_db('water scarcity', 'water conflict')

    extract_mastodon_db('water scarcity', 'water conflict')


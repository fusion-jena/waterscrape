# Topics

This directory contains hierarchical lists of water-related topics that this project is interested in gathering data on from social media platforms.

Currently, this project makes use of the `hierarchy-social-media.txt` file in order to access and categorize the keywords. Essentially, each keyword is used as a query on a social media platform, the corresponding accounts, posts, etc. are scraped and added to the database.

The code uses this hierarchy mainly through `hierarchy.py`, with a dictionary mapping each category to its keywords. This is used in the database in order to infer the field `keyword_category` from the current `keyword`. For example, after querying and saving content for the keyword `hierarchy_Social_Media.txt`, the post is categorized as `natural_sciences` via the dictionary.

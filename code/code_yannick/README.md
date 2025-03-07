# Scraping water-based social media data

## Data extraction

Currently, we use `main.py` to extract data on a certain keyword and keyword category and save it to a database.

Example usage of the script:

```bash
$ python3 main.py bluesky --keywords "water scarcity" --keyword_category "water conflict"
```

## Database structure

We can take a look at the foreign key relationships:


```sql
SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME 
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'i86hoxb7_thwicsonar'
AND REFERENCED_TABLE_NAME IS NOT NULL;
```

```bash
+-------------------+-------------+--------------------------+-----------------------+------------------------+
| TABLE_NAME        | COLUMN_NAME | CONSTRAINT_NAME          | REFERENCED_TABLE_NAME | REFERENCED_COLUMN_NAME |
+-------------------+-------------+--------------------------+-----------------------+------------------------+
| media_attachments | post_id     | media_attachments_ibfk_1 | posts                 | post_id                |
| polls             | post_id     | fk_polls_posts           | posts                 | post_id                |
| posts             | account_id  | posts_ibfk_1             | accounts              | account_id             |
+-------------------+-------------+--------------------------+-----------------------+------------------------+
```

Each `media_attachment` and `poll` has a `post`, each post is associated with an `account`.

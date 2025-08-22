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

## Run with `cron`

As opposed to manually running the scraping script with specific keywords like in the example above, we use the `cron` scheduler to automatically execute the script in set time intervals. This repository is cloned onto a remote server accessed via SSH, where we submit one `cron` job for each platform. The result is an automatic scrape taking place once a week.

In order to access the server, make sure the university's `sci-std-VPN` VPN is active. Follow the [wiki page](https://wiki.uni-jena.de/spaces/URZ010SD/pages/22453512/VPN+-+zuhause+und+unterwegs) to setup the VPN. 

For example, we can use `OpenConnect` on a Linux machine:

```bash
$ sudo openconnect -b --useragent 'AnyConnect' --user=ab12cde@uni-jena.de --pid-file=/var/run/vpn.pid --timestamp --syslog vpn.sci.uni-jena.de
```

Then, connect to the SSH server with our given username:

```bash
$ ssh lab12cde@thwicsonar.inf-bb.uni-jena.de
```

# Scraping water-based social media data

## Data extraction

Currently, we use `main.py` to extract data on a certain keyword and keyword category and save it to a database.

Example usage of the script:

```bash
$ python3 main.py bluesky --keywords "water scarcity" --keyword_category "water conflict"
```

If the `keywords` and `keyword_category` arguments are not provided explicitly, the script will run the scraping process for all keywords contained in the file `hierarchy_Social_Media.txt`.

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

## Instructions

### Prerequisites

In order to run the main scraping script, make sure to install the necessary requirements:

```bash
$ pip install -r requirements.txt
```

The directory must also contain a `.env` file with the necessary credentials for both the MySQL user and the social media accesses:

```bash
DB_HOST=mysql8p2.uni-jena.de
DB_PORT=3306
DB_USER=<username>
DB_PASSWORD=<password>
DB_NAME=i86hoxb7_thwicsonar
BLUESKY_HANDLE=<bluesky-username>
BLUESKY_APP_PASSWORD=<bluesky-password>
ACCESS_TOKEN=<mastodon-access-token>
```

Finally, the university's `sci-std-VPN` must be active in order to connect to the MySQL server, and for the SSH server if one intends to use `cron` to run the code automatically. Follow the [wiki page](https://wiki.uni-jena.de/spaces/URZ010SD/pages/22453512/VPN+-+zuhause+und+unterwegs) to setup the VPN. 

For example, we can use `OpenConnect` on a Linux machine:

```bash
$ sudo openconnect -b --useragent 'AnyConnect' --user=ab12cde@uni-jena.de --pid-file=/var/run/vpn.pid --timestamp --syslog vpn.sci.uni-jena.de
```

### Run with `cron`

As opposed to manually running the scraping script with specific keywords like in the example above, we use the `cron` scheduler to automatically execute the script in set time intervals. This repository is cloned onto a remote server accessed via SSH, where we submit one `cron` job for each platform. The result is an automatic scrape taking place once a week.

Once the `sci-std-VPN` is active, connect to the SSH server with your given username:

```bash
$ ssh lab12cde@thwicsonar.inf-bb.uni-jena.de
```

This repo can then be cloned and setup on the server with a virtual environment. Once this is done, one or multiple `cron` jobs can be submitted in order to automatically run the code whenever specified. Use `crontab -l` to check if the correct command and time have been submitted for each job.

# Scraping water-based social media data

![Workflow](workflow.png)

## Data extraction

Currently, we use `main.py` to extract data on a certain keyword and keyword category and save it to a database.

Example usage of the script:

```bash
$ python3 main.py bluesky 1000 --keywords "water scarcity" --keyword_category "water conflict"
```

If the `keywords` and `keyword_category` arguments are not provided explicitly, the script will run the scraping process for all keywords contained in the file `hierarchy-social-media.txt`.

Due to the scarcity of some of the rare keywords, we provide an additional argument that specifies a minimum post number for a given keyword. For example, if a given keyword has less than `k = 1000` posts, it is omitted from the scraping process and not taken into consideration for further analysis.


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

### Sentiment analysis

The sentiment analysis is designed to take place in two separate steps. The `fetch_posts.py` saves relevant columns from the database table to a CSV table. For faster computation, we run the sentiment analysis from a separate Draco cluster with the use of GPUs. This results in the following workflow from KSZ:

```text
$ python3 fetch_posts.py
$ scp posts_likes.csv qe75hep@login1.draco.uni-jena.de:/home/qe75hep/yannick_hiwi/code/code_yannick/posts_likes.csv
```

Then login to Draco for the analysis step:

```text
$ ssh qe75hep@login1.draco.uni-jena.de
$ cd yannick_hiwi/code/code_yannick
```

And submit a Slurm job:
```text
$ sbatch run.sh
```

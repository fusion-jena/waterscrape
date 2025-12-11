- Meeting Room: https://bbb.mirz.uni-jena.de/b/div-pr2-ydt-1k7
- Meeting time: TBD

<!-- template
# 2023/xx/xx
## Orga
## Last week
## Feedback
## Next steps
-->

- potentially change or remove rare keywords
- find out if problem fixes itself with max limit on keyword searches

TODO:
- [x] change datatype from keyword to longer varchar
- [x] ensure all queries are lowercase

hierarchy todos:
- add info to (separate) README about:
  * asterisk, suffix, prefix and slash
  * potentially handle suffix/prefix in code as well for future use ?

- next meeting with three of us potentially:
  * 25th of august 11-12:30

TODO:
- fix attachment bug
- [x] don't manually provide keyword arguments
  * read all keywords from hierarchy

- [x] add explanation in README for cron job + SSH

- [x] find out whether cron jobs run in parallel
  * if not, maybe make mastodon and bluesky run at different times

- cleaning HTML tags and links

# 13.06.2025

- ssh <local-account>@<hostname?>.inf-bb.uni-jena.de
- use `cron` job to schedule

# 02.05.2025

- [x] create sketch/overview of DBs

- [x] remove redundant category table and references
- [x] handle multiple hashtags per post


# 18.04.2025

- does it make sense to search by hashtag directly?
  * use a combination of additional search terms/hashtag to better filter posts
- does it make sense to infer keyword/category by the hashtag? 

- next meeting on 02.05.2025

# 07.03.2025

- either copy database locally and then modify contents
- or get access to CREATE/ask Julia how she did it -> create copies 

- update keywords (possible choices)
- get accounts information bluesky

Optional:

- [x] cleanup code/breakup big function

Next meeting scheduled 21.03. 13:00.

# 11.02.2025

- [x] Get MySQL Workbench running (fix dependency error)
- [x] Find out how size of tables 
  - [x] Make copies of tables (+ Python scripts)

- [ ] start with point 2 in https://pad.uni-jena.de/nE-N5lt9T3GgjEgZ23rNKw# 

Optional/add-ons:

- [x] Make db connection use environment variables
- [x] Change main script to use command line arguments (?)

Next meeting scheduled for 07.03., 13:00.

# 19.12.2024

- [x] Create University of Jena login (itservice@uni-jena.de)
  * [x] Setup VPN and Element
- [x] Get permissions for MySQL database

- Skim thesis, focus on 6.4 DB overview + future work

# 2.07.2024 

## Orga
- @Daphne: finalized keywords?

## Last week

- Outcome of meeting with Data Protection Officer
    - working with personal data for Univesity projects is ok, she even wrote a summary about that which I'll probably include in thesis
    - indirectly informing people about which data will be collected would be good -> include that on a Website?
    - for giving the Social Media Data to a company: this has to be discussed with her again and there's also the AI Regulation which   has to be considered

- all "two categories" of keywords in DB?

- do you have an idea about how exactly the "history" will be included in DB? 
    
## feedback

## Next steps
- get comments for theory part of thesis
- finally push Mstdn and Bsky Data in DB

# 18.06.2024 

## Orga
- mid next week: time to read thesis?

## Last week
- modified DB
- -> main question: what is dynamic info? -> account description can also be dynamic -> "data which comes from other people than the publisher (account) of the post"
- Mastodon Code
- wrote Data Protection Officer (german: Datenschutzbeauftragte) of our University

- questions:
- DB: Uniqueness of post_id and account_id
- -> do you already know if you will also use other platforms than BlueSky and Mastodon?
- -> and other instances on these platforms?
    
## feedback

## Next steps



# 30.05.2024 

## Orga

## Last week
- read sth about GDPR (General Data Protection Regulation) and DSGVO (Datenschutzgrundverordnung)
- reference projects for data protection?
- after thesis: who needs access to DB?
- FUSION group structure: working for ThWIC project is seen as scientific research?
- Recomm system: not show deleted posts
- only save data for 3 years?

- found third law: Landesdatenschutzgesetz (Thüringen)

    
## feedback

## Next steps



# 22.05.2024 

## Orga
- Gendering in thesis?!

## Last week
- wanted to finish unification chapter, but discovered there are several optional Mastodon properties to add -> now: just one left :) 
- read sth about GDPR (General Data Protection Regulation) and DSGVO (Datenschutzgrundverordnung) -> I suggest that you read the unification chapter after I also finished this chapter
- converted everything from Word to LaTeX -> formatting still not great, but it gets better step by step

- questions: 
-	structure of DB? -> separate table, e.g. for polls (https://docs.joinmastodon.org/entities/Poll/)? -> more storage efficient?
-	further information relevant and include in DB? -> e.g. from_Plattform, Keyword_category, keywords/s, date of request, ID in ThWIC DB, last change at, ... -> further ideas?
-   updating the DB: should all posts be collected at the same day? -> Divyasha: no, only mention in discussion part

    
## feedback

## Next steps
- (really) finish unification chapter
- LaTeX
- finish text/table for unification of Bsky and Mastodon Posts
    - get feedback for that 


# 16.05.2024 

## Orga
- when time to read unification chapter?

## Last week
- wanted to finish unification chapter, but discovered there are several optional Mastodon properties to add

- questions: 
-	structure of DB? -> separate table, e.g. for polls?
-	further information relevant and include in DB? -> e.g. from_Plattform, Keyword_category, keywords/s, date of request, ID in ThWIC DB, last change at, ... -> further ideas?
-   updating the DB: should all posts be collected at the same day?
-	Gendering in thesis?
-   package for LaTeX quotation?
-   new structure of thesis -> more focussed on project part?
    
## Feedback
- write code in english

## Next steps
- (really) finish unification chapter
- finish text/table for unification of Bsky and Mastodon Posts
    - get feedback for that 



# 23.04.2024 

## Orga
- access for VMs?

## Last week
- start write unificaition chapter of posts from Bsky and Mastodon, all properties?
- experimenting with MySQL DB locally

- questions: 
-	structure of DB? -> one table per platform
-   Use Cases: mention only Daphnes Recomm System or define several other Use Cases?
-	Gendering?

    
## Feedback
- structure of DB: only one table
- describe all JSON properties of Bsky and Mastodon posts
- define other Use Cases

## Next steps
- get access to VM of faculty
- finish text/table for unification of Bsky and Mastodon Posts
    - get feedback for that
- ask PA again if thesis is now registered


# 8.03.2024 (instead of 5.03.2024)

## Orga
- register thesis next week! -> orga: Master Thesis?
## Last week
- research about how I can retrieve posts ("statuses") from Mastodon
    - reminder: 
        - we chose to not use elasticsearch, 
        - the v1 API of Mastodon is deprecated,
        - we looked for alternatives for the timelines API since the v2 API seemed to offer special
         "search functionality": https://docs.joinmastodon.org/methods/search/ 
        - we tried to do requests with v2 API together but it didn't work so I continued with v1 API
        - we wanted to find out how we can retrieve more requests than just the last x ones
            - found out that this could be possible because of Snowflake IDs
    - now:
        - I can retrieve posts using the v2 API (e.g.: https://mastodon.social/api/v2/search?q=water)
        - found out that I can use the search functionality with offset parameter
            - probably better than Snowflake IDs because I use offset ("cursor") also in Bsky
            - requires Authorisation https://docs.joinmastodon.org/methods/search/ 
        - implemented Python Code but still have to test it, 
            - was already able to retrieve Posts from 1.02.2024 with offset=~9500

    
## Feedback

## Next steps
- find out ho to search for multiple keywords within one requests
    - for Bsky and Mastodon
- find out if possible to get posts from ~ 8 months ago (in April 2023 Bsky was released)
- find title for thesis



# 9.02.2024

## Orga
- NA
## Last week
- research about how many posts I can retrieve from Bsky and Mastodon:

- Bsky:
    - documentation of AT Protocol: cursor-based pagination is possible: https://atp.readthedocs.io/en/latest/atproto/atproto_client.models.app.bsky.feed.search_posts.html
    - about the cursors and pagination: https://atproto.com/specs/xrpc 
    - experiment: 100 posts per page, the biggest cursor possible is about 9000, 
	    so for keyword “water” we can get posts from five to six days ago

- Mastodon: 
    - Snowflake IDs: https://readthedocs.org/projects/mastodonpy/downloads/pdf/latest/ p. 7

    
## Feedback

## Next steps
- still from last week: concept workflow
    - data collection (Datensammlung mit Suche)
    - data consolidation (Datenvereineinheitlichung)
        - JSON file for all data
        - how to deal with missing fields
    - what is the next step after data consolidation ? ..

- set a limit for the number of posts? what is possible ? maybe per year
    - -> try the findings



# 30.01.2024

## Orga
- NA
## Last week
- looked about how to search over tags and posts in masterdon and in bluesky
    - link the documentation or put directly (word document and put in repo)
## Feedback
- include findings in the thesis text with references
    - mastedon offers different types of search over their content:
        - api search method -> not supported why
        - elastic search -> not supported why
        - search over tags using timelines content -> explain how
## Next steps
- concept workflow
    - data collection (Datensammlung mit Suche)
    - data consolidation (Datenvereineinheitlichung)
        - JSON file for all data
        - how to deal with missing fields
    - what is the next step after data consolidation ? ..
- set a limit for the number of posts? what is possible ? maybe per year 

# 14.11.23
* talked with Daphne:
    * How save Social Media Data in a unified way?
    * main goal: Recommendations System (in Social Media Context, recommend either posts or
accounts)
        * --> I have to save especially the following information:
        * 1) Number of views of a post
        * 2) Number of Likes of a post
        * 3) Number of comments on a post
        * 4) (find out related words in that post to recommend Hashtags/Keywords) --> the text of a post also has to be saved
        * 5) Account (ID) of the creator of a post 
            * --> Account (IDs) who posted a post of interest (= post with specific keyword)
            * --> table: Account ID, number of posts of interest, keyword(s) of the post(s)
    * --> next steps:
        * 1) find out if this information can be extracted via the official APIs
        * 2) find out which additional metadata can be extracted via the official APIs
        * 3) try BlueSky --> @Divyasha?
* Questions:
    * 1) are three Social Media Platforms enough for the thesis?
    * 2) relevant question for the whole project, especially Daphne: how do normal Recommendation Systems work in comparison to Social Media Recommendation Algorithms?
    * 3) in Thesis: should I also write about the whole Thwic Project or is it just about extracting and saving Social Media Data?

* Structure of thesis (suggestion)
    * 1) Theoretical aspects
    * 1.1) Introduction/Motivation
    * 1.2) how data (or social science data) is saved in general, regarding:
        * technical way (e.g. Database/public txt file),
        * logical way (e.g. structure, metadata)
    * 1.3) identify specific properties of SM Data (in comparison to normal data), e.g. scale, speed, platform dependence, ownership, …
    * 1.4) identify specific use cases of SM Data in Social Science (in comparison to normal data)
    * 1.5) identify how SM Data should be saved in comparison to normal data
    * 2) Project
        * explain Thwic Project and the role of my bachelor thesis
        * how can SM Data be useful for “wasserwerk thueringen” (explain why e.g. LinkedIn instead of Insta, explain Use Cases e.g. find experts and innovations) 
        * how can this data be scraped/extracted from different platforms
        * how can this data be saved  (s. Theory, technicaly + logically)






# 24.10.23

## Orga

-   [x] GitLab setup
-   [x] Invited to fusion matrix room
-   [ ] invited to room  ask brigitta
- 	[x] matrix setup
-   [x] creation of a room in matrix with all supervisors
-   [ ] Register in the fusion-all mailing list: https://lserv.uni-jena.de/mailman/listinfo/fusion-all (with uni-jena email address)
-   [ ] Register: https://lserv.uni-jena.de/mailman/listinfo/fusion-phdscrum
-   [x] is a laptop needed? virtual machine needed ?
-   Status Meetings: **_needs to be defined_**
-   [x] Access to [phd scrum file](https://git.rz.uni-jena.de/fusion/orga/-/blob/master/phdscrum_minutes.md)
	-   Phd Scrum participation every monday at 10h.
-   Latex, Word, OpenOffice/LibreOffice? up to the student to decide which tool to use
    -   In case of latex usage here some templates provided from teh group: https://git.rz.uni-jena.de/fusion/template
-   form for registration and template for title page and "Selbständigkeitserklärung" available online:
    -   https://www.fmi.uni-jena.de/fmi_femedia/studium/studienorganisation/service-und-downloads/antrag-masterarbeit-20201.pdf
    -   https://www.fmi.uni-jena.de/fmi_femedia/studium/studienorganisation/service-und-downloads/antrag-masterarbeit-anlagen-2021.pdf
    -   https://www.fmi.uni-jena.de/fmi_femedia/studium/studienorganisation/service-und-downloads/gestaltungshinweise-masterarbeit.pdf
-   if you need urgent feedback, do not wait for the next meeting, you can contact via slack or email
-   literature management tool: e.g., Jabref ..
-   concrete time schedule and milestones within the first month
-   Topic discussion
    - social media platforms: Mastodon, Bluesky, Facebook, Instagram, LinkedIn, Twitter (X)
    - look after APIs 
    - literature 

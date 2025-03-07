import mysql.connector

db_config = {
    "host": "mysql8p2.uni-jena.de",
    "user": "i86hoxb7_qe75hep",
    "password": ".tr2dp8K!QtMRr+F",
    "database": "i86hoxb7_thwicsonar",
    "port": 3306
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

print("Success!")

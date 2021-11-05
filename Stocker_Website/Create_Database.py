import psycopg2
import pandas as pd

# todo Find away to run this script automaticly

""" DELETES ORIGINAL DATABASE
    AND CREATES A NEW ONE FROM
    THE WSB_TRACKER.CSV FILE """


conn = psycopg2.connect(
    host="localhost",
    database="stocker",
    user="brandonbischoff",
    password="stocker")

curs = conn.cursor()

delete_table = """ DROP TABLE the_stocks CASCADE; """
curs.execute(delete_table)

create_table = """CREATE TABLE the_stocks(
            primarykey Int PRIMARY KEY,
            name VARCHAR(10),
            source VARCHAR(50),
            purchase_date TIMESTAMP)"""
curs.execute(create_table)
df = pd.read_csv(
    "/Users/brandonbischoff/Stocker/Stocker_Website/WSB_Tracker.csv")
df = df[["Name", "Source", "Time_Added", "Purchase_Date"]]
records = df.to_records()

for record in records:

    curs.execute("""INSERT INTO the_stocks
        VALUES (%s,%s,%s,%s)""", (int(record[0]), record[1], record[2], record[4]))

conn.commit()

#!/usr/bin/python
import psycopg2
from datetime import datetime

def insert_projectdata(message):
    """ insert a new vendor into the vendors table """
    sql = """I"""

    query = "INSERT INTO PROJECTDATA (gpsx, gpsy, humidity, temperature, lighting, ts) VALUES (%s, %s, %s, %s, %s, %s);"
    query2 = "DELETE FROM PROJECTDATA"
    data =  (12345, 1234, 1, 43345, 10123123, datetime.now())

    conn = None
    try:
        # connect to the PostgreSQL database
        conn =  conn = psycopg2.connect(host="localhost", database="Project3", user="postgres", password="fay42fwv")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query2, data)
        cur.execute(query, data)

        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
     insert_projectdata('Goodnight!')
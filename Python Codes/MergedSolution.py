import paho.mqtt.client as mqtt
import psycopg2
from datetime import datetime
# The callback for when the client receives a CONNACK response from the server.
temperature = ""
humidity = ""
xcoor = ""
ycoor = ""
lum = ""
id = 0

def insert_projectdata(ID, Humidity, Temperature, Lighting, gpsx, gpsy, ts, Device):
    print("function initialized")
    queryDen = "INSERT INTO iotdata (id, humidity, temperature, lighting, gpsx, gpsy, ts) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    queryVal = "INSERT INTO iotdata2 (id, humidity, temperature, lighting, gpsx, gpsy, ts) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    DeleteDen = "delete from iotdata where id = {}"; #used for making space for new upcoming data
    DeleteVal = "delete from iotdata2 where id = {}";
    data =  (ID, Humidity, Temperature, Lighting, gpsx, gpsy, ts)
    conn = None
    try:
        print("replacing data")
        conn = conn = psycopg2.connect(host="localhost", database="projectData", user="postgres", password="igra1122")
        cur = conn.cursor()
        if(Device == "device1"):
            print("First device")
            cur.execute(DeleteDen.format(ID)) #delete the data in a row if a matching ID is already taken
            cur.execute(queryDen, data) #upload data
        elif(Device == "device2"):
            print("Second device")
            cur.execute(DeleteVal.format(ID))
            cur.execute(queryVal, data)
        conn.commit()
        cur.close()
        print("success")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def HandlePayload(message):
    global temperature,humidity,xcoor,ycoor,lum
    separatedmessage = message.split(",")
    for i in range(0,len(separatedmessage)):
        temp = separatedmessage[i]
        if (temp[0]=="T"):
            temperature = round(filterDigits(temp),2)
        elif (temp[0]=="H"):
            humidity = round(filterDigits(temp),2)
        elif (temp[0]=="X"):
            xcoor = filterDigits(temp)
        elif (temp[0]=="Y"):
            ycoor = filterDigits(temp)
        elif (temp[0]=="L"):
            lum = int(filterDigits(temp))


def filterDigits(a):
    temp2 = float(''.join(digit for digit in a if digit.isdigit() or digit == "."))
    return temp2

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("IDDeniss/#",qos = 1) #subscribe to the response topic

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global id
    topicRecieved = msg.topic
    device = topicRecieved.split("/")[1]
    messageReceived = msg.payload.decode()
    HandlePayload(messageReceived)
    print(temperature, humidity, ycoor, xcoor, lum)
    id += 1 #going through the 10 database rows to fill
    if id > 10:
        id = 1
        insert_projectdata(id, humidity, temperature, lum, xcoor, ycoor, datetime.now(),device)

client = mqtt.Client()
client.connect("test.mosquitto.org", 1883, 60)
client.on_connect = on_connect
client.on_message = on_message

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
client.loop_forever()

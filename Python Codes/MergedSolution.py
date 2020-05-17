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
    DeleteDen = "delete from iotdata where id = {}";
    DeleteVal = "delete from iotdata2 where id = {}";
    data =  (ID, Humidity, Temperature, Lighting, gpsx, gpsy, ts)
    conn = None
    try:
        print("replacing data")
        conn = conn = psycopg2.connect(host="localhost", database="projectData", user="postgres", password="igra1122")
        cur = conn.cursor()
        if(Device == "device1"):
            print("First device")
            cur.execute(DeleteDen.format(ID))
            cur.execute(queryDen, data)
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
            temperature = round(float(filterDigits(temp)),2)
        elif (temp[0]=="H"):
            humidity = round(float(filterDigits(temp)),2)
        elif (temp[0]=="X"):
            xcoor = float(filterDigits(temp))
        elif (temp[0]=="Y"):
            ycoor = float(filterDigits(temp))
        elif (temp[0]=="L"):
            lum = int(float(filterDigits(temp)))


def filterDigits(a):
    temp2 = ''.join(digit for digit in a if digit.isdigit() or digit == ".")
    return temp2

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("IDDeniss/#",qos = 1) #subscribe to the response topic

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global id
    message = open("message.txt", "w+") #create a file in the current folder that will hold the received status
    topicRecieved = msg.topic
    print(topicRecieved)
    messageReceived = msg.payload.decode()
    print(messageReceived)
    HandlePayload(messageReceived)
    print(temperature, humidity, ycoor, xcoor, lum)
    id += 1
    if id > 10:
        id = 1
    if(topicRecieved == "IDDeniss/esptest"):
        insert_projectdata(id, humidity, temperature, lum, xcoor, ycoor, datetime.now(),"device1")
    if (topicRecieved == "IDDeniss/device2"):
        insert_projectdata(id, humidity, temperature, lum, xcoor, ycoor, datetime.now(),"device2")
    message.write(messageReceived) #write the message into the text file

client = mqtt.Client()
client.connect("test.mosquitto.org", 1883, 60)
client.on_connect = on_connect
client.on_message = on_message

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

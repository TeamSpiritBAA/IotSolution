from datetime import datetime
import paho.mqtt.client as mqtt
import psycopg2

temperature = humidity = lum = xcoor = ycoor = ""
id = 0

class databaseCommunication:
    def __init__(self,ID,Humidity,Temperature,Lighting,gpsx,gpsy,ts,Device):
        self.ID = ID
        self.Device = Device
        self.data =  (ID, Humidity, Temperature, Lighting, gpsx, gpsy, ts)
    def insert_projectdata(self):
        print("function initialized")

        #queries
        queryDen = "INSERT INTO iotdata (id, humidity, temperature, lighting, gpsx, gpsy, ts) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        queryVal = "INSERT INTO iotdata2 (id, humidity, temperature, lighting, gpsx, gpsy, ts) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        DeleteDen = "delete from iotdata where id = {}"; #used for making space for new upcoming data
        DeleteVal = "delete from iotdata2 where id = {}";
        conn = None
        try:
            print("replacing data")
            conn = conn = psycopg2.connect(host="localhost", database="projectData", user="postgres", password="igra1122")
            cur = conn.cursor()
            if(self.Device == "device1"):
                print("First device")
                cur.execute(DeleteDen.format(self.ID)) #delete the data in a row if a matching ID is already taken
                cur.execute(queryDen, self.data) #upload data
            elif(self.Device == "device2"):
                print("Second device")
                cur.execute(DeleteVal.format(self.ID))
                cur.execute(queryVal, self.data)
            conn.commit()
            cur.close()
            print("success")
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

class ProcessMessages:
    def __init__(self,message):
        self.message = message

    def HandlePayload(self): #method for separating the incoming mqtt string from the embedded system into corresponding variables
        global temperature,humidity,xcoor,ycoor,lum
        separatedmessage = self.message.split(",")
        for i in range(0,len(separatedmessage)):
            temp = separatedmessage[i]
            if (temp[0]=="T"):
                temperature = round(self.filterDigits(temp),2)
            elif (temp[0]=="H"):
                humidity = round(self.filterDigits(temp),2)
            elif (temp[0]=="X"):
                xcoor = self.filterDigits(temp)
            elif (temp[0]=="Y"):
                ycoor = self.filterDigits(temp)
            elif (temp[0]=="L"):
                lum = int(self.filterDigits(temp))

    @staticmethod
    def filterDigits(a): #helper function
        temp2 = float(''.join(digit for digit in a if digit.isdigit() or digit == "."))
        return temp2

class MQTTclass(mqtt.Client):
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("IDDeniss/#",qos = 1) #subscribe to the response topic

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self,client, userdata, msg):
        global id
        topicRecieved = msg.topic
        device = topicRecieved.split("/")[-1] #part of the topic corresponding to the device
        messageReceived = msg.payload.decode()
        toVariables = ProcessMessages(messageReceived)
        toVariables.HandlePayload() #separates payload string
        print(temperature, humidity, ycoor, xcoor, lum)
        id += 1 #going through the 10 database rows to fill
        if id > 10:
            id = 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #formats to exclude microseconds
        databaseInstance = databaseCommunication(id, humidity, temperature, lum, xcoor, ycoor, timestamp, device)
        databaseInstance.insert_projectdata() #uploading data to the postgres database


if __name__ == '__main__':
    client = MQTTclass()
    client.connect("mqtt.eclipse.org", 1883, 60)
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    client.loop_forever()

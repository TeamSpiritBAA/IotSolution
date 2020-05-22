import threading

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:igra1122@localhost/projectData' #edit as in: username:password@host/database
db = SQLAlchemy(app)

class iotdata(db.Model): #first device table class
   id = db.Column('id', db.Integer, primary_key = True)
   humidity = db.Column(db.Numeric(20,2))
   temperature= db.Column(db.Numeric(20,2))
   lighting = db.Column(db.Numeric(20,1))
   gpsx = db.Column(db.Numeric(20,6))
   gpsy = db.Column(db.Numeric(20,6))
   ts = db.Column(db.TIMESTAMP)

   def __repr__(self):
       return f"{self.id},{self.humidity},{self.temperature},{self.lighting},{self.gpsx},{self.gpsy},{self.ts}"

class iotdata2(db.Model): #second device table class
   id = db.Column('id', db.Integer, primary_key = True)
   humidity = db.Column(db.Numeric(20,2))
   temperature= db.Column(db.Numeric(20,2))
   lighting = db.Column(db.Numeric(20,1))
   gpsx = db.Column(db.Numeric(20,6))
   gpsy = db.Column(db.Numeric(20,6))
   ts = db.Column(db.TIMESTAMP)

   def __repr__(self):
       return f"{self.id},{self.humidity},{self.temperature},{self.lighting},{self.gpsx},{self.gpsy},{self.ts}"


myIotdata1 = [] #variables for the first device
IDlist1 = []
HUMlist1 = []
TMPlist1 = []
LUXlist1 = []
Xlist1 = []
Ylist1= []
TSlist1 = []

myIotdata2 = [] #variables for the second device
IDlist2 = []
HUMlist2 = []
TMPlist2 = []
LUXlist2 = []
Xlist2 = []
Ylist2 = []
TSlist2 = []

def PushData(dataToSplit,idlist,humlist,tmplist,luxlist,xlist,ylist,tslist):
    for i in range(0, len(dataToSplit)):
        column = str(dataToSplit[i])
        splittedColumn = column.split(",")
        id = splittedColumn[0]
        humidity = splittedColumn[1]
        temperature = splittedColumn[2]
        lighting = splittedColumn[3]
        gpsx = splittedColumn[4]
        gpsy = splittedColumn[5]
        ts = splittedColumn[6]
        idlist.append(int(id))
        humlist.append(float(humidity))
        tmplist.append(float(temperature))
        luxlist.append(float(lighting))
        xlist.append(float(gpsx))
        ylist.append(float(gpsy))
        tslist.append(ts)

def getData():
  global myIotdata1,myIotdata2,IDlist1,HUMlist1,TMPlist1,LUXlist1,Xlist1,Ylist1,TSlist1,IDlist2,HUMlist2,TMPlist2,LUXlist2,Xlist2,Ylist2,TSlist2
  print("updating")
  #resetting the lists
  myIotdata1 = []
  IDlist1 = []
  HUMlist1 = []
  TMPlist1 = []
  LUXlist1 = []
  Xlist1 = []
  Ylist1 = []
  TSlist1 = []

  myIotdata2 = []
  IDlist2 = []
  HUMlist2 = []
  TMPlist2 = []
  LUXlist2 = []
  Xlist2 = []
  Ylist2 = []
  TSlist2 = []

  threading.Timer(10, getData).start() #schedules the function to run every 10 seconds to dynamically update the website
  myIotdata1 = iotdata.query.order_by(iotdata.ts).all()
  PushData(myIotdata1,IDlist1,HUMlist1,TMPlist1,LUXlist1,Xlist1,Ylist1,TSlist1)
  myIotdata2 = iotdata2.query.order_by(iotdata2.ts).all()
  PushData(myIotdata2, IDlist2, HUMlist2, TMPlist2, LUXlist2, Xlist2, Ylist2, TSlist2)
  db.session.remove()
  
getData()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@app.route("/Home.html")
@app.route('/')
def home():
    return render_template("Home.html")
@app.route('/Readings.html')
def Readings():
    return render_template("Readings.html", temp1 = TMPlist1, hum1 = HUMlist1, lum1 = LUXlist1, #First device datasets
                            temp2=TMPlist2, hum2=HUMlist2, lum2=LUXlist2,  #second device datasets
                            lTemp1 = TMPlist1[-1], lHum1 = HUMlist1[-1], lLight1 = LUXlist1[-1],Long1 = Xlist1[-1],Lat1 = Ylist1[-1],TS1 = TSlist1[-1], #first table row
                            lTemp2=TMPlist2[-1], lHum2=HUMlist2[-1], lLight2=LUXlist2[-1], Long2=Xlist2[-1],Lat2=Ylist2[-1], TS2=TSlist2[-1]) #second table row
@app.route('/Schematics.html')
def Schematics():
    return render_template("Schematics.html")

@app.route("/Map.html")
def Map():
    return render_template("Map.html", Long = [Xlist1[-1],Xlist2[-1]], Lat = [Ylist1[-1],Ylist2[-1]])

if __name__=="__main__":
    app.run(debug=True)

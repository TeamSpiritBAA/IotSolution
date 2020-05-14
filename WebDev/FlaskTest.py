from flask import Flask,request,render_template,redirect
from flask_sqlalchemy import SQLAlchemy
import psycopg2
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:igra1122@localhost/projectData'
db = SQLAlchemy(app)
#@app.route('/hello')
#@app.route('/hello/<name>')
#def hello(name=None):
 #   return render_template('/testplate.html',name=name)
#@app.route('/sign-up',methods=["GET","POST"])

class Iotdata(db.Model):
   id = db.Column('id', db.Integer, primary_key = True)
   humidity = db.Column(db.Numeric(20,2))
   temperature= db.Column(db.Numeric(20,2))
   lighting = db.Column(db.Numeric(20,1))
   gpsx = db.Column(db.Numeric(20,6))
   gpsy = db.Column(db.Numeric(20,6))
   ts = db.Column(db.TIMESTAMP)

   def __init__(self, id, humidity, temperature, lighting, gpsx, gpsy,ts):
      self.id = id
      self.humidity = humidity
      self.temperature = temperature
      self.lighting = lighting
      self.gpsx = gpsx
      self.gpsy = gpsy
      self.ts = ts

   def __repr__(self):
       return f"{self.id},{self.humidity},{self.temperature},{self.lighting},{self.gpsx},{self.gpsy},{self.ts}"

myIotdata = Iotdata.query.all()
IDlist= []
HUMlist = []
TMPlist = []
LUXlist = []
Xlist = []
Ylist = []
TSlist = []


for i in range(0, len(myIotdata)):
    column = str(myIotdata[i])
    splittedColumn = column.split(",")
    id = splittedColumn[0]
    humidity = splittedColumn[1]
    temperature = splittedColumn[2]
    lighting = splittedColumn[3]
    gpsx = splittedColumn[4]
    gpsy = splittedColumn[5]
    ts = splittedColumn[6]
    IDlist.append(int(id))
    HUMlist.append(float(humidity))
    TMPlist.append(float(temperature))
    LUXlist.append(float(lighting))
    Xlist.append(float(gpsx))
    Ylist.append(float(gpsy))
    TSlist.append(ts)

print(TMPlist)
@app.route("/Home.html")
@app.route('/')
def home():
    return render_template("Home.html")
@app.route('/Readings.html')
def Readings():
    return render_template("Readings.html", temp = TMPlist, hum = HUMlist, lum = LUXlist,ID = IDlist[9],Long = Xlist[9], Lat = Ylist[9],lHum = HUMlist[9],lTemp = TMPlist[9],lLight = LUXlist[9],TS = TSlist[9])
@app.route('/Map.html')
def Map():
    return render_template("Map.html")
@app.route('/Schematics.html')
def Schematics():
    return render_template("Schematics.html")
if __name__=="__main__":
    app.run(debug=True)
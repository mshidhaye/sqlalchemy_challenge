# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt



#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def Welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    Recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    twelve_months_before = dt.datetime.strptime(Recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    P_results = session.query(Measurement.date,func.avg(Measurement.prcp)).group_by(Measurement.date).filter(Measurement.date >= twelve_months_before).all()

    session.close()
                              
    Precepitation=[]
    for date,prcp in P_results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        Precepitation.append(precipitation_dict)
    return jsonify(Precepitation)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.id,Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    
    session.close()
    
    station_list=[]
    for id,station,name,latitude,longitude,elevation in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_dict['latitude']=latitude
        station_dict['longitude']=longitude
        station_dict['elevation']=elevation
        station_list.append(station_dict)
    return jsonify(station_list)
    

@app.route("/api/v1.0/tobs")
def tobs():
    station_count = session.query(Measurement.station, func.count(Measurement.tobs))\
             .group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc())
    active_station = station_count[0][0]
    Recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    twelve_months_before = dt.datetime.strptime(Recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    t_results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == active_station).\
                filter(Measurement.date >= twelve_months_before).all()
    
    session.close()
        
    temperatures = []
    for result in t_results:
        tobs_dict={}
        tobs_dict['date']=result.date
        tobs_dict['tobs']=result.tobs
        temperatures.append(tobs_dict)
  
    return jsonify(temperatures)
       
@app.route("/api/v1.0/<start>")
def temp_calc_sd(start):
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).all()
    print(results)
    session.close()
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)
    

@app.route("/api/v1.0/<start>/<end>")
def temp_calc_ed(start, end):
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, '%Y-%m-%d')
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >=start_dt).filter(Measurement.date <= end_dt).all()
    session.close()
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)

if __name__=="__main__":
    app.run()
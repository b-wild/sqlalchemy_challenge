# 1. Import Dependencies

from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from requests import session
from operator import and_
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///hawaii.sqlite")
conn = engine.connect()

Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# 2. Create an app
app = Flask(__name__)


# 3. Define static routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Vacation Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
# Convert the query results from your precipitation analysis
def precipitation():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year).\
    order_by(Measurement.date).all()

    session.close()

# Convert list of tuples into normal list
    precipitate = []
    for date, prcp in results:
        precipitate_dict = {}
        precipitate_dict[date] = prcp
        precipitate.append(precipitate_dict)

    return jsonify(precipitate)

@app.route("/api/v1.0/stations")
# Return a JSON list of stations from the dataset.
def stations():
    
    session = Session(engine)
# Perform a query to retrieve the data and precipitation scores
    results = session.query(Station.station).all()

    session.close()

# Convert list of tuples into normal list
    station_box = list(np.ravel(results))

    return jsonify(station_box)

@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most-active station for the previous year of data. Return a JSON list of temperature observations for the previous year.
def tobs():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= year).\
    order_by(Measurement.date).all()

    session.close()

# Convert list of tuples into normal list
    Observations = []
    for date, tobs in results:
        obs_dict = {}
        obs_dict[date] = tobs
        Observations.append(obs_dict)

    return jsonify(Observations)

@app.route("/api/v1.0/<start>")
# Return a JSON list of stations from the dataset.
def start(start):
    Summation = []

    results =   session.query(Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        sum_dict = {}
        sum_dict["Date"] = date
        sum_dict["TMIN"] = min
        sum_dict["TAVG"] = avg
        sum_dict["TMAX"] = max
        Summation.append(sum_dict)

    session.close()    

    return jsonify(Summation)

@app.route("/api/v1.0/<start>/<end>")
# Return a JSON list of stations from the dataset.
def end(start,end):
    session = Session(engine)

    Summary = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(and_(Measurement.date >= start, Measurement.date <= end)).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        sum_dict = {}
        sum_dict["Date"] = date
        sum_dict["TMIN"] = min
        sum_dict["TAVG"] = avg
        sum_dict["TMAX"] = max
        Summary.append(sum_dict)

    session.close()    

    return jsonify(Summary)



# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)

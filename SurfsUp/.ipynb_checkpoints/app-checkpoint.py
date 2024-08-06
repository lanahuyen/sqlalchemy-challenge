# Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np
import datetime as dt


#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables

Base.classes.keys()

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

# Define the most recent date
most_recent_date = "2017-08-23"

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Import datetime module inside the function
    import datetime as dt
    
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve the data and precipitation scores
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    # Close session
    session.close()
    
    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in precipitation_data:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve all stations
    results = session.query(Station.station).all()
    
    # Close session
    session.close()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Import datetime module inside the function
    import datetime as dt
    
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most active station
    most_active_station_id = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()[0]
    
    # Perform a query to retrieve the last 12 months of temperature observation data
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Close session
    session.close()
    
    # Convert list of tuples into a list of dictionaries
    all_tobs = []
    for date, tobs in temperature_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temperature"] = tobs
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve the min, avg, and max temperatures for all dates greater than and equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    # Close session
    session.close()
    
    # Convert list of tuples into normal list
    temps = list(np.ravel(results))
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve the min, avg, and max temperatures for dates between the start and end date inclusive
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Close session
    session.close()
    
    # Convert list of tuples into normal list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
#db config from app.py
import os
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.tododb
###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    # FIXME: These probably aren't the right open and close times
    # and brevets may be longer than 200km
    bv = request.args.get('bv', type=int)
    bst = request.args.get('bst', type=str)
        
    if (isinstance(km, float) and not(km < 0)):
        if (km < (bv*1.05)) :
            open_time = acp_times.open_time(km, bv, bst).isoformat()
            close_time = acp_times.close_time(km, bv, bst).isoformat()
            if (open_time != -1):
                result = {"open": open_time, "close": close_time}
            else:
                result = { "errmsg": "Distance over the limit" }
        else:
            result = { "errmsg": "Distance over the limit" }
    else:
        result = { "errmsg": "Input not in valid format" }


    return flask.jsonify(result=result)


#############
# @app.route('/clean')
# #this method for cleaning the previous records
# def clear():
#     db.tododb.delete_many({})
#############

# This function will insert the record into
@app.route('/submit', methods=['POST'])
def submit_func():
    #This are will ge the info from user input and store into the db
    miles_holder = request.form.getlist("miles")
    km_holder = request.form.getlist("km")
    location_holder = request.form.getlist("location")
    open_holder = request.form.getlist("open")
    close_holder = request.form.getlist("close")

    #traversal whole table
    for curr in range(len(open_holder)):
        if (open_holder[curr] != ""):
            datalist = { "miles": miles_holder[curr], "km": float(km_holder[curr]), "location": location_holder[curr],
                         "open": open_holder[curr], "close": close_holder[curr] }
            # insert_one() will insert single obejct into the db, defined dtype is dict.
            db.tododb.insert_one(datalist)
        else:
            # if there have nothing remain, error message will present
            db.tododb.insert_one({"Error, don't have any info" : 'Please try again'})
            
    return redirect(url_for('index'))

@app.route('/delete')
def delete_function():
    db.tododb.delete_many({})
    return render_template('delete_all.html')

@app.route('/display')
def display_func():
    items_total = db.tododb.find().sort("km")
    if (items_total.count() == 0):
        return render_template('lack_input.html')
    items = [item for item in items_total]
    return render_template('display.html', items=items)

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")

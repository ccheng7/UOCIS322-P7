# Streaming Service
from json import JSONEncoder

import flask
import json
from flask import request
from flask import Flask, redirect, url_for, request, render_template
from flask_restful import Resource, Api,reqparse
import acp_times
from pymongo import MongoClient
parser = reqparse.RequestParser()
parser.add_argument('top', type=list)

app = Flask(__name__)
api = Api(app)



client = MongoClient('mongodb://'+os.environ['MONGODB_HOSTNAME'], 27017)
db=client.tododb
app.sercet_key='Default secret'

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

    if (isinstance(km, float) and not (km < 0)):
        if (km < (bv * 1.05)):
            open_time = acp_times.open_time(km, bv, bst).isoformat()
            close_time = acp_times.close_time(km, bv, bst).isoformat()
            if (open_time != -1):
                result = {"open": open_time, "close": close_time}
            else:
                result = {"errmsg": "Distance over the limit"}
        else:
            result = {"errmsg": "Distance over the limit"}
    else:
        result = {"errmsg": "Input not in valid format"}

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
    # This are will ge the info from user input and store into the db
    miles_holder = request.form.getlist("miles")
    km_holder = request.form.getlist("km")
    location_holder = request.form.getlist("location")
    open_holder = request.form.getlist("open")
    close_holder = request.form.getlist("close")

    # traversal whole table
    for curr in range(len(open_holder)):
        if (open_holder[curr] != ""):
            datalist = {"miles": miles_holder[curr], "km": float(km_holder[curr]), "location": location_holder[curr],
                        "open": open_holder[curr], "close": close_holder[curr]}
            # insert_one() will insert single obejct into the db, defined dtype is dict.
            print(datalist)
            db.insert_one(datalist)
        else:
            # if there have nothing remain, error message will present
            db.insert_one({"Error, don't have any info": 'Please try again'})
            pass
    return redirect(url_for('index'))


@app.route('/delete')
def delete_function():
    # db.tododb.delete_many({})
    return render_template('delete_all.html')


@app.route('/display')
def display_func():
    pass
    items_total = db.find().sort("km")
    if (items_total.count() == 0):
        return render_template('lack_input.html')
    items = [item for item in items_total]
    print(items)
    return render_template('display.html', items=items)




def listAll_csv():
    pass
    items_total = db.find()

    items = []
    for item in items_total:
        data = []
        if item.get("open"):
            data.append(item["open"])
            data.append(item["close"])
            items.append(data)



    # print(items)
    return items

def listAll_json():
    pass
    items_total = db.find()

    items = []
    for item in items_total:
        data = []
        if item.get("open"):
            data.append(item["open"])
            data.append(item["close"])
            items.append(data)



    # print(items)
    return items

def list_open_csv(count):
    items_total = db.find().sort("open")

    items = []
    i = 0
    for item in items_total:
        data = []
        if item.get("open"):
            i += 1
            data.append(item["open"])
            print(item["open"])
            items.append(data)
        if i >= count:
            break

    return items


def list_open_json(count):
    items_total = db.find().sort("open")

    items = []
    i = 0
    for item in items_total:
        data = []

        if item.get("open"):
            data.append(item["open"])
            i += 1
            items.append(data)
        if i >= count:
            break
    # print(items)
    return items



def list_close_csv(count):
    items_total = db.find().sort("close")
    i = 0
    items = []
    for item in items_total:
        data = []
        if item.get("close"):
            data.append(item["close"])
            i += 1
            items.append(data)
        if i >= count:
            break
    # print(items)
    return items


def list_close_json(count):
    items_total = db.find().sort("close")

    items = []
    i = 0
    for item in items_total:
        data = []
        if item.get("close"):
            data.append(item["close"])
            i += 1
            items.append(data)
        if i >= count:
            break
    # print(items)
    return items


SERIES = {
    0: {
        'name': 'Breaking Bad',
        'from': 2008,
        'to': 2013,
        'ongoing': False,
        'creators': ['Vince Gilligan'],
        'cast': {
            'Bryan Cranston': ['Walter White'],
            'Aaron Paul': ['Jesse Pinkman'],
            'Anna Gunn': ['Skyler White'],
            'Bob Odenkirk': ['Saul Goodman'],
            'Jonathan Banks': ['Mike Ehrmantraut'],
            'Giancarlo Esposito': ['Gus Fring']
        },
        'imdb_rating': 9.5,
        'genre': ['crime', 'drama']
    },
    1: {
        'name': 'Better Call Saul',
        'from': 2015,
        'to': 2021,
        'ongoing': False,
        'creators': ['Vince Gilligan', 'Peter Gould'],
        'cast': {
            'Bob Odenkirk': [
                'Saul Goodman',
                'James McGill'
            ],
            'Jonathan Banks': ['Mike Ehrmantraut'],
            'Giancarlo Esposito': ['Gus Fring']
        },
        'imdb_rating': 8.7,
        'genre': ['crime', 'drama']
    },
    2: {
        'name': 'Curb Your Enthusiasm',
        'from': 2000,
        'to': None,
        'ongoing': True,
        'creators': ['Larry David'],
        'cast': {'Larry David': ['Larry David'],
                 'Jeff Garlin': ['Jeff Greene'],
                 'Cheryl Hines': ['Cheryl David'],
                 'Susie Essman': ['Susie Greene']
                 },
        'imdb_rating': 8.7,
        'genre': ['comedy']
    }
}

#  restful
#  csv
class TVShow(Resource):
    def __init__(self,item):
        self.item = item

    def get(self):
        return JSONEncoder().encode(self.item)

#  json
class TVShows(Resource):
    def __init__(self,item):
        self.item = item

    def get(self):
        return {"time":self.item}

class Open_time_csv(Resource):



    def get(self):
        args = parser.parse_args()
        print(args)
        top = args["top"]

        item = list_open_csv(int(top[0]))
        print(item)
        return JSONEncoder().encode(item)

class Open_time_json(Resource):


    def get(self):
        args = parser.parse_args()
        print(args)
        top = args["top"]
        item = list_open_csv(int(top[0]))
        return json.dumps({"open_time":item})

class Close_time_csv(Resource):
    def get(self):
        args = parser.parse_args()
        print(args)
        top = args["top"]

        item = list_open_csv(int(top[0]))

        return JSONEncoder().encode(item)


class Close_time_json(Resource):

    def get(self):
        args = parser.parse_args()
        print(args)
        top = args["top"]
        item = list_open_csv(int(top[0]))
        return {"open_time": item}



# Create routes
# Another way, without decorators
api.add_resource(TVShow, '/listAll/',resource_class_kwargs={'item': listAll_csv()})
api.add_resource(TVShows, '/listAll/json/',resource_class_kwargs={'item': listAll_json()})
api.add_resource(Open_time_csv, '/listOpenOnly/csv/')
api.add_resource(Open_time_json, '/listOpenOnly/json/')
api.add_resource(Close_time_csv, '/listCloseOnly/csv/')
api.add_resource(Close_time_json, '/listCloseOnly/json/')

# Run the application
if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)

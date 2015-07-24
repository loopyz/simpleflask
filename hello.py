import os
import csv
import sys
import json
import itertools
from flask import Flask, jsonify, request

app = Flask(__name__)

housesCSV = csv.reader(open('listings.csv'), dialect='excel')
houses = []

for row in itertools.islice(housesCSV, 1, None):
    houses.append({
        "id": row[0],
        "price": int(row[3]),
        "bed": int(row[4]),
        "bath": int(row[5]),
        "street": row[1],
        "sqft": int(row[6]),
        "coordinates": [float(row[8]), float(row[7])]
    })

@app.route("/listings", methods=['GET'])

def get_houses():
    min_filters = {}
    max_filters = {}

    for filter_name in ['price', 'bed', 'bath']:
        min_filters[filter_name] = request.args.get('min_%s' % filter_name)
        max_filters[filter_name] = request.args.get('max_%s' % filter_name)

    filteredHouses = list(filterHousesByFilters(houses, min_filters, max_filters))
    return toGeoJson(filteredHouses)


def matchesFilters(matchType, filters, house):
    for key, val in filters.iteritems():
        # if argument is actually found, checks if breaks conditions
        # also checks to see if GET parameter is a valid key
        if key in house and val is not None:
            if matchType == 'min':
                if int(house[key]) < int(val):
                    return False
            else:
                if int(house[key]) > int(val): 
                    return False
    return True

def filterHousesByFilters(houses, min_filters, max_filters):
    filteredList = []
    for house in houses:
        if (matchesFilters('min', min_filters, house) and
            matchesFilters('max', max_filters, house)):
            filteredList.append(house)
    return filteredList

def toGeoJson(houseList):
    template = \
    ''' \
    {   "type" : "Feature",
        "geometry" : {
            "type" : "Point",
            "coordinates" : %s},
        "properties" : { "id" : "%s", "price" : "%s", "street" : "%s", "bedrooms" : "%i", "bathrooms" : "%i", "sq_ft" : "%i"}
    }
    '''

    output = \
        ''' \
    { "type" : "FeatureCollection",
        "features" : [
        '''

    for house in houseList:
        output += template % (house["coordinates"], house["id"], house["price"], house["street"], house["bed"], house["bath"], house["sqft"])
        output += ','
        
    # remove last comma
    output = output[:-2]

    # ending of output
    output += \
        ''' \
        ]
    }
        '''

    return output

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

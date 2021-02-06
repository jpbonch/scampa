from flask import Flask, render_template
import urllib.request
from datetime import date, timedelta
from scipy.interpolate import make_interp_spline
import numpy as np


app = Flask(__name__)


def get_graph_data(graphdate, smoothness):
    deleted = []
    for i in range(len(info["id"])):
        try:
            url = "https://archive.sensor.community/" + graphdate + \
                "/" + graphdate + "_pms5003_sensor_" + info['id'][i] + ".csv"
            urllib.request.urlretrieve(url, info["shortname"][i] + ".csv")
        except urllib.error.HTTPError:
            print("Error downloading " + info["shortname"][i])
            deleted.append(info["longname"][i])

    deleted_indeces = [info["longname"].index(name) for name in deleted]

    for index in deleted_indeces:
        for k in info.keys():
            info[k][index] = ''

    for k in info.keys():
        info[k] = list(filter(lambda a: a != '', info[k]))

    print(info)




    graphdata = {"p1": [], "p2": []}

    if smoothness == "smooth":
        x_new = list(range(0, 24))
    else:
        x_new = np.linspace(0, 24, 582)

    for i in range(len(info["id"])):
        with open(info["shortname"][i] + ".csv", 'r+') as f:
            data = f.read()
            data = data.split('\n')
        for x in range(len(data)):
            data[x] = data[x].split(';')
        data.pop(0)
        data.pop(len(data) - 1)

        # Both P1 and P2
        for num in (6, 7):
            ys = []
            for row in data:
                ys.append(int(row[num]))

            if num == 6:
                graphdata["p1"].append(ys)
            else:
                graphdata["p2"].append(ys)

    return graphdata, x_new, deleted


@ app.route("/", methods=['GET', 'POST'])
def index():
    today = date.today() - timedelta(days=2)
    return "<script>window.location = '/" + str(today) + "/smooth';</script>" + '\n' + \
           """<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }};">"""


@ app.route("/<graphdate>/<smoothness>", methods=['GET', 'POST'])
def main(graphdate=None, smoothness='smooth'):

    global info
    info = {
        "longname": ["Abingdon School", "St. Blaise", "Radley College",
                     "Abingdon Prep", "Thomas Reade", "Sensor 48673"],
        "shortname": ['abingdon', 'stblaise', 'radley', 'abingdonprep',
                      'thomasreade', 'otherone'],
        "id": ['48281', '50299', '51969', '52053', '52049', '48673'],
        "colors": ['#e74697', '#0091ff', '#650000', '#a4d2c7', '#C0C0C0',
                   '#000000']
    }

    today = date.today() - timedelta(days=2)
    start = today - timedelta(days=100)
    date_list = []
    for y in range(today.toordinal(), start.toordinal() - 1, -1):
        date_list.append(date.fromordinal(y))
    if graphdate is None:
        graphdate = str(today)

    graphdata, x_new, deleted = get_graph_data(graphdate, smoothness)

    return render_template('index.html', graphdata=graphdata, date_list=date_list,
                           longname=info["longname"], x_new=x_new,
                           colors=info["colors"], deleted=deleted)


if __name__ == "__main__":
    app.run()

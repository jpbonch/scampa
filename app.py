from flask import Flask, render_template
import urllib.request
from datetime import date, timedelta
from scipy.interpolate import make_interp_spline
import numpy as np


app = Flask(__name__)
# ------------- add new sensor, pms5003 ####################
longname = ["Abingdon School", "St. Blaise",
            "Radley College", "Abingdon Prep", "Thomas Reade", "Sensor 48673"]
shortname = ['abingdon', 'stblaise', 'radley', 'abingdonprep',
             'thomasreade', 'otherone']  # also filename
id = ['48281', '50299', '51969', '52053', '52049', '48673']
colors = ['#e74697', '#0091ff', '#800000', '#a4d2c7', '#C0C0C0', '000000']
do_plot = [True, True, True, True, True, True]
###################################


def get_graph_data(graphdate, SMOOTHNESS):
    for i in range(len(id)):
        try:
            url = "https://archive.sensor.community/" + graphdate + \
                "/" + graphdate + "_pms5003_sensor_" + id[i] + ".csv"
            urllib.request.urlretrieve(url, shortname[i] + ".csv")
        except urllib.error.HTTPError:
            colors[i] = '#FFFFFF'
            do_plot[i] = False

    graphdata = {"p1": [], "p2": []}
    x_new = np.linspace(0, 24, SMOOTHNESS)
    for i in range(len(id)):
        if do_plot[i]:
            with open(shortname[i] + ".csv", 'r+') as f:
                data = f.read()
                data = data.split('\n')
            for x in range(len(data)):
                data[x] = data[x].split(';')
            data.pop(0)
            data.pop(len(data) - 1)

            # Both P1 and P2
            for num in (6, 7):
                xs = []
                ys = []
                for row in data:
                    xs.append(row[5])
                    ys.append(int(row[num]))

                xs = [x[11:] for x in xs]
                for x in xs:
                    splitted = x.split(':')
                    xs[xs.index(x)] = float(splitted[0]) + \
                        float(splitted[1]) / 60 + float(splitted[2]) / 3600

                a_BSpline = make_interp_spline(xs, ys)

                y_new = a_BSpline(x_new)

                y_new = [abs(ele) for ele in y_new]
                if num == 6:
                    graphdata["p1"].append(y_new)
                else:
                    graphdata["p2"].append(y_new)
            # handle no data TODO
            #fix 2020-01-14

    return graphdata, x_new


@app.route("/", methods=['GET', 'POST'])
@app.route("/<graphdate>", methods=['GET', 'POST'])
def main(graphdate=None):
    today = date.today() - timedelta(days=2)
    start = today - timedelta(days=100)
    date_list = []
    for y in range(today.toordinal(), start.toordinal() - 1, -1):
        date_list.append(date.fromordinal(y))
    if graphdate is None:
        graphdate = str(today)

    graphdata, x_new = get_graph_data(graphdate, 300)

    return render_template('index.html', graphdata=graphdata, date_list=date_list, longname=longname, x_new=x_new, colors=colors)


if __name__ == "__main__":
    app.run()

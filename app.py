from flask import Flask, render_template, redirect
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpld3 import fig_to_html
import urllib.request
from datetime import date, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    today = date.today() - timedelta(days=2)
    todaydate = today.strftime("%Y-%m-%d")
    strngy = "<script>window.location = '/'+screen.width+'/"+todaydate+"';"+"</script>"
    print(strngy)
    return "<script>window.location = '/'+screen.width+'/"+todaydate+"';"+"</script>"

@app.route("/<width>/<graphdate>", methods=['GET', 'POST'])
def main(width, graphdate):
    today = date.today() - timedelta(days=2)
    start = today - timedelta(days=50)
    todaydate = today.strftime("%Y-%m-%d")
    date_list = []
    for y in range(today.toordinal(), start.toordinal()-1, -1):
        date_list.append(date.fromordinal(y))

    ############### add new sensor, pms5003 ####################
    longname = ["Abingdon School", "St. Blaise", "Radley College", "Abingdon Prep", ""]
    shortname  = ['abingdon', 'stblaise', 'radley', 'abingdonprep','otherone'] #also filename
    id = ['48281', '50299', '51969', '52053_indoor', '48673']
    colors = ['#e74697', '#0091ff', '#800000', '#a4d2c7', '000000']
    ###################################

    notfoundtext = ['' for i in range(len(id))]
    for i in range(len(id)):
        try:
            url = "https://archive.sensor.community/"+graphdate+"/"+graphdate+"_pms5003_sensor_"+id[i]+".csv"
            urllib.request.urlretrieve(url, shortname[i]+".csv")
        except urllib.error.HTTPError:
            notfoundtext[i] = 'NO DATA'
            colors[i] = '#FFFFFF'

    plots = [[] for i in range(len(id))]
    latest = [[] for i in range(len(id))]
    for i in range(len(id)):
        with open(shortname[i]+".csv", 'r+') as f:
            data = f.read()
            data = data.split('\n')
        for x in range(len(data)):
            data[x] = data[x].split(';')
        data.pop(0)
        data.pop(len(data)-1)

        for num in (6,7):
            xs = []
            ys = []
            for row in data:
                xs.append(row[5])
                ys.append(int(row[num]))

            xs = [x[11:] for x in xs]
            for x in xs:
                splitted = x.split(':')
                xs[xs.index(x)] = float(splitted[0]) + float(splitted[1])/60 + float(splitted[2])/3600

            fig = Figure(figsize=(int(width)*(0.00484375/1.42), int(width)*0.5625*0.00625/1.3))
            axis = fig.add_subplot(1, 1, 1)
            axis.set_xlabel('Time')
            axis.set_ylabel('µg/m³')
            axis.text(((max(xs)-min(xs))/2)+min(xs), max(ys)/2, notfoundtext[i], size=18, ha='center', va='center', color='#A0A0A0')
            toprighttext = 'PM10' if num == 6 else 'PM2.5'
            if notfoundtext[i] == '':
                axis.text(((max(xs)-min(xs))/1.1)+min(xs), max(ys)/1.05, toprighttext, size=30, ha='center', va='center', color='#A0A0A0' )


            axis.plot(xs, ys, c=colors[i])
            plots[i].append(fig_to_html(fig))

    return render_template('index.html', plots=plots, latest=latest, date_list=date_list, id=id, longname=longname)


if __name__ == "__main__":
    app.run()

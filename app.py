from flask import Flask, render_template, redirect
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpld3 import fig_to_html
import urllib.request
from datetime import date, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return """
<script>
   window.location = '/'+screen.width;
</script>"""

@app.route("/<width>", methods=['GET', 'POST'])
def main(width):
    today = date.today() - timedelta(days=2)
    todaydate = today.strftime("%Y-%m-%d")

    abingdon = "https://archive.sensor.community/"+todaydate+"/"+todaydate+"_pms5003_sensor_48281.csv"
    stblaise = "https://archive.sensor.community/"+todaydate+"/"+todaydate+"_pms5003_sensor_50299.csv"
    otherone = "https://archive.sensor.community/"+todaydate+"/"+todaydate+"_pms5003_sensor_48673.csv"
    urllib.request.urlretrieve(abingdon, "abingdon.csv")
    urllib.request.urlretrieve(stblaise, "stblaise.csv")
    urllib.request.urlretrieve(otherone, "otherone.csv")

    longname = ["Abingdon School", "St. Blaise", ""]
    shortname  = ['abingdon', 'stblaise', 'otherone']
    id = ['48281', '50299', '48673']
    plots = []
    colors = ['#e74697', '#add8e6', '#debe5d']

    for i in range(3):
        with open(shortname[i]+".csv", 'r+') as f:
            data = f.read()
            data = data.split('\n')
        for x in range(len(data)):
            data[x] = data[x].split(';')
        data.pop(0)
        data.pop(len(data)-1)

        xs = []
        ys = []
        for row in data:
            xs.append(row[5])
            ys.append(int(row[6]))

        xs = [x[11:] for x in xs]
        for x in xs:
            splitted = x.split(':')
            xs[xs.index(x)] = float(splitted[0]) + float(splitted[1])/60 + float(splitted[2])/3600

        fig = Figure(figsize=(int(width)*(0.00484375), int(width)*0.5625*0.00625))
        axis = fig.add_subplot(1, 1, 1)
        axis.set_xlabel('Time')
        axis.set_ylabel('P1')
        axis.set_title('Sensor ' +id[i]+': '+ longname[i] + ' Date: ' + todaydate)


        axis.plot(xs, ys, c=colors[i])
        plots.append(fig_to_html(fig))

    return render_template('index.html', plots=plots)


if __name__ == "__main__":
    app.run()

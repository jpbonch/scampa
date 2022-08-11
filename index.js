const express = require('express');
const path = require('path');
const fetch = require('node-fetch')

const app = express();
app.use(express.static(path.join(__dirname, 'public')));


app.get('/', function (req, res) {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/:date', async function (req, res) {

    var info = [
        {"name":"Abingdon School", "id":"48281", "color":"#e74697", "p1":{}, "p2":{}},
        {"name":"St. Blaise", "id":"50299", "color":"#0091ff", "p1":{}, "p2":{}},
        {"name":"Radley College", "id":"51969", "color":"#650000", "p1":{}, "p2":{}},
        {"name":"Abingdon Prep", "id":"52053", "color":"#a4d2c7", "p1":{}, "p2":{}},
        {"name":"Thomas Reade", "id":"52049", "color":"#C0C0C0", "p1":{}, "p2":{}},
        {"name":"Sensor 48673", "id":"48673", "color":"#000000", "p1":{}, "p2":{}},
        {"name":"John Mason", "id":"59506", "color":"#fc6a03", "p1":{}, "p2":{}}
    ]
    

    for (let i=0; i<info.length; i++){
        var url = "https://archive.sensor.community/" + req.params.date + "/" + req.params.date + "_pms5003_sensor_" + info[i]["id"] + ".csv";
        var response = await fetch(url);
        info[i]["status"] = response.status;
        if (response.status != 200){
            break;
        }
        var body = await response.text();
        
        var p1 = [];
        var p2 = [];
    
        var listed = body.split('\n');
        listed.shift();
        for (let j=0; j<listed.length; j++){
            var splitted = listed[j].split(';');
            p1.push(parseInt(splitted[6]));
            p2.push(parseInt(splitted[7]));
        }

       info[i]["p1"] = p1;
       info[i]["p2"] = p2;
    }

    var graph = generateGraph(info, "p1");
    var graph2 = generateGraph(info, "p2");
    res.send({p1:graph, p2:graph2});
});

function generateGraph(info, type){
    var datasets = [];
    for (place of info){
        if (place.status == 200){
        datasets.push({
            label: place.name,
            fill: false,
            borderColor: place.color,
            data: place[type]
        });
         } else {
        datasets.push({
            borderColor: "#FFFFFF",
          label: place.name + " (no data)",
          hidden: true
        });
         }
    }

    var hours = [];
    for(var i=0; i < 24; i++) {
        hours.push((i < 10 ? "0" : "") + i + ":00");
    }


    var graph = {
        // The type of chart we want to create
        type: 'line',
        lineTension: 0.8,
        // The data for our dataset
        data: {
          labels: hours,
          datasets: datasets
        },

        // Configuration options go here
        options: {
          responsive: true,
          tooltips: {
            mode: 'index',
            position: 'nearest',
            intersect: false,
          },
          scales: {
          yAxes: [{
              display: true,
              ticks: {
                  suggestedMin: 0,
                  suggestedMax: 25
              },
              scaleLabel: {
              display: true,
              labelString: 'µg/m³'
        }
          }]
        }
          }
      }

      return graph;
}

module.exports = app;
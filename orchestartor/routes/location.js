var express = require('express');
var router = express.Router();
var firebase = require("firebase");
var radar = require('radar-sdk-js');
var inside = require('point-in-polygon');
const axios = require('axios')
var inside = require('point-in-geopolygon');

/* GET users listing. */
const data = {
  'Vipul':7,
  'Vignesh': 3,
  'Rosna': 8,
  'Parth': 1
};
router.get('/', function(req, res, next) {
  var starCountRef = firebase.database().ref('faces_detected/');
  starCountRef.on('child_added', function(snapshot) {
    var obj = snapshot.val();
    var key;
    for (var k in obj) {
      key = k;
      break;
    }
    var curr_val = obj[key];

    if(data[curr_val.id] > 5) {
      console.log(curr_val);
      firebase.database().ref('alert/').set({
        bool: 1,
      });
      console.log('Alerted the human !!');
      console.log("--------------------------------------");
      var curr_loc = curr_val.location;
      axios.get("https://api.radar.io/v1/geofences", { headers: { Authorization: "prj_live_sk_6cf8ab46c57c254a8d4475436968a0a909fba953" } }).then(response => {
             // console.log(curr_loc, response.data.geofences[0].geometry.coordinates);
             var nearest = '';
             var nearest_metadata = '';
             for (var i = 0; i < response.data.geofences.length; i++) {
               var polygon = response.data.geofences[i].geometry.coordinates;
               var found = inside.polygon(polygon,[-118.286119,34.020091]);
               if(found) {
                 nearest = response.data.geofences[i].description;
                 nearest_metadata = response.data.geofences[i].metadata;
                 break;
               }

             }

             console.log("Alerting nearest Police station", nearest, nearest_metadata);
             console.log("--------------------------------------");
             //Stream to this police station
           }).catch((error) => {
             console.log('error 3 ' + error);
           });

    }
  });
  res.send('Police station');

});

module.exports = router;

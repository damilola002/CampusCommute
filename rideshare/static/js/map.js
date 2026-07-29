// -----------------------------
// Create Map
// -----------------------------


let map = L.map("map")
.setView(
    [32.7298,-97.1163],
    13
);



// Load OpenStreetMap tiles

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {

        attribution:
        "© OpenStreetMap contributors"

    }

).addTo(map);




// -----------------------------
// Pickup Location
// -----------------------------


let pickup = [
    32.7340,
    -97.1128
];


let pickupMarker =
L.marker(pickup)
.addTo(map)
.bindPopup("Pickup Location");




// -----------------------------
// Dropoff Location
// -----------------------------


let dropoff = [
    32.7279,
    -97.1105       //Parking lot by kalpana chawala hall
];


let dropoffMarker =
L.marker(dropoff)
.addTo(map)
.bindPopup("Dropoff Location");





// -----------------------------
// Draw Route Line
// -----------------------------


let route =
L.polyline(

[
    pickup,
    dropoff
],

{

    color:"red"

}

)

.addTo(map);





// -----------------------------
// Driver Marker
// -----------------------------


let driverMarker =
L.marker(
    [32.7298,-97.1163]
)

.addTo(map)

.bindPopup(
"Driver"
);





// -----------------------------
// User Location
// -----------------------------


navigator.geolocation.getCurrentPosition(

function(position){


    let userLat =
    position.coords.latitude;


    let userLng =
    position.coords.longitude;



    let userMarker =
    L.marker(
        [
            userLat,
            userLng
        ]
    )

    .addTo(map)

    .bindPopup(
        "You are here"
    );



    map.setView(
        [
            userLat,
            userLng
        ],
        14
    );


},

function(){

    alert(
    "Location permission denied"
    );

}

);





// -----------------------------
// Update Driver Position
// -----------------------------


function updateDriver(){


fetch("/driver_location")


.then(response =>
response.json()
)


.then(data => {


    driverMarker.setLatLng(

        [
            data.lat,
            data.lng
        ]

    );


});


}



// Update every 2 seconds

setInterval(
    updateDriver,
    2000
);

const lieux = [
  { nom: "Amphi 502", status: "Ouvert", tempsRestant: "2h" },
  { nom: "Bibliothèque centrale", status: "Fermé", tempsRestant: "3h" },
  // Ajoutez ici vos autres lieux
  { nom: "Faculté des Lettres", status: "Ouvert", tempsRestant: "1h" },
  { nom: "Restaurant universitaire", status: "Fermé", tempsRestant: "4h" },
  { nom: "Salle de sport", status: "Ouvert", tempsRestant: "30min" },
  { nom: "Laboratoire d'informatique", status: "Fermé", tempsRestant: "2h30" },
  { nom: "Jardin botanique", status: "Ouvert", tempsRestant: "Indéfini" }
];

lieux.forEach(lieu => {
  var item = document.createElement('li');
  item.classList.add('nav-item');
  item.classList.add('dropdown');
item.style.marginTop="4px";
  item.innerHTML = `
  <div class="container-fluid element text-light">
    <div class="location-name fw-bold" style="float: left; ">${lieu.nom}</div>
    <span class="badge bg-${lieu.status === 'Ouvert' ? 'success' : 'danger'}">${lieu.status}</span><br>
    <span class="time-remaining">${lieu.status === 'Ouvert' ? 'Fermeture dans:' : 'Ouverture dans:'} ${lieu.tempsRestant}</span>
    </div>
  `;

  document.getElementsByClassName("navbar-nav")[0].appendChild(item);
});


var sidebar=document.getElementById("profile");
var lateral= document.getElementById("sidebar");

var fonc1=document.getElementById("fonction1");
var fonc2=document.getElementById("fonction2");
var search = document.getElementById("search");

search.addEventListener("click",function(){

    if(fonc1.style.display=="none"){ 
        fonc1.style.display="";
        fonc2.style.display="";
        lateral.style.display="none";
    }
    else{
        fonc1.style.display="none";
        fonc2.style.display="none";
        lateral.style.display="none";

    }
});






sidebar.addEventListener("click",function(){
    if(lateral.style.display=="none"){
        lateral.style.display="";
    }
    else{
        lateral.style.display="none";
    }
});





// Campus boundaries (to be updated with actual coordinates from map.osm)
const campusBounds = [
  [3.8700, 11.5000],  // Southwest corner
  [3.8800, 11.5200]   // Northeast corner
];

// Initialize map
let map = L.map('map').setView([3.8750, 11.5100], 16);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Restrict map view to campus bounds
map.setMaxBounds(campusBounds);
map.options.minZoom = 16;
map.options.maxZoom = 19;

// Current user location
let userLocation = null;

// Fonction 1: Get User Location
document.getElementById('fonction1').addEventListener('click', function() {
  if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(function(position) {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;

          // Check if location is within campus bounds
          if (isWithinCampus(lat, lon)) {
              userLocation = L.marker([lat, lon]).addTo(map);
              map.setView([lat, lon], 18);
          } else {
              showErrorModal();
          }
      }, function(error) {
          console.error("Error getting location:", error);
      });
  }
});

// Fonction 2: Route Calculation
document.getElementById('fonction2').addEventListener('click', function() {
  if (userLocation) {
      const destination = prompt("Entrez la destination (ex: Amphi 502)");
      // This would be enhanced with actual campus location database
      const destinationCoords = getDestinationCoordinates(destination);
      
      if (destinationCoords) {
          L.Routing.control({
              waypoints: [
                  L.latLng(userLocation.getLatLng()),
                  L.latLng(destinationCoords)
              ],
              routeWhileDragging: false,
              show: true,
              addWaypoints: false,
              fitSelectedRoutes: true,
              lineOptions: {
                  styles: [{color: 'blue', opacity: 0.7, weight: 5}]
              }
          }).addTo(map);
      } else {
          alert("Destination non trouvée");
      }
  } else {
      alert("Localisez-vous d'abord");
  }
});

// Utility Functions
function isWithinCampus(lat, lon) {
  return (lat >= campusBounds[0][0] && lat <= campusBounds[1][0] &&
          lon >= campusBounds[0][1] && lon <= campusBounds[1][1]);
}

function showErrorModal() {
  const modal = document.getElementById('error-modal');
  modal.style.display = 'block';
  setTimeout(() => { modal.style.display = 'none'; }, 3000);
}

function getDestinationCoordinates(destination) {
  // Placeholder: replace with actual campus location database
  const destinations = {
      "Amphi 502": [3.8755, 11.5110],
      "Bibliothèque centrale": [3.8760, 11.5105]
  };
  return destinations[destination];
}




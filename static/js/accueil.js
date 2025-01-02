// Définir les coordonnées des coins Nord, Sud, Est et Ouest
var bounds = [
    [3.84747, 11.48706], // Sud-Ouest (Sud, Ouest)
    [3.86849, 11.51457]  // Nord-Est (Nord, Est)
];

// Initialisation de la carte Leaflet
const map = L.map('map', {
    zoom: 16,              // Zoom initial
    minZoom: 16            // Zoom minimum pour empêcher de dézoomer plus que l'état initial
});

// Ajouter une couche de tuiles OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Ajuster la vue de la carte pour couvrir les coordonnées définies
map.fitBounds(bounds);
// Empêcher le déplacement en dehors des limites
map.setMaxBounds(bounds);


// Variables globales
let userMarker = null;
let routeLayer = null;

// Fonction 1 : Localisation de l'utilisateur
function trouverPositionUtilisateur() {
    if (!navigator.geolocation) {
        afficherMessage("La géolocalisation n'est pas prise en charge par votre navigateur." , "red");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const { latitude, longitude } = position.coords;
    
            // Envoyer la position au serveur pour validation
            fetch('/api/position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ latitude, longitude })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Ajouter ou mettre à jour le marqueur de l'utilisateur
                        if (userMarker) {
                            userMarker.setLatLng([latitude, longitude]);
                        } else {
                            userMarker = L.marker([latitude, longitude], { draggable: false, color: 'blue' }).addTo(map);
                            map.setView([latitude, longitude], 19);
                        }
                    } else {
                        afficherMessage("Vous n'êtes pas dans la zone du campus", "red");
                    }
                })
                .catch(err => console.error("Erreur lors de l'envoi de la position :", err));
        },
        (error) => {
            afficherMessage("Impossible d'obtenir votre position : " + error.message, "red");
        },
        { enableHighAccuracy: true }
    );
    
}
var marker=[];
// Fonction 2 : Recherche et itinéraire
function rechercherLieu(nom) {
    
    fetch('/api/recherche', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nom })
    })
        .then(response => response.json())
        .then(data => {
            const resultatsDiv = document.getElementById('resultats');
            const resultatsContainer = document.getElementById('resultats-container');

            // Vider les résultats précédents
            resultatsDiv.innerHTML = '';

            if (data.status === 'success') {
                const lieux = data.data;

                // Ajouter les résultats à la div #resultats
                lieux.forEach(lieu => {
                    const resultCard = document.createElement('div');
                    resultCard.classList.add('result-card');

                    resultCard.innerHTML = `
                        <h3>${lieu.nom}</h3>
                        <p>${lieu.description}</p>
                        <img src="${lieu.images[0]}" alt="Image" />
                    `;

                    resultCard.addEventListener('click', function() {
                        //enlever les anciens marqueurs
                        removeAllMarkers();
                        // Vous pouvez ajouter une logique pour marquer l'élément comme sélectionné
                    
                        // Créer un marqueur standard Leaflet avec une icône personnalisée pour le lieu sélectionné
                        var lieuMarker = L.marker([lieu.latitude, lieu.longitude], {
                            draggable: false, // Marqueur non déplaçable
                            icon: L.icon({
                                iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png', // Icône de marqueur par défaut
                                iconSize: [25, 41], // Taille de l'icône du marqueur
                                iconAnchor: [12, 41], // Point d'ancrage de l'icône
                                popupAnchor: [1, -34], // Point d'ancrage du popup
                                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png', // Ombre du marqueur
                                shadowSize: [41, 41] // Taille de l'ombre
                            })
                        }).addTo(map);
                        // Ajouter le marqueur au tableau des marqueurs
                        marker.push(lieuMarker);
                    
                        // Centrer la carte sur le lieu et zoomer à 19
                        map.setView([lieu.latitude, lieu.longitude], 19);
                    
                        // Ajouter une popup au marqueur avec des informations sur le lieu
                        lieuMarker.bindPopup(`<b>${lieu.nom}</b><br>${lieu.description}<br><img src="${lieu.images[0]}" alt="Image" style="width:100px; height:50px;">`)
                            .openPopup();
                    
                        // Masquer la div des résultats après la sélection
                        resultatsContainer.style.display = 'none';
                    });
                    
                    

                    // Ajouter chaque carte à la div des résultats
                    resultatsDiv.appendChild(resultCard);
                });

                // Afficher la div contenant les résultats avec un flou d'arrière-plan
                resultatsContainer.style.display = 'flex';
            } else {
                // Afficher un message d'aucun résultat
                const noResultsMessage = document.createElement('div');
                noResultsMessage.classList.add('no-results-message');
                noResultsMessage.textContent = 'Aucun résultat trouvé';
                resultatsDiv.appendChild(noResultsMessage);

                // Afficher la div contenant les résultats avec un flou d'arrière-plan
                resultatsContainer.style.display = 'flex';

                // Masquer le message après un court délai
                setTimeout(() => {
                    resultatsContainer.style.display = 'none';
                }, 2000);
            }
        })
        .catch(err => console.error("Erreur lors de la recherche du lieu :", err));
}

// Gestionnaire pour la barre de recherche
document.getElementsByClassName('searchbutton')[0].addEventListener('click', () => {
    const searchInput = document.getElementsByClassName('searchbar')[0].value;
    if (searchInput.trim()) {
        rechercherLieu(searchInput);
    } else {
        afficherMessage("Veuillez entrer un nom de lieu à rechercher.");
    }
});

// Fermer la div des résultats lorsque l'utilisateur clique ailleurs
document.addEventListener('click', function(event) {
    const resultatsContainer = document.getElementById('resultats-container');
    var resultatsDiv=document.getElementById("resultats");
    // Vérifier si le clic a eu lieu en dehors de la div #resultats-container
    if (!resultatsDiv.contains(event.target)) {
        resultatsContainer.style.display = 'none';
    }
});

// Activer la localisation de l'utilisateur
document.getElementById('fonction1').addEventListener('click', function(){
    trouverPositionUtilisateur();
    console.log("ok bonne position :)");
});
//fonction pour suggerer les amphis
function chargerAmphis() {
    fetch('/api/amphis')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                const amphis = data.data;
                const navbar = document.querySelector('.navbar-nav');
  
                amphis.forEach(amphi => {
                    const amphiContainer = document.createElement('div');
                    amphiContainer.classList.add('amphi-container');
                    amphiContainer.style.margin = '10px';
                    amphiContainer.style.padding = '10px';
                    amphiContainer.style.border = '1px solid #ccc';
                    amphiContainer.style.borderRadius = '5px';
                    amphiContainer.style.backgroundColor = '#f9f9f9';
                    amphiContainer.style.cursor ="pointer" ;
  
                    amphiContainer.innerHTML = `
                        <strong>${amphi.nom}</strong><br>
                        <span>${amphi.description}</span>
                        <br><img src="${amphi.images[0]}" alt="Image" style="width:100px; height:50px;">
                    `;
                     
                   

                    // Ajouter un gestionnaire de clic pour centrer sur l'amphi
                    amphiContainer.addEventListener('click', () => {
                         // Simuler un clic sur un élément de classe "navbar-nav"
                    const navbarNav = document.getElementById('search');
                    if (navbarNav) {
                        navbarNav.click();
                    }
                        // Supprimer les anciens marqueurs
                        removeAllMarkers();
  
                        // Ajouter un marqueur pour l'amphi sélectionné
                        const amphiMarker = L.marker([amphi.latitude, amphi.longitude], {
                            draggable: false,
                            icon: L.icon({
                                iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
                                iconSize: [25, 41],
                                iconAnchor: [12, 41],
                                popupAnchor: [1, -34],
                                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                                shadowSize: [41, 41]
                            })
                        }).addTo(map);
  
                        // Ajouter le marqueur au tableau des marqueurs
                        marker.push(amphiMarker);
  
                        // Centrer la carte sur l'amphi sélectionné
                        map.setView([amphi.latitude, amphi.longitude], 19);
  
                        // Ajouter une popup au marqueur avec les informations sur l'amphi
                        amphiMarker.bindPopup(`<b>${amphi.nom}</b><br>${amphi.description}<br><img src="${amphi.images[0]}" alt="Image" style="width:100px; height:50px;">`).openPopup();
                    });
  
                    navbar.appendChild(amphiContainer);
                });
            } else {
                console.error("Erreur lors du chargement des amphithéâtres :", data.message);
            }
        })
        .catch(err => console.error("Erreur lors de la requête des amphithéâtres :", err));
  }
  

// Charger les amphithéâtres au démarrage
document.addEventListener('DOMContentLoaded', chargerAmphis);

document.addEventListener('DOMContentLoaded', function() {
    const profile = document.getElementById('profile');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const overlay = document.getElementById('overlay');

    // Fonction pour réinitialiser le menu
    function resetMenu() {
        dropdownMenu.style.left = '-250px';  // Cache le menu à gauche
        overlay.style.display = 'none';  // Cache l'overlay
        dropdownMenu.style.display = 'none';  // Assure que le menu est caché
    }

    // Afficher ou masquer le menu et l'overlay lorsque le profil est cliqué
    profile.addEventListener('click', function() {
        if (dropdownMenu.style.display === 'block') {
            // Si le menu est déjà ouvert, on le ferme
            resetMenu();
        } else {
            // Sinon, on affiche le menu et l'overlay
            dropdownMenu.style.display = 'block';
            overlay.style.display = 'block';
            dropdownMenu.style.left = '0';  // Déplace le menu vers la droite (visible)
        }
    });

    // Fermer le menu et l'overlay si on clique en dehors
    window.addEventListener('click', function(event) {
        if (!profile.contains(event.target) && !dropdownMenu.contains(event.target) && !overlay.contains(event.target)) {
            resetMenu();  // Réinitialise le menu et l'overlay
        }
    });

    // Fermer le menu et l'overlay si on clique sur l'overlay
    overlay.addEventListener('click', function() {
        resetMenu();  // Réinitialise le menu et l'overlay
    });
});




// Fonction : Afficher un message temporaire avec gestion de clics en dehors
function afficherMessage(message, couleur) {
    const messageBox = document.createElement('div');
    messageBox.textContent = message;
    messageBox.style.position = 'fixed';
    messageBox.style.top = '50%';
    messageBox.style.left = '50%';
    messageBox.style.transform = 'translate(-50%, -50%)';
    messageBox.style.backgroundColor = couleur;
    messageBox.style.color = 'white';
    messageBox.style.padding = '15px';
    messageBox.style.borderRadius = '5px';
    messageBox.style.zIndex = '1000';
    messageBox.style.textAlign = 'center';
    document.body.appendChild(messageBox);

    // Gestionnaire d'événements pour détecter les clics en dehors
    function handleClickOutside(event) {
        if (!messageBox.contains(event.target)) {
            // Supprime la boîte de message et l'écouteur d'événements
            document.body.removeChild(messageBox);
            document.removeEventListener('click', handleClickOutside);
        }
    }

    // Ajouter un écouteur pour les clics en dehors
    document.addEventListener('click', handleClickOutside);

    // Supprimer automatiquement après 3 secondes si aucun clic
    setTimeout(() => {
        if (document.body.contains(messageBox)) {
            document.body.removeChild(messageBox);
            document.removeEventListener('click', handleClickOutside);
        }
    }, 3000); // Supprime le message après 3 secondes
}


// Fonction : Suivre la position de l'utilisateur et mettre à jour l'itinéraire
function suivreUtilisateurEtAfficherItineraire(destinationCoords) {
    if (!navigator.geolocation) {
        afficherMessage("La géolocalisation n'est pas prise en charge par votre navigateur.", "red");
        return;
    }

    navigator.geolocation.watchPosition(
        (position) => {
            const { latitude, longitude } = position.coords;

            // Mettre à jour la position de l'utilisateur
            if (userMarker) {
                userMarker.setLatLng([latitude, longitude]);
            } else {
                userMarker = L.marker([latitude, longitude], { draggable: false, color: 'blue' }).addTo(map);
            }

            // Envoyer une requête pour calculer le plus court chemin
            fetch('/api/itineraire', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_coords: [latitude, longitude],
                    destination_coords: destinationCoords
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        const pathCoords = data.path;

                        // Supprimer l'ancien itinéraire
                        if (routeLayer) {
                            map.removeLayer(routeLayer);
                        }

                        // Tracer le nouvel itinéraire
                        routeLayer = L.polyline(pathCoords, { color: 'blue', weight: 5 }).addTo(map);

                        // Vérifier si l'utilisateur est arrivé à destination
                        const userLatLng = L.latLng(latitude, longitude);
                        const destinationLatLng = L.latLng(destinationCoords[0], destinationCoords[1]);
                        if (userLatLng.distanceTo(destinationLatLng) < 10) { // Seuil de proximité (10 mètres)
                            afficherMessage("Vous êtes arrivé.", "green");
                        }
                    } else {
                        afficherMessage("Erreur lors du calcul de l'itinéraire ", "red");
                    }
                })
                .catch(err => afficherMessage("Erreur lors de la requête de l'itinéraire : " , "red"));
        },
        (error) => {
            afficherMessage("Impossible d'obtenir votre position  ", "red");
        },
        { enableHighAccuracy: true }
    );
}

// Gestionnaire pour la fonctionnalité "itinéraire"
document.getElementById('fonction2').addEventListener('click', () => {
    if (marker.length === 0) {
        afficherMessage("Aucun marqueur trouvé sur la carte.", "red");
        return;
    }

    // Prendre le premier marqueur du tableau comme destination
    const destinationMarker = marker[0];
    const destinationCoords = [
        destinationMarker.getLatLng().lat,
        destinationMarker.getLatLng().lng
    ];

    suivreUtilisateurEtAfficherItineraire(destinationCoords);
});

//evenement sur les amphi-container
document.querySelector(".amphi-container")


// Fonction pour gérer la recherche
function handleSearch() {
    const searchButton = document.getElementById("searchbutton");

    searchButton.addEventListener("click", () => {
    const searchInput = document.getElementById("searchinput").value.trim();
        if (searchInput) {
        
        if (searchInput.startsWith("@@")) {
            try {
                // Extraire les coordonnées entre les crochets
                const match = searchInput.match(/^@@\[(\d+(\.\d+)?\s\d+(\.\d+)?)\]$/);

                if (!match) {
                    throw new Error("Format des coordonnées incorrect.");
                }

                const coords = match[1].split(" ");
                const latitude = parseFloat(coords[0]);
                const longitude = parseFloat(coords[1]);

                if (isNaN(latitude) || isNaN(longitude)) {
                    throw new Error("Coordonnées invalides.");
                }

                // Enlever tous les marqueurs
                removeAllMarkers();
                

                // Ajouter le nouveau marqueur
                const marker = L.marker([latitude, longitude], {
                    draggable: false,
                    icon: L.icon({
                        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                        shadowSize: [41, 41]
                    })
                }).addTo(map);

                // Centrer la carte sur le marqueur
                map.setView([latitude, longitude], 19);

                // Ajouter une popup au marqueur
                marker.bindPopup(`ses Coordonnées : ${latitude}, ${longitude}`).openPopup();
            } catch (error) {
                afficherMessage("Mauvaise copie ! " ,"red");
            }
        } else {
            //enlever les itinéraires
            if (routeLayer) {
                map.removeLayer(routeLayer);
            }
            //trouver le lieu
            rechercherLieu(searchInput);
        }
}
else {
        afficherMessage("Veuillez entrer un nom de lieu à rechercher.", "red");
    }
});
}

// Fonction pour supprimer tous les marqueurs
function removeAllMarkers() {
    marker.forEach(marker => map.removeLayer(marker));
    marker = [];
}

// Appeler la fonction lorsque la page est prête
document.addEventListener("DOMContentLoaded", handleSearch);


// Fonction pour copier la position d'un élément de classe "share" au format "@@[x y]"
function activerPartage() {
    // Sélectionner tous les éléments ayant la classe "share"
    const shareElements = document.querySelectorAll('.share');

    shareElements.forEach(element => {
        element.addEventListener('click', () => {
            // Extraire la position de l'élément
            const lat = element.getAttribute('data-lat');
            const lng = element.getAttribute('data-lng');

            if (lat && lng) {
                // Formater la position
                const positionFormat = `@@[${lat} ${lng}]`;

                // Copier dans le presse-papier
                navigator.clipboard.writeText(positionFormat)
                    .then(() => {
                        // Afficher une afficherMessagee de succès
                        afficherMessage("Position copiée avec succès!" , "red");
                    })
                    .catch(err => {
                        console.error("Erreur lors de la copie :", err);
                        afficherMessage("Impossible de copier la position." , "red");
                    });
            } else {
                afficherMessage("Position non disponible.");
            }
        });
    });
}

// Activer la fonctionnalité au chargement de la page
document.addEventListener('DOMContentLoaded', activerPartage);

//events

document.addEventListener("DOMContentLoaded", function () {
    const horizontalTexts = document.querySelector(".horizontal-texts");
  
    // Fonction pour vérifier la largeur de l'écran et appliquer la classe active
    function toggleMenu() {
      // Vérifier la largeur de l'écran
      if (window.innerWidth <= 768) {
        horizontalTexts.style.display = "flex"; // Afficher la div sur les écrans moyens ou plus grands
      } 
       
    }
  
    // Gérer le clic sur la div pour déplier/plier
    horizontalTexts.addEventListener("click", function () {
      horizontalTexts.classList.toggle("active");
    });
  
    // Fermer la div lorsque l'un des éléments est cliqué
    const links = document.querySelectorAll(".horizontal-texts .text-overlay a");
    links.forEach(function (link) {
      link.addEventListener("click", function () {
        horizontalTexts.classList.remove("active");
      });
    });
  
    // Fermer la div si l'utilisateur clique en dehors de celle-ci
    document.addEventListener("click", function (event) {
      if (!horizontalTexts.contains(event.target)) {
        horizontalTexts.classList.remove("active");
      }
    });
  
    // Vérifier la taille de l'écran au démarrage et au redimensionnement
    toggleMenu(); // Appliquer la logique de base lors du chargement initial
    window.addEventListener("resize", toggleMenu); // Vérifier lors du redimensionnement de l'écran
  });
  
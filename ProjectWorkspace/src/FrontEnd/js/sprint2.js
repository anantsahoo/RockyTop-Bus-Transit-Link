document.addEventListener("DOMContentLoaded", () => {
	/* Handle form submission and route suggestions */
	const form = document.getElementById("location-form");
	const routesList = document.getElementById("routes-list");

	form.addEventListener("submit", (event) => {
		event.preventDefault();

		const currentLocation = document
			.getElementById("current-location")
			.value.trim();
		const destination = document.getElementById("destination").value.trim();
		document.getElementById("current-location").value = ""
		document.getElementById("destination").value = "";
		routesList.innerHTML = ""; /* Clear previous routes */

		if (!currentLocation || !destination) {
			alert("Please enter both current location and destination.");
			return;
		}

		// send routing information to the backend
		const generateRoutes = (from, to) => {
			const dataToSend = {
				locationToSend : from,
				destinationToSend: to
			}
			
			url = 'http://127.0.0.1:5000/send-route-info'
			fetch(url, {
				method: 'POST', 
				headers: {
				'Content-Type': 'application/json', 
				},
				body: JSON.stringify(dataToSend) 
			})
			.then(response => {
				if (!response.ok) {
				throw new Error('Network response was not ok');
				}
				return response.json(); 
			})
			.then(data => {
				if (data.success){
					// need to work with backend to figure out what is needed to be returned
					console.log('Success'); 
				}
				else{
					console.log('Error');
				}
			})
			.catch(error => {
				console.error('There was a problem with the fetch operation:', error); 
			});
			return [
				`Bus 12: From ${from} to ${to}`,
				`Bus 20: From ${from} to ${to}`,
				`Bus 7: From ${from} to ${to}`,
			];
		};

		const suggestedRoutes = generateRoutes(currentLocation, destination);
		suggestedRoutes.forEach((route) => {
			const li = document.createElement("li");
			li.textContent = route;
			routesList.appendChild(li);
		});
	});
});

const inputBox = document.getElementById("input-box");
const listContainer = document.getElementById("list-container");
const favoriteList = document.getElementById("slide-out-favorite");
const history = document.getElementById("slide-out-history");

/* Adds item to favorites list */
function addTask() {
	if (inputBox.value === "") {
		alert("You must write something!");
	} else {
		let li = document.createElement("li");
		li.innerHTML = inputBox.value;
		listContainer.appendChild(li);
		let span = document.createElement("span");
		span.innerHTML = "\u00d7";
		li.appendChild(span);
	}
	inputBox.value = "";
	saveData();
}

/* Removes item from the favorites list */
listContainer.addEventListener(
	"click",
	function (e) {
		if (e.target.tagName === "SPAN") {
			e.target.parentElement.remove();
			saveData();
		}
	},
	false
);

/* Stores user's favorites data in the browser */
function saveData() {
	localStorage.setItem("data", listContainer.innerHTML);
}

function showTask() {
	listContainer.innerHTML = localStorage.getItem("data");
}

/* Slides in the favorites list */
function showFavoritesList() {
	/* Close history if it's open */
	const history = document.getElementById("slide-out-history");
	if (history.style.width !== "0%") {
		history.style.width = "0%"; /* Close History */
	}

	/* Toggle favorites list */
	favoriteList.style.width = favoriteList.style.width === "0%" ? "30%" : "0%";
}

/* Slides in the history popup */
function showHistory() {
	const history = document.getElementById("slide-out-history");
	/* Close favorites if it's open */
	if (favoriteList.style.width !== "0%") {
		favoriteList.style.width = "0%"; /* Close Favorites */
	}

	/* Toggle history section */
	history.style.width = history.style.width === "0%" ? "30%" : "0%";
}

/* Adds items to the history based on the user's account*/
function populateHistory(data) {
	const historyList = document.getElementById("history-list");

	/* Clear placeholder items (if any) */
	historyList.innerHTML = "";
	url = 'http://127.0.0.1:5000/get-history'
	fetch(url)
	.then(response => {
		if (!response.ok) {
		throw new Error('Network response was not ok');
		}
		return response.json(); 
	})
	.then(data => {
		if (data.success){
			console.log('Success'); 
			/* Loop through the data and append items to the history list */
			data.list.forEach((item) => {
				const li = document.createElement("li");
				li.textContent = item;
				historyList.appendChild(li);
			});
		}
		else{
			console.log('No History Found');
			for (let i = 1; i < 5; i++){
				const li = document.createElement("li");
				li.textContent = "Placeholder " + i;
				historyList.appendChild(li);
			}
		}
	})
	.catch(error => {
		console.error('There was a problem with the fetch operation:', error); 
	});
}

/* Load saved tasks after page load */
showTask();

let latitude
let longitude
let id
// if location was found, then send it to the backend
const location_success = (position)=> {
    console.log(position);
    latitude = position.coords.latitude
    longitude = position.coords.longitude
    const dataToSend = {
        latitude: latitude,
        longitude: longitude
    };
	url = 'http://127.0.0.1:5000/send-real-time-location'
	fetch(url, {
		method: 'POST', // Send a POST request
		headers: {
		  'Content-Type': 'application/json', // Specify that we are sending JSON
		},
		body: JSON.stringify(dataToSend) // Convert JavaScript object to JSON
	  })
	  .then(response => {
		if (!response.ok) {
		  throw new Error('Network response was not ok');
		}
		return response.json(); // Parse JSON from the response
	  })
	  .then(data => {
		// Handle the JSON response from Flask
		if (data.success){
			// need to work with backend to figure out what is needed to be returned
			console.log('Success'); 
		}
		else{
			console.log('Error');
		}
	  })
	  .catch(error => {
		console.error('There was a problem with the fetch operation:', error); 
	  });
};
// if location couldn't be found then give reason why
const location_error = (error) => {
    console.log(error);
    if (error.code === 1){
        alert("Please enable location permissions to allow real-time location access")
    }
    else if(error.code === 2){
        alert("Unknown error occurred while getting location")
    }
    else if (error.code === 3){
        alert("Timeout occured while getting location, please reload")
    }
}
const location_options = {
    enableHighAccuracy: true,
    timeout: 2000
}
// get the user's location
if (navigator.geolocation){
    id = navigator.geolocation.watchPosition(location_success, location_error, location_options);
	// use when switching off of the map page
	// navigator.geolocation.clearWatch(id);
}
else{
    console.log("Geolocation is not supported by this browser.");
}

/* ------------ Login Functionality ------------ */
document.getElementById("login-form").addEventListener("submit", (event) => {
	event.preventDefault();

	const username = document.getElementById("username").value.trim();
	const password = document.getElementById("password").value.trim();

	if (!username || !password) {
		alert("Please enter both username and password.");
		return;
	}

	const loginData = {
		username: username,
		password: password,
	};

	fetch("http://127.0.0.1:5000/login", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(loginData),
	})
		.then((response) => {
			if (!response.ok) {
				throw new Error("Login failed.");
			}
			return response.json();
		})
		.then((data) => {
			if (data.success) {
				alert("Login successful!");
				// Handle successful login, redirect, etc from the backend.
			} else {
				alert("Invalid login credentials.");
			}
		})
		.catch((error) => {
			console.error("Error during login:", error);
			alert("Login failed.");
		});
});

// Make the slide-outs disappear when cursor is no longer pointing at them
const favorites = document.getElementById('slide-out-favorite');
favorites.addEventListener('mouseleave', function() {
	favorites.style.width = "0";
});

const historySlideIn = document.getElementById('slide-out-history');
historySlideIn.addEventListener('mouseleave', function() {
	historySlideIn.style.width = "0";
});
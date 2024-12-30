document.addEventListener("DOMContentLoaded", () => {
	/* Get references to the form and routes list */
	const form = document.getElementById("location-form");
	const routesList = document.getElementById("routes-list");

	form.addEventListener("submit", (event) => {
		event.preventDefault();

		/* Get the current location and destination inputs */
		const currentLocation = document
			.getElementById("current-location")
			.value.trim();
		const destination = document.getElementById("destination").value.trim();

		/* Clear previous routes */
		routesList.innerHTML = "";

		/* Check if inputs are valid else stop execution if inputs are invalid */
		if (!currentLocation || !destination) {
			alert("Please enter both current location and destination.");
			return;
		}

		/* Mock function to generate suggested routes based on input */
		const generateRoutes = (from, to) => {
			return [
				`Bus 12: From ${from} to ${to}`,
				`Bus 20: From ${from} to ${to}`,
				`Bus 7: From ${from} to ${to}`,
			];
		};

		/* Get suggested routes */
		const suggestedRoutes = generateRoutes(currentLocation, destination);

		/* Display suggested routes */
		suggestedRoutes.forEach((route) => {
			const li = document.createElement("li");
			li.textContent = route;
			routesList.appendChild(li);
		});
	});
});

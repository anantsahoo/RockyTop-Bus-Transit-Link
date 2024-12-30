document.addEventListener("DOMContentLoaded", () => {
    // Attach event listeners to the "Favorites" and "History" links
    const favoritesLink = document.getElementById("favorites-link");
    const historyLink = document.getElementById("history-link");

    if (favoritesLink) {
        favoritesLink.addEventListener("click", function (event) {
            event.preventDefault();
            toggleFavoritesSlideOut();
        });
    }

    if (historyLink) {
        historyLink.addEventListener("click", function (event) {
            event.preventDefault();
            toggleHistorySlideOut();
        });
    }

    // Initialize variables after DOM content is loaded
    const inputBox = document.getElementById("input-box");
    const listContainer = document.getElementById("list-container");
    const favoriteList = document.getElementById("slide-out-favorite");
    const history = document.getElementById("slide-out-history");
    const addButton = document.getElementById("add-bus-stop");

    // Check if elements exist before adding event listeners
    if (addButton && inputBox && listContainer) {
        addButton.addEventListener("click", addTask);

        // Load saved tasks after page load
        showTask();
    }

    // Define functions that use these variables
    function addTask() {
        if (inputBox.value === "") {
            alert("You must write something!");
        } else {
            let favorite_place = inputBox.value.trim();
            // Send AJAX POST request to add favorite
            fetch(addFavoriteUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 'favorite_place': favorite_place })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update favoritePlaces array
                    favoritePlaces.push(favorite_place);
                    // Add the favorite place to the list
                    let li = document.createElement("li");
                    li.innerHTML = favorite_place;
                    let span = document.createElement("span");
                    span.innerHTML = "\u00d7";
                    span.onclick = function () { removeFavorite(this); };
                    li.appendChild(span);
                    listContainer.appendChild(li);
                    inputBox.value = "";
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while adding the favorite location.');
            });
        }
    }

    function removeFavorite(spanElement) {
        let li = spanElement.parentElement;
        let place_to_remove = li.firstChild.textContent.trim();

        fetch(removeFavoriteUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'place_to_remove': place_to_remove })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the favorite place from the list and array
                li.remove();
                const index = favoritePlaces.indexOf(place_to_remove);
                if (index > -1) {
                    favoritePlaces.splice(index, 1);
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while removing the favorite location.');
        });
    }

    function showTask() {
        listContainer.innerHTML = '';
        favoritePlaces.forEach(function(place) {
            let li = document.createElement("li");
            li.innerHTML = place;
            let span = document.createElement("span");
            span.innerHTML = "\u00d7";
            span.onclick = function () { removeFavorite(this); };
            li.appendChild(span);
            listContainer.appendChild(li);
        });
    }
    

    function toggleFavoritesSlideOut() {
        // Fetch updated favorites from the backend
        fetch('/get_favorites')
        .then(response => response.json())
        .then(data => {
            if (data.favorite_places) {
                favoritePlaces = data.favorite_places;
                // Clear the existing list
                listContainer.innerHTML = '';
                // Populate the list with updated favorites
                favoritePlaces.forEach(place => {
                    let li = document.createElement("li");
                    li.innerHTML = place;
                    let span = document.createElement("span");
                    span.innerHTML = "\u00d7";
                    span.onclick = function () { removeFavorite(this); };
                    li.appendChild(span);
                    listContainer.appendChild(li);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching favorites:', error);
        });

        // Toggle the favorites slide-out
        if (favoriteList) {
            favoriteList.classList.toggle("active");
        }

        // Close history if it's open
        if (history && history.classList.contains("active")) {
            history.classList.remove("active");
        }
    }

    function toggleHistorySlideOut() {
        // Fetch and populate history
        fetch('/get_history')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.history) {
                const historyList = document.getElementById("history-list");
                historyList.innerHTML = ''; // Clear existing items
                data.history.forEach(item => {
                    const li = document.createElement("li");
                    li.innerHTML = `<strong>${item.start_stop}</strong> to <strong>${item.end_stop}</strong> on ${item.timestamp}`;
                    historyList.appendChild(li);
                });
            } else {
                console.log('No history found.');
            }
        })
        .catch(error => {
            console.error('Error fetching history:', error);
        });

        // Toggle the history slide-out
        if (history) {
            history.classList.toggle("active");
        }

        // Close favorites if it's open
        if (favoriteList && favoriteList.classList.contains("active")) {
            favoriteList.classList.remove("active");
        }
    }
});

fetch(addFavoriteUrl, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 'favorite_place': favorite_place })
})
.then(response => {
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
})
.then(data => {
    // Handle success
})
.catch(error => {
    console.error('Error:', error);
    alert('An error occurred while adding the favorite location.');
});
function setupAutocomplete(inputId) {
    $("#" + inputId).autocomplete({
        source: function(request, response) {
            $.ajax({
                url: autocompleteUrl,  // Using the variable defined in the HTML template
                dataType: "json",
                data: { term: request.term },
                success: function(data) {
                    console.log("Autocomplete data:", data);  // Debugging
                    response(data);
                },
                error: function(xhr, status, error) {
                    console.error("Autocomplete error:", error);  // Error handling
                }
            });
        },
        minLength: 2,
        select: function(event, ui) {
            $("#" + inputId).val(ui.item.label);
            return false;
        }
    });
}
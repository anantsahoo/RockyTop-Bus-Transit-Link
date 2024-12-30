const inputBox = document.getElementById("input-box");
const listContainer = document.getElementById("list-container");
const favoriteList = document.getElementById("slide-out-favorite");
const history = document.getElementById("slide-out-history")

// adds item to favorites list
function addTask(){
    if(inputBox.value === ''){
        alert("You must write something!");
    }
    else{
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

// removes item from the favorites list
listContainer.addEventListener("click", function(e){
    if(e.target.tagName === "SPAN"){
        e.target.parentElement.remove();
        saveData();
    }
}, false);

// stores user's favoites data on the browser
function saveData(){
    localStorage.setItem("data", listContainer.innerHTML);
}
function showTask(){
    listContainer.innerHTML = localStorage.getItem("data");
}

// slides in the favorites list
function showFavoritesList(){
    if (favoriteList.style.width === "0%") {
        favoriteList.style.width = "40%";
    }
    else{
        favoriteList.style.width = "0%";
    }
}

// slides in the history popup
function showHistory(){
    history.classList.toggle("open"); // Toggle open class
}

// adds items to the history based on the user's account (for later when we have the functionality)
function populateHistory(data) {
    const historyList = document.getElementById('history-list');
    
    // Clear placeholder items (if any)
    historyList.innerHTML = '';

    // Loop through the data and append items to the history list
    data.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item; 
        historyList.appendChild(li);
    });
}

showTask();
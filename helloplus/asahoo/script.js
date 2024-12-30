/* Citation: Used YouTube, StackOverflow, and GeeksforGeeks to understand function implementations
 * and get inspiration for the way to approach this simple code in Javascript. Used YouTube and
 * documentations to learn JavaScript and CSS.
 */

/* The goal of this function is to greet the user based on the time of the day. */
function updateGreeting() {
	const hour = new Date().getHours();
	let greetingText;

	if (hour < 12) {
		greetingText = "Good Morning";
	} else if (hour < 18) {
		greetingText = "Good Afternoon";
	} else {
		greetingText = "Good Evening";
	}

	document.getElementById("greeting").textContent = `${greetingText}, World!`;
}

/* This segment updates the code user based on the user's input in input field. */
document
	.getElementById("updateGreetingBtn")
	.addEventListener("click", function () {
		const nameInput = document.getElementById("nameInput").value.trim();
		const greeting = document.getElementById("greeting");

		if (nameInput !== "") {
			greeting.textContent = `Hello, ${nameInput}!`;
		} else {
			greeting.textContent = "Hello, World!";
		}
	});

/* This function is going to diplay the current time. */
function updateTime() {
	const currentTime = new Date().toLocaleTimeString();
	document.getElementById("currentTime").textContent = currentTime;
}

updateGreeting();
updateTime();

setInterval(updateTime, 1000);

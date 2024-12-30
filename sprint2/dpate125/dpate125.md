# Sprint 2

Name: Deep Patel

GitHubID: Deep0320

Group Name: Rocky Top Transit Link

### What I planned to do
* Issue #18: Get location information [Link to Issue 18](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/18)
* Issue #19: Send location information to the backend [Link to Issue 19](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/19)
* Issue #22: Make the slide-ins disappear when the mouse is no longer over them [Link to Issue 22](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/22)
* Issue #27: Add more information about a stop when clicked on the map [Link to Issue 27](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/27)
* Issue #29: Send suggested routes information to the backend [Link to Issue 29](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/29)
* Issue #35: Get the history information from backend and populate the history section [Link to Issue 35](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/35)
* Issue #36: Add basic styling to text in both slide-ins [Link to Issue 36](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/36)


### What I did not do
* Everything I was assigned for sprint 2 was completed.

### What problems I encountered
* I wasn't able to make sure that the sending and receiving of information works as our team member who would be in charge of merging the backend and frontend dropped the class, so I couldn't test if the frontend code is properly sending requests. 

### Issues I worked on
* [#18](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/18) Get the location of the user
* [#19](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/19) Send location to back-end
* [#22](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/22) Make the favorites list and history list disappear once the user's mouse moves off of the slide-in
* [#27](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/27) Add More Information About Stop When Pin Clicked
* [#29](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/29) Send suggested route information from main page to back-end
* [#35](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/35) Populate the History Slide-in
* [#36](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/36) Add basic styling to history and favorites list items

### Files I worked on
* `ProjectWorkspace/src/FrontEnd/sprint2.html`
* `ProjectWorkspace/src/FrontEnd/CSS/sprint2.css`
* `ProjectWorkspace/src/FrontEnd/js/sprint2.js`
* `ProjectWorkspace/src/BackEnd/v3/app/templates/stop_detail.html`

### What I accomplished
* **Get location information**: Getting the user's current location is essential for the app to be easy to use since we don't want the user to have to always input where they are as they walk. I worked out how to get the user's location even if they are moving in which case it will constantly update the location as they travel.

* **Sending various information to the Backend**: I sent location information and routing information to the backend that they can use to do their calculations and then return information that can be plotted on the map (not finished yet as the frontend and backend wasn't able to be connected due to our teammate's withdrawal from the class).

* **Populating the History** I added functionality to get history information from the Backend and then show it on the history slide-in.

* **Adding information to pins** I was able to create a way for the user to get more information upon clicking a pin on the map which will list various information about the bus stop.

* **Other Changes** I also added minor changes on the updated merged Frontend file Anant Sahoo worked on, and worked with him to help him integrate my sprint1 code into his as needed.
# Sprint 3 Reflection

## Name
Harrison Crettol

## GitHub Username
harrisoncrettol

## Project
Rocky Top Transit Link

## What I Planned to Do
- **Not an official issue:** Integrate everyone's code (Anant and Deep's home page and Will's Sprint 2 route logic) into one main project directory and get everyone on the same page.
- **Issue #47:** Click Twice Bug. [Link to Issue](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/50)
- **Issue #50:** Allow Password Change. [Link to Issue](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/50)
- **Issue #51:** Update Stop Details. [Link to Issue](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/51)
- **Issue #55:** Route Calculation. [Link to Issue](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/55)
- **Issue #56:** Add Toggle Switches for Pins. [Link to Issue](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/56)

## What I Did Not Do
- Everything planned was completed.

## Problems Encountered
- **Integrating Everyone's Code**: I had to modify Anant and Deep's html/css/js files for the homepage so that they were compatiable with the existing backend.
- **Route Calculation**: The route calculation still doesn't fully work for every stop and it is pretty slow.

## Issues Worked On
- [Issue #47: Click Twice Bug](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/31)
- [Issue #50: Allow Password Change](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/30)
- [Issue #51: Update Stop Details](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/26)
- [Issue #55: Route Calculation](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/25)
- [Issue #56: Add Toggle Switches for Pins](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/24)

## Files Worked On
- `ProjectWorkspace\src\BackEnd\v4\requirements.txt`
- `ProjectWorkspace\src\BackEnd\v4\app\forms.py`
- `ProjectWorkspace\src\BackEnd\v4\app\graph_utils.py`
- `ProjectWorkspace\src\BackEnd\v4\app\routes.py`
- `ProjectWorkspace\src\BackEnd\v4\app\templates\map.html`
- `ProjectWorkspace\src\BackEnd\v4\app\templates\settings.html`
- `ProjectWorkspace\src\BackEnd\v4\app\templates\stop_detail.html`


## What I Accomplished:
- First I integrated everyone's code into the v4 folder. Then we held a meeting where I got everyone up to speed with the project. I made a video for my group members showing them how to run the project from scratch, and made sure eveyone understood how to run it.
- Before the meeting I made a sprint 3 backlog ***(see below)*** with issues that I thought we could potentially do this sprint. Durring the meeting we went over my backlog and assigned issues to everyone.
- Then I worked on my issues, first implementing the route finding logic.
- Then one of my group members, Anant, reached out to me asking for help. I met with him for roughly 2 hours doing pair programming and we were able to complete all of his issues. I reached out to my other group members offering help and so far Will got back to me and scheduled a meeting for later today (10/29/2024).
- After that I finished my other issues and started prepairing for sprint 4 by making note of any bugs or things that could be changed or added.
- Lastly, I met with Will and helped him with his issues.

## Sprint 3 Backlog I made:
BE = Back End
FE = Front End

Current bugs:
- The Login button on the home page's hover functionality prematurely hides the input fields. (FE)
- When using the names of bus stops as the start/end location, an error occurs when finding route. (BE)
- On the home page, sometimes you'll need to click "Favorites" or "History" twice to make them show up. (BE)
- When adding a location to the favorites tab, if there are commas in the location name, it will split and make multiple locations split at the comma. (BE)

Things that could be changed:
- Add a different color pin or icon on the map to indicate current location. (FE)
- Add a way to get back to the home page from other pages. (FE)
- Add "Register Account" and possibly "Settings" to the homepage's navbar. (FE)
- Update settings page (Remove "Add Favorite Location" and "Your Favorite Locations"). (FE)
- Make sure all pages have the same nav bar (Right now the home page's is different). (FE)
- Add a key/legend to clarify what pins represent. (FE)
- Add footers to pages that could use them. (FE)
- Add toggle switches for pins to control whether they are displayed or not. (BE)
- More detailed route calculation (need to show route on map: one from the user to the first bus stop, another one from first bus stop to final bus stop, and one from final bus stop to destination) (Also needs to account times, so use the current time to figure out when bus will be at the first bus stop) (Can use my work in v3 as a start). (BE)
- When a user finds a route, we need to save the route details so that we can display it in the history tab. (BE)
- Add existing favorite locations so that they show up in the favorites tab on the home page. (BE)
- Update the "Add" button in the favorites list on the home page so that it adds to the user's database. (Need to account for if the user is not logged in and they add a location on the home page, it needs to be accessible from the map page's "favorite locations" tab).
- Update the home page to display relevant information. (Possibly remove Routes and Schedules tab in nav bar. Possibly replace "Plan Your Journey" with a default map). (BE)
- Update Stop Details page to show more relevant information. (BE)
- Update settings page (Allow user to change password). (BE)
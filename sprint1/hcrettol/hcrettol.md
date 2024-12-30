# Sprint 1 Reflection

## Name
Harrison Crettol

## GitHub Username
harrisoncrettol

## Project
Rocky Top Transit Link

## What I Planned to Do
- **Issue #7:** Set up account registration. [Link to Issue](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/7)
- **Issue #8:** Set up account deregistration. [Link to Issue](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/8)
- **Issue #11:** Allow users to input/save favorite locations. [Link to Issue](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/11)

## What I Did Not Do
- Everything planned was completed.

## Problems Encountered
- **Map Not Displaying**: Initially, the map was not displaying properly. Adjusting the script integration resolved this issue.
- **Autocomplete Not Working**: Autocomplete functionality failed due to JavaScript errors. Correcting the script order fixed the issue.
- **Favorite Locations Not Populating**: Favorite locations were not showing on the map. Fixing data passing in the back-end resolved this.

## Issues Worked On
- [Issue #7: Set up account registration](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/7)
- [Issue #8: Set up account deregistration](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/8)
- [Issue #11: Allow users to input/save favorite locations](https://github.com/utk-cs340-fall24/RockyTop-Transit-Link/issues/11)

## Files Worked On
- `sprint1\BACKLOG.md`
- `sprint1\hcrettol\hcrettol.md`
- `sprint1\hcrettol\v1\README.md`
- `sprint1\hcrettol\v1\requirements.txt`
- `sprint1\hcrettol\v1\run.py`
- `sprint1\hcrettol\v1\app\config.py`
- `sprint1\hcrettol\v1\app\models.py`
- `sprint1\hcrettol\v1\app\routes.py`
- `sprint1\hcrettol\v1\app\__init__.py`
- `sprint1\hcrettol\v1\app\templates\home.html`
- `sprint1\hcrettol\v1\app\templates\login.html`
- `sprint1\hcrettol\v1\app\templates\register.html`
- `sprint1\hcrettol\v1\app\templates\welcome.html`
- `sprint1\hcrettol\v2\README.md`
- `sprint1\hcrettol\v2\requirements.txt`
- `sprint1\hcrettol\v2\run.py`
- `sprint1\hcrettol\v2\app\models.py`
- `sprint1\hcrettol\v2\app\routes.py`
- `sprint1\hcrettol\v2\app\__init__.py`
- `sprint1\hcrettol\v2\app\templates\base.html`
- `sprint1\hcrettol\v2\app\templates\login.html`
- `sprint1\hcrettol\v2\app\templates\map.html`
- `sprint1\hcrettol\v2\app\templates\register.html`
- `sprint1\hcrettol\v2\app\templates\settings.html`
- `sprint1\hcrettol\v2\gtfs\agency.txt`
- `sprint1\hcrettol\v2\gtfs\calendar.txt`
- `sprint1\hcrettol\v2\gtfs\calendar_attributes.txt`
- `sprint1\hcrettol\v2\gtfs\calendar_dates.txt`
- `sprint1\hcrettol\v2\gtfs\directions.txt`
- `sprint1\hcrettol\v2\gtfs\feed_info.txt`
- `sprint1\hcrettol\v2\gtfs\realtime_routes.txt`
- `sprint1\hcrettol\v2\gtfs\routes.txt`
- `sprint1\hcrettol\v2\gtfs\shapes.txt`
- `sprint1\hcrettol\v2\gtfs\stops.txt`
- `sprint1\hcrettol\v2\gtfs\stop_times.txt`
- `sprint1\hcrettol\v2\gtfs\trips.txt`

## What I Accomplished
- **Map Page as Homepage:** Configured and set up the interactive map page to serve as the default homepage for the application, making it immediately accessible upon login. Ensured that the map loads correctly using Leaflet.js, which enhances the visual appeal and usability of our application.

- **User Authentication:** Developed and integrated a full user authentication system, allowing users to register for an account, log in, and securely delete their account if desired. This system is built to ensure that user data is handled securely and provides a foundation for adding more personalized features in the future.

- **Enhanced Map Features:** Enhanced the map with additional interactive features such as displaying bus stops. Implemented an autocomplete search feature to help users quickly find bus stops.

- **User Settings Page:** Created a settings page that allows users to manage their personal settings, including adding or removing favorite locations and deleting their account. This page makes the application more tailored to individual user needs.

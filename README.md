Hitchcock is a web application for managing and providing access to locally hosted electronic reserves materials.

# Setup
Requires Python 3.5 or later.

``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
patches/apply_patches.sh

cp src/hitchcock/settings_copy_me.py src/hitchcock/settings.py
# ... edit src/hitchcock/settings.py ...

python manage.py runserver
```

# Tests
Tests are in `tests/`. See `tests/README.md`.

# Set up MEDIA_ROOT
- Chose a location with adequate storage for Hitchcock to store uploaded asset files. E.g. `/var/www/html/hitchcock_files`.
- Make sure it's writable by the user/group that the Hitchcock web service runs as.
- Set the MEDIA_ROOT variable in `src/hitchcock/settings.py`.

# Setting up serving Text materials
Hitchcock relies on an external web server (such as Apache or NGINX) to serve text materials.

## Setup
- Point your web server to a directory from which to serve the text files. The default subdirectory for text materials under MEDIA_ROOT is 'text/' so for example the website directory would be `/var/www/html/hitchcock_files/text/`
- Set the `TEXTS_ENDPOINT` variable in `src/hitchcock/settings.py` to the web location that the web server is configured to

# Panopto Upload API integration

Hitchcock uses the Panopto streaming service for transcoding and delivering AV content. When the user checks "Upload to panopto" and submits the Video edit page, Hitchcock will upload the asset to the Panopto service for ingest and automatically update the Panopto session id field. Hitchcock uses the Panopto Upload API to accomplish this. If the user opts not to automatically upload the file to Panopto they may also manually paste in an existing Panopto session ID into the Panopto session id field.

## Quick Setup

### API Client Setup
- Log into Panopto with an administrator account
- Under System create an API Client
- Set the Client Type to 'Server-side Web Application'
- Add a CORS Origin URL set to the fully qualified Hitchcock base url
- Add a Redirect URL constructed thusly: [HITCHCOCK_BASE_URL]/panopto-auth2-redirect
- Edit the variables in PANOPTO SETTINGS section in `src/hitchcock/settings.py` filling in the values from the API client like
- Make sure that the PANOPTO_UPLOAD_MANIFEST_TEMPLATES and PANOPTO_AUTH_CACHE_FILE_PATH paths are writable by the user/group that the Hitchcock web service runs as.

### Oauth2 bearer token creation
Log in as a super user in Hitchcock and point your web browser to [HITCHCOCK_BASE_URL]/admin/renew-panopto-token. This will redirect you to a Panopto log-in page and automatically redirect you back to the Hitchcock Oauth2 redirect endpoint (/panopto-auth2-redirect) which will consume the bearer token and cache it for later use.
Hence forth the API authentication should be set up and should require possibly only a very occasional retrial of the above steps.

### Set up Panopto upload background processing cron job
Add a line to your crontab that looks something like this:

```
0 */3 * * * .../venv/bin/python .../app/src/manage.py process_tasks --duration 10800
```

Make sure you add the full path to the Python executable in your venv directory and the manage.py file.

## Background
### API
Hitchcock uses the Panopto Upload API to upload AV to Panopto (https://support.panopto.com/s/article/Upload-API). Uploads to Panopto are called "sessions". Upon creation of a "session" the API returns a "session id" which is used to retrieve the AV in the future. Hitchcock automatically grabs the session id after upload and adds it to the "panopto session id" field after successful creation.

### API Client Authentication
Once the API Client is set up on the Panopto side and the settings are configured in the Hitchcock settings file you must generate the initial bearer token which will ask you to log in to authorize the API connection from Hitchcock.
To do this log in as a super user in Hitchcock and point your web browser to [HITCHCOCK_BASE_URL]/admin/renew-panopto-token. This will redirect you to a Panopto log-in page and automatically redirect you back to the Hitchcock Oauth2 redirect endpoint (/panopto-auth2-redirect) which will consume the bearer token and cache it for later use.
Hence forth the API authentication should be set up and should require possibly only a very occasional retrial of the above steps.

### Background tasks
In order to outlast the temporary duration of a web request, Hitchcock backgrounds the process of uploading to and waiting for Panopto to transcode the files. Hitchcock uses the Django app called django-background-tasks to create a queue of upload tasks. In order for the tasks to be processed the 'process_tasks' manage.py command must be running. On a local environment this can be triggered by using the command `python manage.py process_tasks`. But on a live system this should be setup as a cron job matched to the command's expiration setting. (https://django-background-tasks.readthedocs.io/en/latest/#running-tasks)

### Fulfilling requests
When a Hitchcock video URL is requested the system looks up the Panopto session id and redirects the user's browser to the Panopto session player page.


## Management commands

### create_uploads_from_csv

Usage: `python manage.py create_uploads_from_csv path/to/spreadsheet_file.csv /path/to/import/directory`

Takes a CSV file with a specific column structure and uses it to add the files
to the media directory, create new upload objects, and link the new upload
objects to the existing Panopto sessions.

### move_unused_files

Usage: `python manage.py move_unused_files [name_for_unused_folder]`.

This script searches the media root for video, audio, texts, and subtitle
tracks that aren't linked to an upload object, and moves them to the
designated folder. These files can then be manually deleted as desired.

The parameter `[name_for_unused_folder]` indicates the name of the folder,
directly under the media root, where unlinked files should go. It defaults
to `unused`. If the folder doesn't exist, it will be created.

### rename_upload

Usage: `python manage.py rename_upload type_of_upload old_file_name new_file_name`

This script allows an admin to rename a file that was given an non-descriptive
filename (such as `video.mp4`), or to move a file that was saved in the wrong
place.

The parameter `type_of_upload` can be one of four values: `Video`, `Audio`,
`Text`, or `VttTrack` (capitalization is important). This indicates the type
of file that needs to be moved.

The parameters `old_file_name` and `new_file_name` are just the filename with
extension, not the complete path. The script will resave any upload
associated with a file that matches the exact filename, regardless of what
folder that file is in. When the new file is saved, it will be located in
the default folder for that media type, which may be different from the place
that the file was originally saved.

If the old file name and the new file name are the same, and the location is
also the same, a suffix will be appended.

### rename_panopto_sessions

Usage `python manage.py rename_panopto_sessions [--noconfirmation] [--audio]`

This script allows the user to rename Panopto sessions that are based on
a filename instead of a title, giving a better user experience. It will go
through each video upload for which the title in Hitchcock does not match
the title in Panopto and ask if you want to rename it.

To rename audio uploads, use the `--audio` parameter.

To bulk update all sessions with titles that don't match, without confirming
each session individually, use `--noconformation`.

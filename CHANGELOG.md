# Hitchcock Releases

## [2.2.7] - 2022-06-03

### New functions
- Allow changing folder on playlists after creation

### Improvements

- Hide "Upload to Panopto" checkbox if an upload is already underway,
  to prevent duplicate uploads
- Don't allow changing folder while an upload is underway, because
  then it would not be mirrored to Panopto

## [2.2.6] - 2022-06-02

### Fixes
- Corrected the connection to Panopto so that when the folder on an
  audio, video, or playlist upload is changed, it is correctly uploaded
  to Panopto

### New functions
- Added dropdown functions for "Lock Panopto ID" and "Unlock Panopto ID"
  for audio and video uploads (not accessible from All Uploads view)

### Improvements
- Relabeled "Panopto session id" to "Delivery ID of Panopto session"
  for clarity

## [2.2.5] - 2022-05-10

### Changes

Use shorter filenames for uploads, truncating from the title if necessary

## [2.2.4] - 2022-04-13
URL view/copy buttons for playlists

### Improvements
- Playlists now have buttons for copying and viewing the URL, just as
  audio, video and text uploads did before

## [2.2.3] - 2022-04-13
Hotfixes

### Changes
- Panopto section of upload is no longer collapsed by default
- Allow .mov video uploads

### Improvements
- For SC batch upload script, create new playlist if one of the specified
  name doesn't exist

### Fixes
- Error no longer appears upon playlist delete
- Popup to add a new video/audio from within a playlist is no longer empty
- Following an audio playlist URL no longer throws an error
- Fixed issue with items not appearing in Panopto after playlist is uploaded

## [2.2.2] - 2022-04-11
Batch save and update

### New functions
- The administration dropdown allows for batch saving/updating of files.
  This triggers automatic processes that are now done upon save, which
  was not the case with earlier versions, such as naming the Panopto session
  according to the Hitchcock title and mirroring the description.

### Improvements
- Can change what the default text type is in settings

## [2.2.1] - 2022-04-08
Themed interface

### New functions
- The administration interface now contains support for "Themes". This allows
  staff to change the color of the interface, as well as customize the
  wording of the header directly from the interface. Being able to customize
  the color is useful because it can visually signal different environments:
  local environment, test environment, and multiple production environments
  (such as ereserves and general acquisitions).

## [2.2.0] - 2022-04-08
Human-readable filenames drawn from titles

### Changes
- Filenames are now drawn from the title, rather than the uploaded
  filename, so that staff don't have to assign names in more than one
  place for files to be findable and filenames to be readable.
- The management command for renaming a single file has been removed,
  as files are now named according to the upload's title.
- File names and locations will be updated as appropriate when a title
  is changed.
- Files are now sorted into large buckets by year of upload (or last title
  change), to avoid crowding a single directory excessively.

## [2.1.0] - 2022-02-09
More support for Panopto integration

### New functions
- Added "folder" object to associate different files with different
  Panopto folders.
- Added "description" field to uploads and playlists, which are currently
  mirrored on Panopto
- A script has been added to support batch upload of Special Collections
  videos, including duration information

### Improvements
- Changes to titles, descriptions or folders will now trigger an update
on Panopto as well.

### Other changes
- The URL for renewing the Panopto authorization token has changed.

## [2.0.4] - 2022-01-24
Hotfix: change URL for renewing Panopto token

## [2.0.3] - 2022-01-10
Security update for Django; added URL for video playlists

## [2.0.2] - 2022-01-03
Hotfix: case-insensitive searching of titles

## [2.0.1] - 2022-01-03
Added documentation for Panopto rename management command

## [2.0.0] - 2022-01-03
Django upgrade; captions; playlists; cleanup tools

### New functions
- VTT tracks (for subtitles and captions) can now be attached to a video
  upload (VTT tracks are automatically uploaded to Panopto if there is a
  Panopto session).
- Added management command `move_unused_files` which allows the user to locate
  all unused files and move them to a separate directory.
- Added management command `rename_upload` which allows the user to provide
  a new filename for a poorly labeled file, or to move a file which has found
  its way to the wrong place.
- Added support for video and audio playlists, which are mirrored on Panopto.
- Added management command to bulk update existing Panopto sessions to use
  the human-readable title instead of the filename with underscores.

### Improvements
- When the file for an audio, video, text, or VTT track is changed, the old
  version of the file is now automatically deleted.
- When a file is deleted from Hitchcock, the corresponding Panopto session
  (if one exists) is tagged #deleted-from-hitchcock.
- Audio, video and text uploads can now be viewed separately in the admin
  interface.
- Panopto now uses the human-readable title instead of the filename as the
  session title. (The filename is still included in the description.)

### Other changes
- Django version 3.2.9 is now used.
- Titles must now be unique, and are limited to 255 characters.
- Notes and filenames are now searchable.

## [1.6.0] - 2021-11-03
Version to allow import from older Panopto sessions

### New functions
- Added management command `create_uploads_from_csv` which allows us to add
  previously uploaded Panopto sessions to Hitchcock

### Improvements
- Changed display of upload size to MB instead of bytes

### Fixes
- Corrected upload location for text uploads of "other files"
- Fixed typos

## [1.5.0] - 2021-01-12
Add audio, fix bad error messages when refresh token expires

### Added
- Add Audio upload type, which uploads to Panopto

### Fixed
- Remove code that attempts to accept oauth2 token hand off, instead print better error message that token needs to be updated manually

## [1.4.0] - 2020-11-17
Inventory view for faculty

### Added
- Add Shibboleth support
- Add view of materials in system at /inventory for faculty to see what's already digitized
- Add site settings system for staff administrators to edit settings, such as content at top of faculty view

### Fixed
- Make search case insensitive

## [1.3.1] - 2020-10-20
Bug-fix release.

### Fixed
- Fix internal server error when a user requests a video that has no Panopto session id. Displays user friendly 404 page now.
- Fix internal server error on large file upload. Maximum theoretical file size increased from 2147483647 bytes to 9223372036854775807 bytes.

## [1.3.0] - 2020-09-28
Panopto video upload features.

### Added
- Add Panopto upload API integration for Video uploads

### Removed
- Temporarily removed Audio and Audio Album upload types, until they are supported by Panopto upload API integration
- Permanently removed Wowza streaming server integrations

## [1.2.0] - 2020-09-22
Database backups and configuration files restructure.

### Added
- Install database backup utility on PROD (django-dbbackup)

### Changed
- Revise settings configuration files structure to be compatible with django-dbbackup

## [1.1.0] - 2020-09-03
Several usability enhancements.

### Added
- Add user friendly 403 and 404 pages styled with visual identity and links to help resources to get help resolving their issue
- Upload edit page: Add view link on Hitchcock url
- Upload edit page: Add copy action link on Hitchcock url

### Changed
- Upload edit page: replace the file link (that doesn't go anywhere), with some text
- Upload edit page: set Published checkbox to enabled by default
- Change barcode field validation to 15 digits (instead of 8)
- Make text type field default to blank instead of 'article', to prevent accidentally selecting 'article'
- Make "Uploads" link in bread crumbs, go to uploads listing, rather than app page

## [1.0.1] - 2020-08-26
Bug-fix release

### Changed
- Fix issue with some uploaded files being set to odd file permissions making them unreadable by web server, causing access denied message for end users

## [1.0.0] - 2020-08-17
Initial release

### Added
- Text Upload
- Video Upload with VTT support
- Audio Upload
- Audio Album Upload
- Wowza streaming server integration
- THEOPlayer based player page for Video, Audio, and Audio Album Uploads

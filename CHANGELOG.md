# Hitchcock Releases

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

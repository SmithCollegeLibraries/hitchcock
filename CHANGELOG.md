# Hitchcock Releases

## [Unreleased]
- Temporarily remove VTT support for Videos, until it is supported by Panopto upload API integration

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

## [1.1.0] - 2020-03-03
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

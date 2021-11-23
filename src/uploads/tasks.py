from background_task import background
from . import models
from .panopto import panopto_uploader, panopto_oauth2
from django.conf import settings

@background
def upload_to_panopto(id):
    oauth2 = panopto_oauth2.PanoptoOAuth2(
        settings.PANOPTO_SERVER,
        settings.PANOPTO_CLIENT_ID,
        settings.PANOPTO_CLIENT_SECRET,
        True,
        settings.PANOPTO_AUTH_CACHE_FILE_PATH)

    myavupload = models.Upload.objects.get(id=id)

    myavupload.processing_status = "Uploading to Panopto..."
    myavupload.save()
    uploader = panopto_uploader.PanoptoUploader(settings.PANOPTO_SERVER, True, oauth2)
    panopto_session_id = uploader.upload_video(settings.MEDIA_ROOT + myavupload.upload.name, settings.PANOPTO_FOLDER_ID)
    myavupload.processing_status = "Processing complete"
    myavupload.queued_for_processing = False
    myavupload.panopto_session_id = panopto_session_id
    myavupload.lock_panopto_session_id = True
    myavupload.save()
    # Now that the panopto_session_id has been saved on the video session,
    # we should check for any vtt files and uplaod those captions to the
    # Panopto session as well.
    # NB: We need to check that this is a video and not an audio; otherwise,
    # looking up VttTracks filtering by video will cause an error.
    if isinstance(myavupload, models.Video):
        vtt_uploads = models.VttTrack.objects.filter(video=myavupload)
        for track in vtt_uploads:
            track.upload_captions()

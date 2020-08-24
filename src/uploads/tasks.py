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
    myavupload.save()

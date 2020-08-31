# features/environment.py
import behave_webdriver
import logging

# -- FILE: features/environment.py
# USE: behave -D BEHAVE_DEBUG_ON_ERROR         (to enable  debug-on-error)
# USE: behave -D BEHAVE_DEBUG_ON_ERROR=yes     (to enable  debug-on-error)
# USE: behave -D BEHAVE_DEBUG_ON_ERROR=no      (to disable debug-on-error)

BEHAVE_DEBUG_ON_ERROR = True

ENVIRONMENT_SETTINGS = {
    'local': {
        'base_url': 'http://localhost:8000',
    },
    'libsandbox': {
        'base_url': 'https://libsandbox.smith.edu/hitchcock',
    },
    'ereserves': {
        'base_url': 'https://ereserves.smith.edu/hitchcock',
    },
}

def before_all(context):
    setup_debug_on_error(context.config.userdata)
    context.behave_driver = behave_webdriver.Chrome()
    context.edit_urls = {}
    context.view_urls = {}
    try:
        target = context.config.userdata['env']
    except KeyError:
        target = 'local'
    context.target = ENVIRONMENT_SETTINGS[target]
    try:
        context.password = context.config.userdata['password']
    except KeyError:
        print("You must set a password for the test_staff_user account with the -D option (e.g. `-D password=opensesame`)")
        exit(1)

def after_all(context):
    # cleanup after tests run
    context.behave_driver.quit()

def after_step(context, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        # -- ENTER DEBUGGER: Zoom in on failure location.
        # NOTE: Use IPython debugger, same for pdb (basic python debugger).
        import pdb
        pdb.post_mortem(step.exc_traceback)

def setup_debug_on_error(userdata):
    global BEHAVE_DEBUG_ON_ERROR
    BEHAVE_DEBUG_ON_ERROR = userdata.getbool("BEHAVE_DEBUG_ON_ERROR")

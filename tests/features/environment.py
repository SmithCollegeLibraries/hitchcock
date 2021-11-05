# features/environment.py
import behave_webdriver
import logging
import sys
import os
import time
import re

BEHAVE_DEBUG_ON_ERROR = True

# -- FILE: features/environment.py
# USE: behave -D BEHAVE_DEBUG_ON_ERROR         (to enable  debug-on-error)
# USE: behave -D BEHAVE_DEBUG_ON_ERROR=yes     (to enable  debug-on-error)
# USE: behave -D BEHAVE_DEBUG_ON_ERROR=no      (to disable debug-on-error)

EXEC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

# Helper function
def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(' ', '-')
    return re.sub(r'(?u)[^-\w.]', '_', s)


ENVIRONMENT_SETTINGS = {
    'local': {
        'base_url': 'http://127.0.0.1:8000',
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

def after_scenario(context, scenario):
    # Take screenshot if scenario fails
    if scenario.status == 'failed':
        screenshot_path = EXEC_PATH + '/screenshots/on_failure/' + \
        time.strftime("%Y-%m-%d-%H%M%S--") + \
        scenario.feature.name.replace(' ', '_') + '--' + \
        get_valid_filename(context.behave_driver.current_url) + \
        '.png'
        context.behave_driver.save_screenshot(screenshot_path)
        print("Screenshot saved to: " + screenshot_path)

def setup_debug_on_error(userdata):
    global BEHAVE_DEBUG_ON_ERROR
    BEHAVE_DEBUG_ON_ERROR = userdata.getbool("BEHAVE_DEBUG_ON_ERROR")

def after_step(context, behave_step):
    if BEHAVE_DEBUG_ON_ERROR and behave_step.status == "failed":
        # -- ENTER DEBUGGER: Zoom in on failure location.
        import pdb
        #pdb.post_mortem(behave_step.exc_traceback)
        pdb.Pdb(stdout=sys.__stdout__).set_trace()

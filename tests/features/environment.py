# features/environment.py
import behave_webdriver
import logging

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

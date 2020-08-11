# features/environment.py
import behave_webdriver

ENVIRONMENT_SETTINGS = {
    'local': {
        'base_url': 'http://localhost:8000',
    },
    'libsandbox': {
        'base_url': 'https://libsandbox.smith.edu/hitchcock',
    }
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

def after_all(context):
    # cleanup after tests run
    context.behave_driver.quit()

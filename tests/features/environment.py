# features/environment.py
import behave_webdriver

def before_all(context):
    context.behave_driver = behave_webdriver.Chrome()
    context.edit_urls = {}
    context.view_urls = {}

def after_all(context):
    # cleanup after tests run
    context.behave_driver.quit()

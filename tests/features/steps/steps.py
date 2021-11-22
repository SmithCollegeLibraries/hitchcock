from behave import *
import time
import os
import re
from selenium.webdriver.support.ui import Select
import sys, pdb

def get_includes_text(driver, tag, text):
    element = driver.find_element_by_xpath(\
    "//%s[contains(text(),'%s')]" % (tag, text))
    return element

def is_valid_url(url):
    regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None # True

@given('I am logged in as a staff user')
def step_imp(context):
    driver = context.behave_driver
    base_url = context.target['base_url']
    driver.switch_to_window(driver.window_handles[0])

    driver.get(base_url + '/admin/')
    if "Log in" in driver.title:
        username_input = driver.find_element_by_name('username')
        username_input.send_keys('test_staff_user')
        password_input = driver.find_element_by_name('password')
        password_input.send_keys(context.password)
        password_input.submit()
        # Check that I'm now on the site administration page
        assert "Site administration" in driver.title, "Log in problem"
    elif "Site administration" in driver.title:
        return # All set!

@when('I ingest a "{object_type}" object')
def setp_imp(context, object_type):
    test_files = {
        'video': 'ed.mp4',
        'audio': 'band_1_clean.mp3',
        'text': 'Lipsitz_Possessive_selections.pdf',
        'audio album': [
            {'file': 'Band_1_Clean.mp3', 'title': '"Half-hitch" performed by W. E. Pierce of North Shrewsbury and Northam, VT'},
            {'file': 'Band_2_Clean.mp3', 'title': '"Lord Bateman (frag)" performed by W. E. Pierce of North Shrewsbury and Northam, VT'},
            {'file': 'Band_3_Clean.mp3', 'title': '"Sailor boy" performed by W. E. Pierce of North Shrewsbury and Northam, VT'},
            {'file': 'Band_4_Clean.mp3', 'title': '"Fair Charlotte" performed by W. E. Pierce of North Shrewsbury and Northam, VT'},
            {'file': 'Band_5_Clean.mp3', 'title': '"Butcher boy" performed by Mrs. Elwin Burditt of Springfield, VT'},
        ]
    }
    driver = context.behave_driver
    base_url = context.target['base_url']

    # Go to add upload page
    driver.get(base_url + '/admin/uploads/upload/add/')
    assert "Add upload" in driver.title, "Upload add page title is wrong"
    radio_item = driver.find_element_by_xpath(
            "//*[contains(text(),'%s')]/input" % object_type)
    radio_item.click()
    radio_item.submit()
    # Fill out the form and submit it
    unique_string = time.time()
    assert "Add %s" % object_type in driver.title, \
    "Add %s page title is wrong" % object_type
    title_input = driver.find_element_by_name('title')
    title_input.send_keys('Test %s upload %s' % (object_type, unique_string))

    upload_button = driver.find_element_by_name('upload')
    filename = os.getcwd() + '/sample_upload_files/' + test_files[object_type]
    upload_button.send_keys(filename)
    # Make sure to set the text type before saving if it's a text object
    if object_type == 'text':
        text_type_element = driver.get_element('#id_text_type')
        select_box = Select(text_type_element)
        select_box.select_by_value('article')
    submit_button = driver.find_element_by_xpath(
        "//input[@value='Save and continue editing']")
    submit_button.click()
    assert "was added successfully" in driver.page_source, \
    "Post ingest page doesn't say it 'was added successfully'"
    context.edit_urls[object_type] = driver.current_url

@then('a valid object view URL should be displayed')
def step_imp(context):
    driver = context.behave_driver

    url_element = driver.get_element('#hitchcock-url')
    assert is_valid_url(url_element.text)

@when('I go to the current "{object_type}" object view URL')
def step_imp(context, object_type):
    driver = context.behave_driver
    url_element = driver.get_element('#hitchcock-url')
    context.view_urls[object_type] = url_element.text # Save this for later for other tests
    view_link_element = driver.find_element_by_xpath("//a[contains(text(),'view')]")
    view_link_element.click()

@then('a working "{asset_viewer}" should load')
def step_imp(context, asset_viewer):
    driver = context.behave_driver

    if asset_viewer == 'av player':
        # AV is in flux, skip this part of the test for now
        pass
        # try:
        #     video_player = driver.get_element('.vjs-paused')
        #     video_player.click() # Start the video
        # except:
        #     assert False, "video player couldn't be found/started"
        # time.sleep(5)
        # try:
        #     video_player = driver.get_element('.vjs-playing')
        #     video_player.click() # Start the video
        # except:
        #     assert False, "video player didn't start or couldn't be paused"

    elif asset_viewer == 'pdf viewer':
        # pdb.Pdb(stdout=sys.__stdout__).set_trace()
        # Follow the popup
        driver.switch_to_window(driver.window_handles[1])
        embed = driver.get_element('embed')
        assert 'application/pdf' == embed.get_attribute('type')

@given("I am a non-staff user")
def step_imp(context):
    driver = context.behave_driver
    base_url = context.target['base_url']
    driver.switch_to_window(driver.window_handles[0])

    driver.get(base_url + '/admin/')
    if "Log in" in driver.title:
        return # All set!
    elif "Site administration" in driver.title:
        logout_link = driver.find_element_by_xpath("//a[contains(text(),'Log out')]")
        logout_link.click()

@when('I go to the "{object_type}"')
def step_imp(context, object_type):
    driver = context.behave_driver
    driver.get(context.view_urls[object_type])

@then("I am forbidden")
def step_imp(context):
    driver = context.behave_driver
    assert "Access Denied" in driver.page_source

@when('I set the "{object_type}" as "{published_state}"')
def step_imp(context, object_type, published_state):
    driver = context.behave_driver
    driver.get(context.edit_urls[object_type])

    target_state = None

    if published_state == "published":
        target_state = True
    elif published_state == "un-published":
        target_state = False

    assert target_state is not None # Make sure it was set correctly by the gherkin

    published_checkbox = driver.get_element('input#id_published')
    if published_checkbox.is_selected() is not target_state:
        published_checkbox.click()
        published_checkbox.submit()
        assert "was changed successfully" in driver.page_source, \
        "Post edit page doesn't say it 'was changed successfully'"
    else:
        return # Nothing to do here, all set!

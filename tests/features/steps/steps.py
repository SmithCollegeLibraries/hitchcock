from behave import *
import time
import os
import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import sys, pdb

TEST_FILES = {
    'video': {
        'filename': 'ed.mp4',
        'title': "Test: Elephant's Dream",
        'captions': 'lear.vtt',
    },
    'audio': {
        'filename': 'band_1_clean.mp3',
        'title': 'Test: Half-hitch',
    },
    'text': {
        'filename': 'Lipsitz_Possessive_selections.pdf',
        'title': 'Test: Lipsitz - Possessive (selections)',
    },
}

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

@when('I ingest an object of type "{object_type}"')
def setp_imp(context, object_type):
    driver = context.behave_driver
    base_url = context.target['base_url']

    # Go to add upload page
    driver.get(base_url + f'/admin/uploads/{object_type}/add/')
    assert f"Add {object_type}" in driver.title, "Upload add page title is wrong"
    # Fill out the form and submit it
    unique_string = str(time.time())
    assert f"Add {object_type}" in driver.title, f"Add {object_type} page title is wrong"
    title_input = driver.find_element_by_name('title')
    title_input.send_keys(TEST_FILES[object_type]['title'] + ' ' + unique_string)

    upload_button = driver.find_element_by_name('upload')
    filename = os.getcwd() + '/sample_upload_files/' + TEST_FILES[object_type]['filename']
    upload_button.send_keys(filename)
    # Make sure to set the text type before saving if it's a text object
    if object_type == 'text':
        text_type_element = driver.get_element('#id_text_type')
        select_box = Select(text_type_element)
        select_box.select_by_value('article')
    # TODO: Include captions if it's a video object
    # elif object_type == 'video':
    #     vtt_upload_button = driver.find_element_by_xpath('//*[@id="id_vtttrack_set-0-upload"]')
    #     vtt_filename = os.getcwd() + '/sample_upload_files/' + TEST_FILES[object_type]['captions']
    #     vtt_upload_button.send_keys(vtt_filename)
    #     vtt_type_element = driver.get_element('#id_vtttrack_set-0-type')
    #     select_box = Select(vtt_type_element)
    #     select_box.select_by_value('captions')

    submit_button = driver.find_element_by_xpath(
        "//input[@value='Save and continue editing']")
    submit_button.click()
    assert "was added successfully" in driver.page_source, "Post ingest page doesn't say it 'was added successfully'"
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
    if object_type == 'video':
        time.sleep(300)
    elif object_type == 'audio':
        time.sleep(120)
    view_link_element.click()

@then('a working "{asset_viewer}" should load')
def step_imp(context, asset_viewer):
    driver = context.behave_driver

    if asset_viewer == 'av player':
        time.sleep(5)
        # TODO: Can we test for captions?

        panopto_header_title = driver.find_element_by_xpath('//*[@id="deliveryTitle"]')
        assert panopto_header_title == TEST_FILES[object_type]['title']

        try:
            panopto_play_button = driver.find_element_by_xpath('//*[@id="playButton"]')
            panopto_play_button.click()  # Start the video
            time.sleep(5)
            try:
                video_player.click()  # Stop the video
            except:
                assert False, "Video player couldn't be paused"
        except:
            assert False, "Video player couldn't be found/started"

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

    target_state = False if published_state == "un-published" else True

    published_checkbox = driver.get_element('input#id_published')
    if published_checkbox.is_selected() is not target_state:
        published_checkbox.click()
        published_checkbox.submit()
        assert "was changed successfully" in driver.page_source, \
        "Post edit page doesn't say it 'was changed successfully'"
    else:
        return  # Nothing to do here, all set!

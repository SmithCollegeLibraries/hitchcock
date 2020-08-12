from behave import *
import time
import os
import sys, pdb

def get_includes_text(driver, tag, text):
    element = driver.find_element_by_xpath(\
    "//%s[contains(text(),'%s')]" % (tag, text))
    return element

@given('I am logged in as a staff user')
def step_imp(context):
    driver = context.behave_driver
    base_url = context.target['base_url']

    driver.get(base_url + '/admin/')
    if "Log in" in driver.title:
        username_input = driver.find_element_by_name('username')
        username_input.send_keys('test_staff_user')
        password_input = driver.find_element_by_name('password')
        password_input.send_keys('opensesame')
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
    radio_item = driver.find_element_by_xpath(\
    "//*[contains(text(),'%s')]" % object_type)
    radio_item.click()
    radio_item.submit()
    # Fill out the form and submit it
    unique_string = time.time()
    assert "Add %s" % object_type in driver.title, \
    "Add %s page title is wrong" % object_type
    title_input = driver.find_element_by_name('title')
    title_input.send_keys('Test %s upload %s' % (object_type, unique_string))
    # pdb.Pdb(stdout=sys.__stdout__).set_trace()
    if object_type == 'audio album':
        track_num = 0
        for track in test_files['audio album']:
            add_track_button = get_includes_text(driver, 'a', \
            'Add another Audio track')
            add_track_button.click()
            choose_file_button = driver.find_element_by_name( \
            'audiotrack_set-%i-upload' % track_num)
            filename = test_files['audio album'][track_num]['file']
            filename = os.getcwd() + '/sample_upload_files/album/' + filename
            choose_file_button.send_keys(filename)
            title = test_files['audio album'][track_num]['title']
            title_input = driver.find_element_by_name( \
            'audiotrack_set-%i-title' % track_num)
            title_input.send_keys(title)
            track_num += 1
    else:
        upload_button = driver.find_element_by_name('upload')
        filename = os.getcwd() + '/sample_upload_files/' + test_files[object_type]
        upload_button.send_keys(filename)
    submit_button = driver.find_element_by_xpath(
        "//input[@value='Save and continue editing']")
    submit_button.click()
    assert "was added successfully" in driver.page_source, \
    "Post ingest page doesn't say it 'was added successfully'"
    context.edit_urls[object_type] = driver.current_url

@when('I go to the current "{object_type}" object URL')
def step_imp(context, object_type):
    driver = context.behave_driver
    url_element = driver.get_element('div.field-url div.readonly')
    url = url_element.text
    context.view_urls[object_type] = url # Save this for later for other tests
    driver.get(url)

@then('a working "{asset_viewer}" should load')
def step_imp(context, asset_viewer):
    driver = context.behave_driver

    if asset_viewer == 'av player':
        try:
            video_player = driver.get_element('.vjs-paused')
            video_player.click() # Start the video
        except:
            assert False, "video player couldn't be found/started"
        time.sleep(5)
        try:
            video_player = driver.get_element('.vjs-playing')
            video_player.click() # Start the video
        except:
            assert False, "video player didn't start or couldn't be paused"

    elif asset_viewer == 'pdf viewer':
        embed = driver.get_element('embed')
        assert 'application/pdf' == embed.get_attribute('type')

@given("I am a non-staff user")
def step_imp(context):
    driver = context.behave_driver
    base_url = context.target['base_url']

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
    assert "403 Forbidden" in driver.page_source

@when('I set the "{object_type}" as published')
def step_imp(context, object_type):
    driver = context.behave_driver
    driver.get(context.edit_urls[object_type])
    published_checkbox = driver.get_element('input#id_published')
    published_checkbox.click()
    published_checkbox.submit()
    assert "was changed successfully" in driver.page_source, \
    "Post edit page doesn't say it 'was changed successfully'"

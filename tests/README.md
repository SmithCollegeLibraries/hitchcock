The tests in `features/` are behavioral regression tests that use Selenium to
drive an instance of chrome.

The files in `sample_upload_files` are a handy set of assets that can be used
when creating test objects.

Test code assumes that there is a staff user account already registered in the
system called `test_staff_user` with a password `opensesame`.

To run behavioral regression tests:

``` bash
# in hitchcock/tests/
python3 -m venv venv
pip install -r requirements.text
# Download Chrome web driver and put it in your path
# https://chromedriver.chromium.org/downloads
behave
```

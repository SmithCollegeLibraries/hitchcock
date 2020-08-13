The tests in `features/` are behavioral regression tests that use Selenium to
drive an instance of chrome.

The files in `sample_upload_files` are a handy set of assets that can be used
when creating test objects.

Test code assumes that there is a user account already registered in the
system called `test_staff_user` with staff status and superuser status enabled. You must set a password for the test_staff_user account with the -D option like this `behave -D password=opensesame`.

To run behavioral regression tests:

``` bash
# in hitchcock/tests/
python3 -m venv venv
pip install -r requirements.text
# Download Chrome web driver and put it in your path
# https://chromedriver.chromium.org/downloads
behave -D password=CHANGEME
```

To specify a target environment use the -D flag to set the 'env' variable

``` bash
behave -D env=libsandbox -D password=CHANGEME
```

By default, 'local' is selected automatically.

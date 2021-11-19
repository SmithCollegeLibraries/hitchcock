Fixes issue in django-polymorphic causing the admin page to return give a 404
when site is configured to run on a subpath. Found while deploying to libsandbox.

https://github.com/django-polymorphic/django-polymorphic/issues/448

This bug should be fixed with django-polymorphic>=3.1.0, which is now in
the project requirements file.

This directory contains temporary patches to be applied to dependencies, that
have not yet been folded into upstream code.

Run this command as part of the setup procedure, from the project root dir:

``` bash
patches/apply_patches.sh
```

When changes have been merged into upstream code the module version number
should be upgraded in requirements.txt, and respective patch code removed from
this directory.

To add a new patch, create a new directory. Within that directory add a
README.md file with an explanation for why the patch exists. Include your patching
code in this directory. Then add a line to `apply_patches.sh`, to execute it.

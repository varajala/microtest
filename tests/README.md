## Tests

The microtest's internal test suite is divided into two sections:

  - unittests executed with Python's builtin unittest framework
  - bootsrapped tests executed with microtest


Assets directory contains tests that do some test disocvery.
These subdirectories are executed by the actual bootsrapped tests.

To execute all tests, just run the **tests/run.py** module.
It is a simple script that just executes the different test units automatically.

When adding new unittest files, add their name into the **UNITTEST_FILES** list in the **tests/run.py** module.

<br>

### Automatic documentation

After doing any changes to the source modules, run the following command:

    python -m microtest.docs [microtest/microtest] [microtest/docs/modules]

This command generates the automatically generated docs for the source modules.

The paths inside the brackets should be absolute filepaths, the first must point to
the folder where microtest.__init__ module is located. The second one must point
to the microtest/docs/modules folder.
This is the folder for the automatically generated docs.

When adding new modules, add a link to the right document to the docs/index.md

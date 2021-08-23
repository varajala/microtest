## Tests

The microtest's internal test suite is divided into two sections:

  - unittests executed with Python's builtin unittest framework
  - bootsrapped tests executed with microtest


Assets directory contains tests that do some test disocvery.
These subdirectories are executed by the actual bootsrapped tests.

To execute all tests, just run the **tests/run.py** module.
It is a simple script that just executes the different test units automatically.

When adding new unittest files, add their name into the **UNITTEST_FILES** list in the **tests/run.py** module.

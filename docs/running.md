Back to [docs](index.md)...

<br>

## Running

Microtest can be used to run tests automatically in two different ways. The first way is to use the **microtest.run** function and run the module normally as a script.

Let's revisit the example from the [basics](basics.md) section:

```python
import microtest


@microtest.test
def function():
    x = 10
    assert x < 0
    

if __name__ == '__main__':
    microtest.run()
```

This is the very simplest form of test suite you can create with microtest. When this module is ran from the command line normally with:

    python module.py

We get the following output:

```
======================================================================
Started testing...
======================================================================
function ..................................................... FAILED

AssertionError on line 7:
assert 10 < 0 


----------------------------------------------------------------------
Ran 1 tests in 0.001s.

ERRORS: 0
FAILED: 1
```

However it is preffered to run microtest as a module. We can execute the same file with the following command:

    python -m microtest module.py

This time we get the following output:

```
======================================================================
Started testing...
======================================================================

/home/varajala/dev/py/microtest/module.py
function ..................................................... FAILED

AssertionError on line 7:
assert 10 < 0 


----------------------------------------------------------------------
Ran 1 tests in 0.002s.

ERRORS: 0
FAILED: 1
```

As you can see there is not much of a difference when running only a single file.
This is becaus if the path points to a file, microtest will simply just execute that single module. This is not that different from executing the test module as a script.
However when running microtest whis way there are many internal things happening differently.

<br>

> **NOTE**: Microtest will expect the last command line argument to be the path to the tested file or directory. Microtest will use the current working directory if no arguments are provided.

<br>

When the path points to a directory rather than a single file, microtest test will perform the following steps:

  - look for a configuration script
  - execute the configuration script if one was found
  - look for test modules inside the directory structure
  - execute the found test modules

<br>

### Config script

First microtest will search for a config script. By default microtest will check the provided directory for a file called **main.py**.

This can be changed with an environment variable called **MICROTEST_ENTRYPOINT**. The entrypoint can be set to a relative or an absolute path.

If a config script is found it will be executed normally before any tests. This step is completely separate from the acrtual testing and any exceptions raised during the configuration will stop the program executing any further. You should not include any tests inside the config script.

See the [config](config.md) section for detailed documentation on the configuration step.

<br>

### Test discovery

After the config step microtest will search for the test modules.
This is done after the config phase so that you can set the rules for finding suitable test modules.

By default microtest will do a breadth-first-search starting from the provided directory path and include all python modules
which's name either

  - starts with **test_** or **tests_**
  - ends with **_test** or **_tests**
  - is equal to **test** or **tests**


This can be changed during the config phase.
It is also possible to filter modules by the path and test functions by adding them in a group. Again, more on this in the [config](config.md) section.

<br>

Modules are discovered using breadth-first-search. This means that modules higher in
the directory hierachy are excecuted before modules that are lower in the directory hierarchy.
**This can be relied on.**

Modules inside the same directory are executed in the order dependent on the underlying filesystem, they are not sorted in any way. **You should not rely on any particular order of execution of modules inside the same directory**.

If some of your test modules rely on resources or utilites to be available when executed,
place them into some subdirectory. This will guarantee that the module higher in the directory
hierarchy that defines the needed entities is executed first.

<br>

### Running all tests inside a directory

Let's take a look on how the output looks when executing tests inside a directory structure. As an example here's a test directory of a Flask application I have built:

```
tests
├── account_verification_tests.py
├── api
│   ├── login_tests.py
│   ├── registering_tests.py
│   └── verification_tests.py
├── extension_loading_test.py
├── jwt_tests.py
├── login_tests.py
├── main.py
├── notifications_tests.py
├── otp_tests.py
├── registering_tests.py
└── validation_tests.py
```

Notice that there is a file called **main.py**. This is the config script as mentioned earlier. It sets up the Flask application and other resources that multiple test modules might use.

Now lets run the tests with the command:

    python -m microtest tests


Here's how the output looks:

```
=====================================================================
Started testing...
=====================================================================

/home/varajala/dev/auth_server/tests/account_verification_tests.py
test_valid_account_verification ................................. OK
test_typechecking ............................................... OK
test_invalid_email .............................................. OK

/home/varajala/dev/auth_server/tests/extension_loading_test.py
test_querying ................................................... OK

/home/varajala/dev/auth_server/tests/otp_tests.py
test_generating_otps ............................................ OK
test_correct_otp_validation ..................................... OK
test_expired_otp_validation ..................................... OK
test_wrong_otp_validation ....................................... OK
test_invalid_otp_validation ..................................... OK

/home/varajala/dev/auth_server/tests/login_tests.py
test_typechecking ............................................... OK
test_valid_login ................................................ OK
test_login_invalid_email ........................................ OK
test_login_invalid_password ..................................... OK
test_login_account_not_verified ................................. OK

/home/varajala/dev/auth_server/tests/jwt_tests.py
test_token_generation ........................................... OK
test_token_decoding ............................................. OK
test_correct_signature_validation ............................... OK
test_incorrect_signature_validation ............................. OK
test_expired_signature_validation ............................... OK
test_validation_with_invalid_json_types ......................... OK
test_decoding_invalid_token_string .............................. OK
test_decoding_token_with_non_b64_chars .......................... OK
test_decoding_token_with_no_json ................................ OK
test_generating_access_tokens ................................... OK
test_generating_refresh_tokens .................................. OK
test_passing_extended_validation ................................ OK
test_failing_extended_validation_via_invalid_context ............ OK
test_failing_extended_validation_via_invalid_token .............. OK

/home/varajala/dev/auth_server/tests/validation_tests.py
test_valid_emails ............................................... OK
test_invalid_emails ............................................. OK
test_valid_passwords ............................................ OK
test_invalid_passwords .......................................... OK
test_valid_urls ................................................. OK
test_invalid_urls ............................................... OK
test_valid_client_names ......................................... OK
test_invalid_client_names ....................................... OK

/home/varajala/dev/auth_server/tests/notifications_tests.py
test_email_sending .............................................. OK
test_writing_email_to_file ...................................... OK

/home/varajala/dev/auth_server/tests/registering_tests.py
test_typechecking ............................................... OK
test_valid_registering .......................................... OK
test_registering_invalid_email .................................. OK
test_registering_email_in_user .................................. OK
test_registering_invalid_password ............................... OK
test_registering_invalid_password_confirm ....................... OK

/home/varajala/dev/auth_server/tests/api/login_tests.py
test_valid_login ................................................ OK
test_login_with_valid_refresh_token ............................. OK
test_login_with_invalid_refresh_token ........................... OK
test_login_with_invalid_client_uuid ............................. OK
test_login_with_invalid_credentials ............................. OK
test_login_with_invalid_json_types .............................. OK

/home/varajala/dev/auth_server/tests/api/registering_tests.py
test_valid_registering .......................................... OK
test_invalid_request_json ....................................... OK

/home/varajala/dev/auth_server/tests/api/verification_tests.py
test_valid_verification ......................................... OK
test_invalid_request_json ....................................... OK

---------------------------------------------------------------------
Ran 54 tests in 2.414s.

OK.

```

As you can see microtest found all python modules matching the default regex and executed all tests inside them. The default output displays all executed modules and the single tests inside them.

<br>

Back to [docs](index.md)...
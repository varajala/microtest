# microtest
Simple but powerful testing framework for Python.

<br>

## Installation

    python -m pip install microtest-framework

<br>

## Usage

Here's the simplest testing program you can create with microtest:
```python
import microtest


@microtest.test
def function():
    x = 10
    assert x < 0
    

if __name__ == '__main__':
    microtest.run()
```
You can run this script normally via the command line:

    python test.py

The script will produce the following output:

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

See the full microtest documentation [here](docs/index.md) for user guide and refrence of the source modules.

<br>

## Contributing

To contribute new features to this project do the following steps:

  - Open a new issue explaining the new feature
  - Wait for approval
  - Fork and clone the repository t your local machine and code up the feature in a **new branch**
  - Pull request

The *wait for approval* step is there so that you don't end up coding up some feature that might
not be included into microtest. This could happen if the proposed feauture is redundant, changes the
existing api too radically, or simply just is not the *right thing* to be added into microtest.

The goal is to keep this project simple and small.

**Bug fixes, documentation improvements and other minnor tweaks are always welcome, no need for approval here.**

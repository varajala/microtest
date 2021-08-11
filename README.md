# microtest
Simple but powerful testing utilities for Python.

<br>

## Installation

To install microtest download and unpack the zip folder with the source code, or fork and clone this project to a local repository. After this navigate to the toplevel directory where the **setup.py** - file is located and install the package with pip.

    python -m pip install .

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

See the full microtest documentation [here](docs/index.md) for complete refrence anduser guide.

<br>

## Contributing

Instructions here...

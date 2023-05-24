Installation
============

All installation of the ``hyswap`` package must, at this time, be done
**from source**. Here we provide instructions on how to do this, including
both a "user" installation with minimal dependencies, as well as a "developer"
installation that is "editable" and contains all of the dependencies needed
to run the tests and build the package documentation.


User Installation
-----------------

Below are the commands to install the ``hyswap`` package from source
as a user. This installation will be static, and reflect the version of the
package as it was at the time the code was downloaded.

.. code-block:: bash

    git clone https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap.git
    cd hyswap
    pip install -r requirements.txt
    pip install .


Developer Installation
----------------------

Below are the commands to install the ``hyswap`` package from source
as a developer. This installation will be "editable", meaning that any
changes made to the source code will be reflected in the installed package
without the need to reinstall. This installation will also contain all of the
dependencies needed to run the tests and build the documentation.

.. code-block:: bash

    git clone https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap.git
    cd hyswap
    pip install -r requirements-dev.txt
    pip install -e .

Once the installation is complete, the suite of tests can be run with a single
command in the console:

.. code-block:: bash

    pytest

The documentation can be built locally with the following commands:

.. code-block:: bash

    cd docs
    make docs

To run the linting and formatting checks locally, run the following commands
from the root of the repository:

.. code-block:: bash

    flake8 .
    pydocstringformatter .

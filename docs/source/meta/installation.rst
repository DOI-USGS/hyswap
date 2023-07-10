Installation
============

Installation instructions for the ``hyswap`` package are provided below.
We provide instructions on recommended "user" installations with minimal dependencies, as well as how to install the package as a "developer" such that it is is "editable" and contains all of the dependencies needed to run the tests and build the package documentation.


User Installation
-----------------

Below are two recommended installation methods for users of the ``hyswap`` package.


Installation via ``pip``
^^^^^^^^^^^^^^^^^^^^^^^^

``hyswap`` is hosted on `pypi <https://pypi.org/project/hyswap/>`_ and can therefore be installed using ``pip``.
This can be done with the following command:

.. code-block:: bash

    pip install hyswap

It is possible to specify the specific version of the package you'd like to install with a command like:

.. code-block:: bash

    pip install hyswap==0.0.1


Installation from source
^^^^^^^^^^^^^^^^^^^^^^^^

Below are the commands to install the ``hyswap`` package from source as a user.
This installation will be static, and reflect the version of the package as it was at the time the code was downloaded.

.. code-block:: bash

    git clone https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap.git
    cd hyswap
    pip install -r requirements.txt
    pip install .


Developer Installation
----------------------

Below are the commands to install the ``hyswap`` package from source as a developer.
This installation will be "editable", meaning that any changes made to the source code will be reflected in the installed package without the need to reinstall.
This installation will also contain all of the dependencies needed to run the tests and build the documentation.

.. code-block:: bash

    git clone https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap.git
    cd hyswap
    pip install -r requirements-dev.txt
    pip install -e .

Once the installation is complete, the suite of unit tests can be run with a single command in the console:

.. code-block:: bash

    pytest

The documentation can be built and tested locally with the following commands:

.. code-block:: bash

    cd docs
    make docs


For a faster local documentation build you can skip running the documentation tests by running ``make html`` instead of ``make docs``.

To run the linting and formatting checks locally, run the following commands from the root of the repository:

.. code-block:: bash

    flake8 .
    pydocstringformatter .

# hyswap

[![USGS-category-image](https://img.shields.io/badge/USGS-Core-green.svg)](https://owi.usgs.gov/R/packages.html#core)
[![pipeline-status-image](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/badges/main/pipeline.svg)](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/commits/main)
[![coverage-report-image](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/badges/main/coverage.svg)](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/commits/main)

### Project Documentation

`hyswap` documentation is available at: [Link](https://rconnect.usgs.gov/hyswap-docs/html/)

## Installation

### User Installation

User installation is possible from source right now.
First you will need to clone the repository.
Next, from the root of the repository, run the following commands:

```bash
pip install -r requirements.txt
pip install .
```

### Developer Installation

Developer installation is possible from source right now.
First you will need to clone the repository.
Next, from the root of the repository, run the following commands:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### Testing and Building Documentation Locally

To test the package locally, run the following command from the root of the repository:

```bash
pytest
```

To build the documentation locally, run the following commands from the root of the repository:

```bash
cd docs
make docs
```

### Running the Linting and Formatting Checks Locally

To run the linting and formatting checks locally, run the following commands from the root of the repository:

```bash
flake8 .
pydocstringformatter .
```

## Contributing

See the [contributing guidelines](CONTRIBUTING.md) for more information.

## License

See the [license](LICENSE.md) for more information.

## Disclaimer

See the [disclaimer](DISCLAIMER.md) for more information.

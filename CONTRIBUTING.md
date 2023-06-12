# Contributing Guidelines

Contributions to `hyswap` are welcome and greatly appreciated, please read this document for information on how to contribute.

Code contributions can be made using a "branching" or a "fork-and-branch" ("forking") workflow.
The branching workflow is the simplest and easiest to understand, but it requires write access to the repository.
The forking workflow is marginally more complex, but it allows contributors to work on their own fork of the repository.
The forking workflow is the recommended workflow for external contributors.
Read more about the differences between the two workflows [here](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow).

---

## Table of Contents

- [Contributing Guidelines](#contributing-guidelines)
  - [Table of Contents](#table-of-contents)
  - [Bugs](#bugs)
    - [Reporting Bugs](#reporting-bugs)
    - [Fixing Bugs](#fixing-bugs)
  - [Code Contributions](#code-contributions)
    - [Implementing Features](#implementing-features)
    - [Pull Request Guidelines](#pull-request-guidelines)
    - [Coding Standards and Style](#coding-standards-and-style)
      - [Style](#style)
      - [Doc-strings](#doc-strings)
  - [Documentation](#documentation)
    - [Contributing to the Documentation](#contributing-to-the-documentation)
  - [Feedback and Feature Requests](#feedback-and-feature-requests)
    - [Submitting Feedback](#submitting-feedback)
    - [Feature Requests](#feature-requests)
  - [Merge Workflow (USGS Maintainers)](#merge-workflow-usgs-maintainers)
    - [Contributions on GitLab](#contributions-on-gitlab)
    - [Contributions on GitHub](#contributions-on-github)
  - [Acknowledgements](#acknowledgements)

---

## Bugs

### Reporting Bugs

Report bugs at https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/issues.

When reporting a bug, please include:

* Detailed steps to reproduce the bug
* Your operating system name and version
* The Python version, as well as information about your local Python environment, such as the versions of installed packages
* Any additional details about your local setup that might be helpful in troubleshooting

**Conda Users:** If you are using conda, please include the output of `conda list`.

### Fixing Bugs

Look through the [issues](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/issues) for known and unresolved bugs.
Any unassigned issues, are open for resolution.
You are welcome to comment in the relevant issue to state your intention to resolve the bug, which will help ensure there is no duplication of the same work by multiple contributors.
Once you begin work on a given issue, you are welcome to open up a *Draft* pull request to track your progress and to allow for early feedback.

---

## Code Contributions

Code contributions can be made using a "branching" or a "fork-and-branch" (or "forking") workflow.
In the "branching" workflow, you clone the repository, create a new feature branch to add your changes, and then open a pull request from your feature branch to the "main" branch.
In the "forking" workflow, you clone the repository, create a new feature branch in your fork, and then open a pull request from your feature branch to the "main" branch of the original repository.

### Implementing Features

Look through the [issues](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/issues) for outstanding feature requests.
Please do not combine multiple feature enhancements into a single pull request.

### Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. If the pull request adds or modifies package functionality, unit tests should be written to test the new functionality
2. If the pull request adds or modifies functionality, the documentation should be updated. To do so, either add or modify a functions docstring which will automatically become part of the API documentation
3. The pull request should work for the versions of Python being tested by the continuous integration pipelines, see the [.gitlab-ci.yml file](https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/blob/main/.gitlab-ci.yml).
   This will be checked automatically by the CI pipelines once the pull request is opened.

### Coding Standards and Style

Note that the CI pipelines will automatically check your code for style and formatting issues following the [PEP8 style guidelines](https://peps.python.org/pep-0008/).
Before merging, your code must pass all of the CI pipelines.

#### Style

* Write code following the [PEP8 style guidelines](https://peps.python.org/pep-0008/)

#### Doc-strings
* Docstrings should follow the [numpy standard](https://numpydoc.readthedocs.io/en/v1.5.0/format.html):
  * Example:
    ``` python
    def foo(param1, param2):
    """Example function with types documented in the docstring.

    A more detailed description of the function and its implementation.

    Parameters
    ----------
    param1 : int
        The first parameter.
    param2 : str
        The second parameter.

    Returns
    -------
    bool
        True if successful, False otherwise.

    Examples
    --------
    Examples should be written in doctest format and should demonstrate basic usage.

    >>> foo(1,'bar')
    True

    """
    ```
  * For more details see https://github.com/sphinx-doc/sphinx/blob/master/doc/ext/example_numpy.py

---

## Documentation

### Contributing to the Documentation

Documentation is built using [sphinx](https://www.sphinx-doc.org/en/master/), and is located within the `docs/source/` subdirectory in the repository.
Documentation is written using [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html).

Contributions to the documentation should be made in a similar fashion to code contributions - by following a forking workflow.
When opening a pull request please be sure to have tested your documentation modifications locally, and clearly describe what it is your proposed changes add or fix.

---

## Feedback and Feature Requests

### Submitting Feedback

The best way to send feedback is to open an issue at https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/issues.

Please be as clear as possible in your feedback, if you are reporting a bug refer to [Reporting Bugs](#reporting-bugs).

### Feature Requests

To request or propose a new feature, open an issue at https://code.usgs.gov/water/computational-tools/surface-water-work/hyswap/-/issues.

Please be sure to:
* Explain in detail how it would work, possibly with pseudo-code or an example use-case
* Keep the scope of the proposed feature as narrow as possible
* Make clear whether you would like to implement this feature, you need help devising the implementation, or you are unable to implement the feature yourself but would like it as a user

---

## Merge Workflow (USGS Maintainers)

This code repository exists (and is publicly available) on both the USGS GitLab platform (code.usgs.gov) and within the DOI-USGS organization on GitHub (github.com/DOI-USGS).
The canonical 'source' repository is on GitLab, all commits on all branches are automatically mirrored from the GitLab repository to the GitHub repository.
To maintain this mirroring and keep the two repositories *exactly* the same (i.e., identical commit histories), there is a specific workflow that must be followed when merging contributions to the project.

Whether contributions are made via GitLab or GitHub, they should follow the code contribution guidelines outlined above.
Below, the specific steps that should be taken to merge or integrate these contributions into the `hyswap` project are outlined.

### Contributions on GitLab
When contributions are proposed on GitLab via merge requests, they can be discussed, altered, and ultimately merged on that platform.
There is no special action that needs to be taken on behalf of the code maintainers and developers in this case.

### Contributions on GitHub
When contributions are proposed on GitHub via pull requests, the review and discussion of the changes can take place within the pull request as usual.
However, **the pull request cannot be merged on GitHub**, as this throws off the automatic mirroring which goes from GitLab to GitHub.
Once a pull request has been reviewed and "approved" on GitHub, a USGS code maintainer or developer (someone with push access to the GitLab repository) has to take action to **push the proposed code to GitLab**.
This process involves the maintainer having a local clone of the `hyswap` project with remote connections to both the GitLab and GitHub repositories.
Locally, the maintainer has to checkout the proposed code from the approved pull request on GitHub.
Then they can push those changes to the *GitLab* repository by specifying the remote repository and "main" branch on GitLab.
Once the changes are pushed to GitLab, they will be automatically mirrored back to GitHub.
In this process, the GitHub pull request will get closed, and the code commits will be credited to the appropriate authors on GitHub too, all while maintaining the mirror and keeping the GitHub and GitLab repositories identical.

---

## Acknowledgements
This document was adapted from the `cookiecutter` project's [CONTRIBUTING file](https://github.com/audreyr/cookiecutter/blob/master/CONTRIBUTING.rst) and the `dataretrieval` project's [CONTRIBUTING file](https://github.com/DOI-USGS/dataretrieval-python/blob/master/CONTRIBUTING.md).

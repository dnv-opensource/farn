# Changelog

All notable changes to the [farn] project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Dependencies
* updated to ruff==0.5.1  (from ruff==0.4.2)
* updated to pyright==1.1.371  (from pyright==1.1.360)
* updated to setup-python@v5  (from setup-python@v4)
* updated to actions-gh-pages@v4  (from actions-gh-pages@v3)
* updated to upload-artifact@v4  (from upload-artifact@v3)

* -/-


## [0.3.7] - 2024-05-22

### Dependencies
* updated to ruff==0.4.2  (from ruff==0.2.1)
* updated to pyright==1.1.360  (from pyright==1.1.350)
* updated to sourcery==1.16  (from sourcery==1.15)
* updated to lxml>=5.2  (from lxml>=5.1)
* updated to types-lxml>=2024.4  (from types-lxml>=5.1)
* updated to scipy>=1.13  (from scipy>=1.12)
* updated to Pillow>=10.3  (from Pillow>=10.2)
* updated to pytest>=8.2  (from pytest>=7.4)
* updated to pytest-cov>=5.0  (from pytest-cov>=4.1)
* updated to Sphinx>=7.3  (from Sphinx>=7.2)
* updated to sphinx-argparse-cli>=1.15  (from sphinx-argparse-cli>=1.11)
* updated to myst-parser>=3.0  (from myst-parser>=2.0)
* updated to furo>=2024.4  (from furo>=2023.9.10)
* updated to dictIO>=0.3.4  (from dictIO>=0.3.3)
* updated to ospx>=0.2.14  (from ospx>=0.2.13)
* updated to numpy>=1.26,<2.0  (from numpy>=1.26)
* updated to matplotlib>=3.9  (from matplotlib>=3.8)
* removed black

### Changed
* replaced black formatter with ruff formatter
* Changed publishing workflow to use OpenID Connect (Trusted Publisher Management) when publishing to PyPI
* Updated copyright statement
* VS Code settings: Turned off automatic venv activation

### Added
* `farn.core.case.Case`: Added method `add_parameters()`, which allows to manually add user-defined parameters to a Case.


## [0.3.6] - 2024-02-21

### Added
* README.md : Under `Development Setup`, added a step to install current package in "editable" mode, using the pip install -e option.
This removes the need to manually add /src to the PythonPath environment variable in order for debugging and tests to work.

### Removed
* VS Code settings: Removed the setting which added the /src folder to PythonPath. This is no longer necessary. Installing the project itself as a package in "editable" mode, using the pip install -e option, solves the issue and removes the need to manually add /src to the PythonPath environment variable.

### Changed
* Moved all project configuration from setup.cfg to pyproject.toml
* Moved all tox configuration from setup.cfg to tox.ini.
* Moved pytest configuration from pyproject.toml to pytest.ini
* Deleted setup.cfg

### Dependencies
* updated to black[jupyter]==24.1  (from black[jupyter]==23.12)
* updated to version: '==24.1'  (from version: '==23.12')
* updated to ruff==0.2.1  (from ruff==0.1.8)
* updated to pyright==1.1.350  (from pyright==1.1.338)
* updated to sourcery==1.15  (from sourcery==1.14)
* updated to lxml>=5.1  (from lxml>=4.9)
* updated to scipy>=1.12  (from scipy>=1.11)
* updated to pandas>=2.2  (from pandas>=2.1)
* updated to Pillow>=10.2  (from Pillow>=10.1)

* -/-


## [0.3.5] - 2024-01-09

### Changed

* farn/sampling/sampling.py:
  * _generate_values_using_uniform_lhs_sampling():
    replaced SALib latin with pyDOE2 lhs
  * _generate_values_using_sobol_sampling():
    replaced sobol-seq with scipy.stats.qmc.sobol
  * removed orphaned _cov argument from normalLhs sampling

### Dependencies

* Upgraded from pyDOE2>=1.3 to pyDOE3>=1.0
* Removed SALib and sobol-seq
* Updated to dictIO>=0.3.1 and ospx>=0.2.12
* Updated other dependencies to latest versions


## [0.3.4] - 2023-09-25

### Dependencies

* Updated dependencies to latest versions


## [0.3.3] - 2023-06-22

### Changed

* Modularized GitHub workflows
* Changed default Python version in GitHub workflows from 3.10 to 3.11

### Dependencies

* updated to dictIO>=0.2.8 and ospx>=0.2.10
* requirements-dev.txt: Updated dependencies to latest versions


## [0.3.2] - 2023-05-04

### Changed

* dependencies: updated dependencies to latest versions


## [0.3.1] - 2023-01-11

### Changed

* Added missing DocStrings for public classes, methods and functions
* Changed links to package documentation to open README.html, not the default index page
* data classes: changed initialisation of mutable types to use default_factory
* ruff: added rule-set "B" (flake8-bugbear)

### Dependencies

* updated to dictIO>=0.2.6 and ospx>=0.2.8


## [0.3.0] - 2023-01-09

v0.3.0 is a major update comprising one breaking change (see below).
Users are encouraged to update to this version.

### Breaking Change

* Moved classes 'Case' and 'Parameter' from farn.farn to farn.core <br>
  As a consequence, if you imported these classes in your code, you need to
  adapt the respective  import statements. I.e. <br>
  old
  ~~~py
  from farn.farn import Case, Parameter
  ~~~
  new
  ~~~py
  from farn.core import Case, Parameter
  ~~~

### Added

* Added a 'Cases' class, acting as a container for Case instances.
  Cases inherits from List[Case] and can hence transparently be used as a Python list type.
  However, Cases provides additional convenience methods to export the attributes of all contained Case instances to a pandas DataFrame (Cases.to_pandas()) or to a numpy ndarray (Cases.to_numpy()) <br><br>
  Cases is located in the farn.core sub-package and can be imported from there, i.e:
  ~~~py
  from farn.core import Case, Cases, Parameter
  ~~~


## [0.2.7] - 2023-01-04

### Changed

* Linter: Migrated from flake8 to ruff. <br>
  (Added ruff; removed flake8 and isort)
* Adjusted GitHub CI workflow accordingly. <br>
  (Added ruff job; removed flake8 and isort jobs)
* VS Code settings: Adjusted Pylance configuration

### Added

* Added a batch file 'qa.bat' in root folder to ease local execution of code quality checks

### Dependencies

* updated to dictIO>=0.2.5 and ospx>=0.2.7


## [0.2.6] - 2022-12-12

### Dependencies

* updated to ospx>=0.2.6

## [0.2.5] - 2022-12-12

### Changed

* Moved dev-only dependencies from requirements.txt to requirements-dev.txt
* farn/`__init__`.py : ensured that imported symbols get also exported <br>
  (added "as" clause -> "from x import y as y" instead of only "from x import y")
* sampling.py: refactored for cleaner code
* Configured code quality tools flake8, black, isort, pyright
* Improved code quality, resolving all warnings and errors flagged by the configured code quality tools
  (flake8, black, isort, pyright, sourcery)

### Added

* Added GitHub workflow 'main.yml' for continuous integration (runs all CI tasks except Sphinx)
    * format checks: black, isort
    * lint check: flake8, flake8-bugbear
    * type check: pyright
    * test: uses tox to run pytest on {Windows, Linux, MacOS} with {py39, py310}
    * publish: publishing to PyPI (runs only on push of new tag vx.x.x, and after all other jobs succeeded)
    * merge_to_release_branch: merge tagged commit to release branch (runs after publish)

### Dependencies

* updated to dictIO>=0.2.4

## [0.2.4] - 2022-12-01

### Changed

* Code formatting: Changed from yapf to black
* STYLEGUIDE.md : Adjusted to match black formatting
* VS Code settings: Updated to use black as formatter
* requirements.txt: Updated dependencies to their most recent versions
* GitHub actions (yml files): Updated following actions to their most recent versions:
    * checkout@v1 -> checkout@v3
    * setup-python@v2 -> setup-python@v4
    * cache@v2 -> cache@v3

### Added

* Added sourcery configuration (.sourcery.yaml)
* Added py.typed file into the package root folder and included it setup.cfg as package_data

## [0.2.3] - 2022-11-08

### Changed

* sampling.py: sampling adapted, removed unused (and non-preferable) options

* dependencies:
    * upgraded to dictIO >= 0.2.2  (now supporting references and expressions in JSON dicts)
    * upgraded to ospx >= 0.2.4
    * changed from pyDOE>=0.3.8 to pyDOE2>=1.3.0


## [0.2.2] - 2022-10-05

### Changed

* dependencies:
    * upgraded to ospx >= 0.2.3


## [0.2.1] - 2022-10-01

### Changed

* dependencies:
    * upgraded to dictIO >= 0.2.0
    * upgraded to ospx >= 0.2.1


## [0.2.0] - 2022-09-28

### Changed

* Dependencies:
    * upgraded to ospx >= 0.2.0
    * upgraded to dictIO >= 0.1.2

## [0.1.2] - 2022-08-19

### Changed

* farn.py:
    * create_samples(): Removed undocumented return value 'layers'. This was simply wrong. create_samples() is not meant to return anything.

* subProcess.py:
    * Changed level of 'per case' log messages from INFO to DEBUG, to reduce cluttering of log.

### Added

* farn CLI (and farn.run_farn() API):
    * EXPERIMENTAL FEATURE: Added --batch option. Default is False. The batch option lets farn execute commands in batch mode, i.e. asynchroneous instead of sequential.

### Fixed

* sampling.py:
    * uniformLhs sampling: Corrected the BoundingBox code for the case where Lhs sampling is requested with only one single parameter varied (i.e. 1-dimensional Lhs)

* farn.py:
    * Additional log file handler for farn gets registered only once. Multiple calls to _configure_additional_logging_handler_exclusively_for_farn() will not create multiple handlers, if the file handler for the log file already exists.

## [0.1.1] - 2022-05-30

### Changed

* Sphinx documentation: Added Changelogs (for combined documentation)
* updated dependency ospx to version >=0.1.1

## [0.1.0] - 2022-05-28

### Changed

* Simplified imports from namespace farn. Example:
    * Old (<= v0.0.22):
        ~~~py
        from farn.farn import run_farn
        ~~~
    * New:
        ~~~py
        from farn import run_farn
        ~~~
* Use new simplified imports from namespace dictIO (using updated version of dictIO package)

* farn.py
    * Renamed following functions:
        * run_sampling() -> create_samples()
        * generate_samples_for_layer() -> create_samples_in_layer()
        * register_cases() -> create_cases()
        * generate_case_folder_structure() -> create_case_folders()
        * generate_case_lists() -> create_case_list_files()
        * _create_param_dict_file_in_case_folders() -> create_param_dict_files()
        * _execute_command_set_in_case_folders() -> execute_command_set()
    * Introduced Dataclass 'Parameter'
    * Removed method add_uservars() in dataclass Case (moved the respective code into create_cases() )
    * run_farn(): Removed the ignore_errors argument
    * farnDict '_samples' section -> changed  naming of '_names' element to '_case_name', to improve clarity of its meaning
    * Smaller refactorings to improve code clarity and testability

* cli/farn.py
    * Removed the -i / --ignore-errors argument


## [0.0.22] - 2022-05-09

* First public release

## [0.0.17] - 2022-02-14

### Added

* Added support for Python 3.10

<!-- Markdown link & img dfn's -->
[unreleased]: https://github.com/dnv-opensource/farn/compare/v0.3.7...HEAD
[0.3.7]: https://github.com/dnv-opensource/farn/compare/v0.3.6...v0.3.7
[0.3.6]: https://github.com/dnv-opensource/farn/compare/v0.3.5...v0.3.6
[0.3.5]: https://github.com/dnv-opensource/farn/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/dnv-opensource/farn/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/dnv-opensource/farn/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/dnv-opensource/farn/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/dnv-opensource/farn/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/dnv-opensource/farn/compare/v0.2.7...v0.3.0
[0.2.7]: https://github.com/dnv-opensource/farn/compare/v0.2.6...v0.2.7
[0.2.6]: https://github.com/dnv-opensource/farn/compare/v0.2.5...v0.2.6
[0.2.5]: https://github.com/dnv-opensource/farn/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/dnv-opensource/farn/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/dnv-opensource/farn/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/dnv-opensource/farn/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/dnv-opensource/farn/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/dnv-opensource/farn/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/dnv-opensource/farn/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/dnv-opensource/farn/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/dnv-opensource/farn/compare/v0.0.22...v0.1.0
[0.0.22]: https://github.com/dnv-opensource/farn/compare/v0.0.17...v0.0.22
[0.0.17]: https://github.com/dnv-opensource/farn/releases/tag/v0.0.17
[farn]: https://github.com/dnv-opensource/farn

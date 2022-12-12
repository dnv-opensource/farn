# Changelog

All notable changes to the [farn] project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

* --


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
[unreleased]: https://github.com/dnv-opensource/farn/compare/v0.2.5...HEAD
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

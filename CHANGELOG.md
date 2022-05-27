# Changelog

All notable changes to the [farn] project will be documented in this file.<br>
The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

* -

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
[unreleased]: https://github.com/dnv-opensource/farn/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dnv-opensource/farn/compare/v0.0.22...v0.1.0
[0.0.22]: https://github.com/dnv-opensource/farn/compare/v0.0.17...v0.0.22
[0.0.17]: https://github.com/dnv-opensource/farn/releases/tag/v0.0.17
[farn]: https://github.com/dnv-opensource/farn

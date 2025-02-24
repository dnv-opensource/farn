[![pypi](https://img.shields.io/pypi/v/ospx.svg?color=blue)](https://pypi.python.org/pypi/ospx)
[![versions](https://img.shields.io/pypi/pyversions/ospx.svg?color=blue)](https://pypi.python.org/pypi/ospx)
[![license](https://img.shields.io/pypi/l/ospx.svg)](https://github.com/dnv-opensource/ospx/blob/main/LICENSE)
![ci](https://img.shields.io/github/actions/workflow/status/dnv-opensource/ospx/.github%2Fworkflows%2Fnightly_build.yml?label=ci)
[![docs](https://img.shields.io/github/actions/workflow/status/dnv-opensource/ospx/.github%2Fworkflows%2Fpush_to_release.yml?label=docs)][ospx_docs]

# ospx
ospx is an extension package to [farn][farn_docs], adding support to build [OSP][osp_docs] (co-)simulation cases using functional mockup units (FMUs).

ospx supports
* building of case-specific [OSP][osp_docs] (co-)simulation configuration files
* watching the progress of cosim, and saving final simulation results as a pandas dataframe.

## Installation

```sh
pip install ospx
```
ospx requires the following (sub-)package:
* [dictIO][dictIO_docs]: foundation package, enabling ospx to handle configuration files in dictIO dict file format.

However, dictIO gets installed automatically with ospx.

## Usage Example

ospx provides both an API for use inside Python as well as a CLI for shell execution of core functions.

Reading a caseDict file and building the case-specific OSP (co-)simulation configuration files:
```py
from ospx import OspCaseBuilder

OspCaseBuilder.build('caseDict')
```

The above task can also be invoked from the command line, using the 'ospCaseBuilder' command line script installed with ospx:
```sh
ospCaseBuilder caseDict
```

_For more examples and usage, please refer to [ospx's documentation][ospx_docs]._

## File Format
A caseDict is a file in dictIO dict file format used with farn.

_For a documentation of the caseDict file format, see [File Format](fileFormat.rst) in [ospx's documentation][ospx_docs] on GitHub Pages._

_For a detailed documentation of the dictIO dict file format used by farn, see [dictIO's documentation][dictIO_docs] on GitHub Pages._

## Development Setup

### 1. Install uv
This project uses `uv` as package manager.
If you haven't already, install [uv](https://docs.astral.sh/uv), preferably using it's ["Standalone installer"](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2) method: <br>
..on Windows:
```sh
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
..on MacOS and Linux:
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
(see [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) for all / alternative installation methods.)

Once installed, you can update `uv` to its latest version, anytime, by running:
```sh
uv self update
```

### 2. Install Python
This project requires Python 3.10 or later. <br>
If you don't already have a compatible version installed on your machine, the probably most comfortable way to install Python is through `uv`:
```sh
uv python install
```
This will install the latest stable version of Python into the uv Python directory, i.e. as a uv-managed version of Python.

Alternatively, and if you want a standalone version of Python on your machine, you can install Python either via `winget`:
```sh
winget install --id Python.Python
```
or you can download and install Python from the [python.org](https://www.python.org/downloads/) website.

### 3. Clone the repository
Clone the ospx repository into your local development directory:
```sh
git clone https://github.com/dnv-opensource/ospx path/to/your/dev/ospx
```
Change into the project directory after cloning:
```sh
cd ospx
```

### 4. Install dependencies
Run `uv sync` to create a virtual environment and install all project dependencies into it:
```sh
uv sync
```
> **Note**: Using `--no-dev` will omit installing development dependencies.

> **Note**: `uv` will create a new virtual environment called `.venv` in the project root directory when running
> `uv sync` the first time. Optionally, you can create your own virtual environment using e.g. `uv venv`, before running
> `uv sync`.

### 5. (Optional) Activate the virtual environment
When using `uv`, there is in almost all cases no longer a need to manually activate the virtual environment. <br>
`uv` will find the `.venv` virtual environment in the working directory or any parent directory, and activate it on the fly whenever you run a command via `uv` inside your project folder structure:
```sh
uv run <command>
```

However, you still _can_ manually activate the virtual environment if needed.
When developing in an IDE, for instance, this can in some cases be necessary depending on your IDE settings.
To manually activate the virtual environment, run one of the "known" legacy commands: <br>
..on Windows:
```sh
.venv\Scripts\activate.bat
```
..on Linux:
```sh
source .venv/bin/activate
```

### 6. Install pre-commit hooks
The `.pre-commit-config.yaml` file in the project root directory contains a configuration for pre-commit hooks.
To install the pre-commit hooks defined therein in your local git repository, run:
```sh
uv run pre-commit install
```

All pre-commit hooks configured in `.pre-commit-config.yaml` will now run each time you commit changes.

pre-commit can also manually be invoked, at anytime, using:
```sh
uv run pre-commit run --all-files
```

To skip the pre-commit validation on commits (e.g. when intentionally committing broken code), run:
```sh
uv run git commit -m <MSG> --no-verify
```

To update the hooks configured in `.pre-commit-config.yaml` to their newest versions, run:
```sh
uv run pre-commit autoupdate
```

### 7. Test that the installation works
To test that the installation works, run pytest in the project root folder:
```sh
uv run pytest
```

## Meta

Copyright (c) 2024 [DNV](https://www.dnv.com) SE. All rights reserved.

Frank Lumpitzsch - [@LinkedIn](https://www.linkedin.com/in/frank-lumpitzsch-23013196/) - frank.lumpitzsch@dnv.com

Claas Rostock - [@LinkedIn](https://www.linkedin.com/in/claasrostock/?locale=en_US) - claas.rostock@dnv.com

Seunghyeon Yoo - [@LinkedIn](https://www.linkedin.com/in/seunghyeon-yoo-3625173b/) - seunghyeon.yoo@dnv.com

Distributed under the MIT license. See [LICENSE](LICENSE.md) for more information.

[https://github.com/dnv-opensource/ospx](https://github.com/dnv-opensource/ospx)

## Contributing

1. Fork it (<https://github.com/dnv-opensource/ospx/fork>)
2. Create an issue in your GitHub repo
3. Create your branch based on the issue number and type (`git checkout -b issue-name`)
4. Evaluate and stage the changes you want to commit (`git add -i`)
5. Commit your changes (`git commit -am 'place a descriptive commit message here'`)
6. Push to the branch (`git push origin issue-name`)
7. Create a new Pull Request in GitHub

For your contribution, please make sure you follow the [STYLEGUIDE](STYLEGUIDE.md) before creating the Pull Request.

<!-- Markdown link & img dfn's -->
[dictIO_docs]: https://dnv-opensource.github.io/dictIO/README.html
[ospx_docs]: https://dnv-opensource.github.io/ospx/README.html
[farn_docs]: https://dnv-opensource.github.io/farn/README.html
[osp_docs]: https://open-simulation-platform.github.io/

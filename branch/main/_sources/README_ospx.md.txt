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
~~~py
from ospx import OspCaseBuilder

OspCaseBuilder.build('caseDict')
~~~

The above task can also be invoked from the command line, using the 'ospCaseBuilder' command line script installed with ospx:
~~~sh
ospCaseBuilder caseDict
~~~

_For more examples and usage, please refer to [ospx's documentation][ospx_docs] on GitHub Pages._

## File Format
A caseDict is a file in dictIO dict file format used with farn.

_For a documentation of the caseDict file format, see [File Format](fileFormat.md) in [ospx's documentation][ospx_docs] on GitHub Pages._

_For a detailed documentation of the dictIO dict file format used by farn, see [dictIO's documentation][dictIO_docs] on GitHub Pages._

## Development Setup

1. Install Python 3.9 or higher, i.e. [Python 3.9](https://www.python.org/downloads/release/python-3912/) or [Python 3.10](https://www.python.org/downloads/release/python-3104/)

2. Update pip and setuptools:

    ~~~sh
    $ python -m pip install --upgrade pip setuptools
    ~~~

3. git clone the farn repository into your local development directory:

    ~~~sh
    git clone https://github.com/dnv-opensource/ospx path/to/your/dev/ospx
    ~~~

4. In the ospx root folder:

    Create a Python virtual environment:
    ~~~sh
    $ python -m venv .venv
    ~~~
    Activate the virtual environment: <br>
    ..on Windows:
    ~~~sh
    > .venv\Scripts\activate.bat
    ~~~
    ..on Linux:
    ~~~sh
    $ source .venv/bin/activate
    ~~~
    Update pip and setuptools:
    ~~~sh
    $ python -m pip install --upgrade pip setuptools
    ~~~
    Install farn's dependencies:
    ~~~sh
    $ pip install -r requirements.txt
    ~~~


## Meta

Copyright (c) 2022 [DNV](https://www.dnv.com) [open source](https://github.com/dnv-opensource)

Frank Lumpitzsch – [@LinkedIn](https://www.linkedin.com/in/frank-lumpitzsch-23013196/) – frank.lumpitzsch@dnv.com

Claas Rostock – [@LinkedIn](https://www.linkedin.com/in/claasrostock/?locale=en_US) – claas.rostock@dnv.com

Seunghyeon Yoo – [@LinkedIn](https://www.linkedin.com/in/seunghyeon-yoo-3625173b/) – seunghyeon.yoo@dnv.com

Distributed under the MIT license. See [LICENSE](LICENSE.md) for more information.

[https://github.com/dnv-opensource/ospx](https://github.com/dnv-opensource/ospx)

## Contributing

1. Fork it (<https://github.com/dnv-opensource/ospx/fork>)
2. Create your branch (`git checkout -b myBranchName`)
3. Commit your changes (`git commit -am 'place your commit message here'`)
4. Push to the branch (`git push origin myBranchName`)
5. Create a new Pull Request

For your contribution, please make sure you follow the [STYLEGUIDE](STYLEGUIDE.md) before creating the Pull Request.

<!-- Markdown link & img dfn's -->
[dictIO_docs]: https://dnv-opensource.github.io/dictIO/
[ospx_docs]: https://dnv-opensource.github.io/ospx/
[farn_docs]: https://dnv-opensource.github.io/farn/
[osp_docs]: https://open-simulation-platform.github.io/
# README
farn is an n-dimensional case generator.

Its primary design goal is to parameterize and execute simulation cases.
However, at its core farn is use-case agnostic and can hence support a wide spectrum of applications.

The name ‘farn’ is inspired by the [Barnsley fractal](https://en.wikipedia.org/wiki/Barnsley_fern)

farn provides both an API for use inside Python as well as a CLI for shell execution of core functions.

farn enables you to:
* generate an arbitrary discrete sampling of the design space (e.g. fixed, linSpace, uniformLHS)
* generate the corresponding case folder structure
* copy arbitrary files from a template folder into case folders
* create a case specific parameter file in each case folder
* execute user-defined shell commands in case folders
* build case specific OSP (co-)simulation files
* run simulation cases as batch process

## Installation
```sh
pip install farn
```
farn requires the following two (sub-)packages:
1. [dictIO][dictIO_docs]: foundation package, enabling farn to handle configuration files in C++ dictionary format.
2. [ospx][ospx_docs]: extension package, enabling farn to generate OSP (co-)simulation files.

However, both get installed automatically with farn (just pip install farn and you're done).

## Usage example

farn provides a simple, high level API that allows to e.g. read a farnDict file and create the resulting case folder structure in essentially one line of code:
~~~py
from farn.farn import run_farn

run_farn('farnDict', run_sampling=True, generate=True)
~~~
_For more examples and usage, please refer to [farn's documentation][farn_docs] on GitHub Pages._


## File Format
A farnDict is a file in C++ dictionary format used with farn.

_For a detailed documentation of the farnDict file format, see [File Format](fileFormat.md) in [farn's documentation][farn_docs] on GitHub Pages._

_For a detailed documentation of the general C++ dictionary file format used by farn, see File Format in [dictIO's documentation][dictIO_docs] on GitHub Pages._

## Development setup

1. Install [Python 3.9](https://www.python.org/downloads/release/python-399/)

2. git clone the dictIO repository into your local development directory

~~~sh
git clone git://github.com/dnv-opensource/farn.git path/to/your/dev/farn
~~~

3. In the farn root folder:

Create a Python virtual environment:
~~~sh
python -m venv .venv
~~~
Activate the virtual environment:
~~~sh
.venv\Scripts\activate
~~~
Update pip and setuptools:
~~~sh
python -m pip install --upgrade pip setuptools
~~~
Install farn's dependencies:
~~~sh
pip install -r requirements.txt
~~~


## Release History

* 0.1.0
    * First release

## Meta

Copyright (c) 2022 [DNV](https://www.dnv.com) [open source](https://github.com/dnv-opensource)

Frank Lumpitzsch – [@LinkedIn](https://www.linkedin.com/in/frank-lumpitzsch-23013196/) – frank.lumpitzsch@dnv.com

Claas Rostock – [@LinkedIn](https://www.linkedin.com/in/claasrostock/?locale=en_US) – claas.rostock@dnv.com

Seunghyeon Yoo – [@LinkedIn](https://www.linkedin.com/in/seunghyeon-yoo-3625173b/) – seunghyeon.yoo@dnv.com

Distributed under the MIT license. See [LICENSE](LICENSE.md) for more information.

[https://github.com/dnv-opensource/farn](https://github.com/dnv-opensource/farn)

## Contributing

1. Fork it (<https://github.com/dnv-opensource/farn/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

For your contribution, please make sure you follow the [STYLEGUIDE](STYLEGUIDE.md) before creating the Pull Request.

<!-- Markdown link & img dfn's -->
[dictIO_docs]: https://turbo-adventure-f218cdea.pages.github.io
[ospx_docs]: https://literate-guacamole-9daa57bc.pages.github.io
[farn_docs]: https://crispy-tribble-285142b5.pages.github.io
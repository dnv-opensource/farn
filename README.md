# Farn model verification framework
Farn is multi-dimensional case generator​ and is suitable for nearly everything (where the aim is to distribute and execute simulations and to collect the results).
The name ‘farn’ is inspired by the well-known Barnsley fractal: https://en.wikipedia.org/wiki/Barnsley_fern​.
Farn consists of Python packages that can be invoked by own Python code and command line scripts for core functions.​
Farn can
* generate an arbitrary discrete sampling of the design space (e.g. fixed, linSpace, uniformLHS)​
* generate a deep case folder structure with each including parameter files (Dictionaries)
* execute user-defined command sets in case folders​
* run simulation cases as batch​ processes, also in parallel.
* build parameterized simulator case files (e.g. OSP, cosim)​

Farn makes widely use of
## Dictionaries
Dictionaries are a modified adaptatione of C++ dictionaries, as the are used e.g. within OpenFOAM.
Some syntactic addions are made to improve the usability and versatility of Dictionaries:
* reading and writing data in C++ dictionary format​
* translating files into runtime data structures with minimal expense: dict is one of the core built-in data structures in Python 3.9​
* supporting variables and expressions, resolved during parseing
* supporting cascaded dict files:  base dict including param dict yielding case dict​
* is widely tolerant in reading different flavours (quotes, preserving comments, etc.)​
* can read C++ dictionary, JSON, XML​
* can write C++ dictionary, JSON, XML, OpenFOAM​

## Example

## Documentation


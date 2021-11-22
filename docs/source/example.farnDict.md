# farnDict file

A farnDict is a file in C++ dictionary format used with farn

A farnDict
* defines the layers, the parameters varied per layer and the related sampling used to create the samples per layer
* after sampling, the layers, parameters and generated samples per layer make up the designspace that farn traverses
* farn creates one distinct case folder for each sample, making up a nested case folder structure
* nest levels and - dimensions of the case folder sructure follows the sequence of layers as defined in the farn dict

Below example shows the typical structure of a farnDict file.

In the example, a 6-dimensional design space is spawned, organised in 4 layers:
1.  'gp'        level 0     (root layer)    no. of parameters: 1    sampling: fixed      (Example 'gp' indicating e.g. a hypothetical grid parameter)
2.  'lhsvar'    level 1     (nested layer)  no. of parameters: 3    sampling: uniformLhs (Example  3 dimensional sub design space, LHS sampled)
3.  'cp'        level 2     (nested layer)  no. of parameters: 1    sampling: linSpace   (Example 'cp' indicating e.g. a hypothetical compute parameter (solver setting, version whatever))
4.  'mp'        level 3     (nested layer)  no. of parameters: 1    sampling: fixed      (Example 'mp' indicating e.g. a hypothetical multiplier for an internal variable)
~~~
/*---------------------------------*- C++ -*----------------------------------*\
filetype dictionary; coding utf-8; version 0.1; local --; purpose --;
\*----------------------------------------------------------------------------*/
_environment
{
    CASEDIR                   cases;
    DUMPDIR                   dump;
    LOGDIR                    logs;
    RESULTDIR                 results;
    TEMPLATEDIR               template;
}
_layers
{
    gp                                          // unique identifier of a layer. This identifier will be used by farn as folder name.
    {
        _sampling
        {
            _type fixed;                        // Fixed values. Note: Each sampling type has its own set of required arguments.
            _names(mpGrid);                     // list with names, each representing one variable or parameter.
            _values((0.9 1.3));                 // list containing tuples with fixed values, one tuple for each parameter name. Required for sampling type 'fixed'.
        }
    }
    lhsvar
    {
        _sampling
        {
            _type uniformLhs;                   // Latin-Hypercube-Sampling. Future options might also include normallhs, lognormlhs etc.
            _names(param1 param2 param3);
            _ranges((-10 10)(0 3.5)(0 1.1));    // list containing ranges. A range is defined through the lower and upper boundary value for the related parameter name, given as tuple (minimum, maximum). For each parameter name, one range tuple must exist.
            _includeBoundingBox True;           // [optional] defines whether the lower and upper boundary values of each parameter name shall be added as additional samples. If missing, defaults to False.
            _numberOfSamples 100;               // number of samples to be generated. The given number of samples will be generated within range (=between lower and upper boundary), excluding the boundaries themselves.
        }
    }
    cp
    {
        _sampling
        {
            _type linSpace;                     // Linearly spaced sampling.
            _names(relFactor);
            _ranges((0.5 0.8));
            _numberOfSamples 5;
        }
        _condition                              // a condition allows to define a filter expression to include or exclude specific samples.
        {
            _filter  'param2 >= param3 and param1 >= 0'; // filter expression.
            _action  exclude;                            // [optional] defines the action triggered when the filter expression evaluates to True. choices: 'include', 'exclude'. If missing, defaults to 'exclude'.
        }
    }
    mp
    {
        _sampling
        {
            _type fixed;
            _names(cpMul ppMul);                // hypothetical multiplier for solver and postprocessing, whatever
            _values((1.5 2.0 3.5)(1.5 2.0 3.5));
        }
        _commands                               // commands. Each command element contains a list with one or more shell commands.
        {
            prepare                             // command 'prepare'
                (
                    'copy %TEMPLATEDIR%/caseDict'
                    'rem parsed.caseDict'
                    'dictParser --quiet caseDict'
                );
            run                                 // command 'run'
                (
                    'cosim.exe run OspSystemStructure.xml -b 0 -d 20 --real-time -v'
                );
        }
    }
}
~~~

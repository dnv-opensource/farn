#!/usr/bin/env python
# coding utf-8

# sampling.py
# all about sampling an distributions
# we will see for what it is good for

import logging
import math
from typing import Iterable, MutableMapping, Union, Sequence

import numpy as np


logger = logging.getLogger(__name__)


class DiscreteSampling():

    def __init__(self):

        self.base_name = 'unnamed'
        self.kwargs = {}
        self.fields = []

        self.sampling_type: str = str()

        self.number_of_fields: int = 0
        self.number_of_samples: int = 0
        self.leading_zeros: int = 0

    def set_sampling_type(self, sampling_type: str):
        '''
        sets the sampling type. sampling_type must match one of the known sampling types as defined in this function.
        '''
        self.known_sampling_types = {
            'fixed': {
                'required_args': ['_names', '_values']
            },
            'linSpace': {
                'required_args': ['_names', '_ranges', '_numberOfSamples']
            },
            'arbitrary': {
                'required_args': [
                    '_names',
                    '_ranges',
                    '_numberOfSamples',
                    '_distributionName',                                                            # uniform|normal|exp... better to have a dedicated name in known_sampling_types
                    '_distributionParameters',                                                      # mu|sigma|skew|camber not applicsble for uniform
                    '_includeBoundingBox'                                                           # required
                ]
            },
            'uniformLhs': {
                'required_args': ['_names', '_ranges', '_numberOfSamples', '_includeBoundingBox']
            },
            'normalLhs': {
                'required_args': ['_names', '_numberOfSamples', '_mu', '_sigma'],
                'optional_args': ['_ranges', '_cov']
            },
            'randNormal': {
                'required_args': [
                    '_names',
                    '_ranges',
                    '_numberOfSamples',
                    '_mu',                                                                          # 1rst order
                    '_sigma',                                                                       # 2nd order
                    '_includeBoundingBox'
                ]
            },
            'sobol': {
                'required_args': [
                    '_names',
                    '_ranges',
                    '_numberOfSamples',                                                             # determines overall sobol set (+ _onset)
                    '_onset',                                                                       # skip first sobol points and start at _onset number
                    '_includeBoundingBox'
                ]
            }
        }

        if sampling_type in self.known_sampling_types:
            self.sampling_type = sampling_type
        else:
            logger.error(f'sampling type {sampling_type} not implemented yet')
            exit(1)

    def set_sampling_parameters(
        self, base_name: str = 'unnamed', kwargs: Union[MutableMapping, None] = None
    ):
        '''
        Validates the provided arguments.
        On successful validation, the configured sampling type is parameterized using the provided arguments.
        '''
        self.base_name = base_name
        self.kwargs = kwargs or {}

        # check if all required arguments are provided
        # todo: check argument types
        for kwarg in self.known_sampling_types[self.sampling_type]['required_args']:
            if kwarg not in self.kwargs:
                logger.error(
                    f'The following required argument is missing to configure '
                    f'sampling type {self.sampling_type}: {kwarg}'
                )

        # read all fields
        for name in self.kwargs['_names']:
            self.fields.append(name)

        # determine the dimension (=number of fields)
        self.number_of_fields = len(self.fields)

        # extra bounding box samples are not treated by lhs algorithm, however part of the lists
        self.number_of_samples = 0
        self.number_of_bb_samples = 0

    def generate(self) -> dict:
        '''
        '''
        import itertools

        return_dict = {}

        if self.sampling_type == 'fixed':

            # set dimension of samples and check nested list
            if not len(self.kwargs['_names']) == len(self.kwargs['_values']):
                logger.error('lists: lenght of entries do not match')

            for item in self.kwargs['_values']:
                try:
                    self.number_of_samples = len(item)
                    break
                except Exception:
                    logger.exception(
                        'values: list(dim names) of lists(dim _samples) required as input'
                    )

            # check equality of nested lists
            for item in self.kwargs['_values']:
                if self.number_of_samples != len(item):
                    logger.error('values: lists in list of lists do not match')

            # get all the fields
            self.values = self.kwargs['_values']

            self.leading_zeros = int(math.log10(self.number_of_samples) - 1.e-06) + 1

            return_dict.update(
                {
                    '_case_name': [
                        '%s_%s' % (self.base_name, format(i, '0%i' % self.leading_zeros))
                        for i in range(self.number_of_samples)
                    ]
                }
            )
            for index, field in enumerate(self.fields):
                return_dict.update({field: [x for x in self.values[index]]})

        if self.sampling_type == 'linSpace':

            self.number_of_samples = int(self.kwargs['_numberOfSamples'])

            # check length of nested lists
            if not len(self.kwargs['_names']) == len(self.kwargs['_ranges']):
                logger.error('lists: lenght of entries do not match')

            # check equality of nested lists
            for item in self.kwargs['_ranges']:
                if not len(item) == 2:
                    logger.error('ranges: lists in list of lists do not contain min and max')

            self.minVals = [x[0] for x in self.kwargs['_ranges']]
            self.maxVals = [x[1] for x in self.kwargs['_ranges']]

            self.leading_zeros = int(math.log10(self.number_of_samples) - 1.e-06) + 1
            return_dict.update(
                {
                    '_case_name': [
                        '%s_%s' % (self.base_name, format(i, '0%i' % self.leading_zeros))
                        for i in range(self.number_of_samples)
                    ]
                }
            )

            for index, item in enumerate(self.fields):
                return_dict.update(
                    {
                        self.fields[index]:
                        list(
                            np.linspace(
                                self.minVals[index], self.maxVals[index], self.number_of_samples
                            )
                        )
                    }
                )

        if self.sampling_type == 'normalLhs':
            '''lhs using gaussian normal dstributions
            required input arguments:
            * _names: required names template
            * _numberOfSamples: required how many samples
            * _mu: required absolute location vector of distribution center point (origin)
            * _sigma: variation (vector), or required scalar, optional vector, optional cov
            or
            NOT IMPLEMENTED, DOES NOT MAKE MUCH SENSE!
            * _cov: @ _mu optional rotation (tensor), otherwise I(_numberOfSamples,_numberOfSamples)
            '''
            self.number_of_samples = int(self.kwargs['_numberOfSamples'])
            self.leading_zeros = int(math.log10(self.number_of_samples) - 1.e-06) + 1
            self.case_names = [
                '%s_%s' % (self.base_name, format(i, '0%i' % self.leading_zeros))
                for i in range(self.number_of_samples)
            ]
            return_dict.update({'_case_name': self.case_names})

            # check dimension of nested lists / vectors
            if not len(self.kwargs['_names']) == len(self.kwargs['_mu']):
                logger.error('lists _names and _mu: lenght of entries do not match')
            self.mean = self.kwargs['_mu']
            if isinstance(self.kwargs['_sigma'],
                          list) and not len(self.kwargs['_names']) == len(self.kwargs['_sigma']):
                logger.error('lists _names and _sigma: lenght of entries do not match')
            self.std = self.kwargs['_sigma']

            self.variables = self.generate_normal_lhs()

            # optional clipping cube
            # ToDo:
            # clipping is implemented, resets the value to range value
            # if this is unaffordable, purgign should be considered, requiring a decrementation of number_of_samples
            if '_ranges' in self.kwargs:
                # check equality of nested lists
                for item in self.kwargs['_ranges']:
                    if not len(item) == 2:
                        logger.error('ranges: lists in list of lists do not contain min and max')

                self.bounds = self.kwargs['_ranges']

                clipped = np.zeros(self.variables.shape)

                for index, field in enumerate(self.variables):
                    clipped[index] = np.clip(field, self.bounds[index][0], self.bounds[index][1])

                self.variables = clipped

            for index, item in enumerate(self.fields):
                return_dict.update({self.fields[index]: self.variables[index].tolist()})

        if self.sampling_type == 'uniformLhs':
            '''lhs uniform
            later implementations may change thie section
            '''
            # first dimension n samples
            self.number_of_samples = int(self.kwargs['_numberOfSamples'])
            if self.kwargs['_includeBoundingBox'] is True:
                self.number_of_bb_samples = int(2**self.number_of_fields)
            self.number_of_samples += self.number_of_bb_samples

            self.leading_zeros = int(math.log10(self.number_of_samples) - 1.e-06) + 1
            self.bounds = self.kwargs['_ranges']
            self.case_names = [
                '%s_%s' % (self.base_name, format(i, '0%i' % self.leading_zeros))
                for i in range(self.number_of_samples)
            ]
            return_dict.update({'_case_name': self.case_names})

            # check length of nested lists
            if not len(self.kwargs['_names']) == len(self.kwargs['_ranges']):
                logger.error('lists _names and _ranges: lenght of entries do not match')

            # check equality of nested lists
            for item in self.kwargs['_ranges']:
                if not len(item) == 2:
                    logger.error('ranges: lists in list of lists do not contain min and max')

            self.variables = self.generate_uniform_lhs()

            if self.kwargs['_includeBoundingBox'] is True:
                tmp = []
                if len(self.kwargs['_ranges']) == 1:
                    # (only one single parameter defined)
                    tmp = list(self.kwargs['_ranges'][0])
                else:
                    # permutate boundaries of all paramaters
                    tmp = list(
                        itertools.product(self.kwargs['_ranges'][0], self.kwargs['_ranges'][1])
                    )
                    for field_index in range(1, self.number_of_fields - 1):
                        tmp = list(itertools.product(tmp, self.kwargs['_ranges'][field_index + 1]))

                self.boundingBox = []
                for item in tmp:
                    if isinstance(item, Iterable):
                        self.boundingBox.append(list(self.flatten(item)))
                    else:
                        self.boundingBox.append([item])

                self.variables = np.concatenate(
                    (np.array(self.boundingBox).T, self.variables), axis=1
                )

            for index, item in enumerate(self.fields):
                return_dict.update({self.fields[index]: self.variables[index].tolist()})

        if self.sampling_type == 'arbitrary':
            '''
            Purpose: To perform a sampling based on the pre-drawn sample.
            Pre-requisite:
                1. Since the most fitted distribution is unknown, it shall be found by using the fitter module.
                2. fitter module provides: 1) the name of the most fitted distribution, 2) relavant parameters
                3. relavent parameters mostly comprises with 3 components: 1) skewness 2) location 3) scale
                4. At this moment, those prerequisites shall be provided as arguments. This could be modified later
                5. refer to commented example below.
            '''

            self.number_of_samples = int(self.kwargs['_numberOfSamples'])
            self.leading_zeros = int(math.log10(self.number_of_samples) - 1.e-06) + 1

            # check length of nested lists
            if not len(self.kwargs['_names']) == len(self.kwargs['_ranges']):
                logger.error('lists: lenght of entries do not match')

            # check equality of nested lists
            for item in self.kwargs['_ranges']:
                if not len(item) == 2:
                    logger.error('ranges: lists in list of lists do not contain min and max')

            self.minVals = [x[0] for x in self.kwargs['_ranges']]
            self.maxVals = [x[1] for x in self.kwargs['_ranges']]

            return_dict.update(
                {
                    '_case_name': [
                        '%s_%s' % (self.base_name, format(i, '0%i' % self.leading_zeros))
                        for i in range(self.number_of_samples)
                    ]
                }
            )

            import scipy.stats  # noqa: F401

            for index, item in enumerate(self.fields):
                self.distribution_name = self.kwargs['_distributionName']
                self.distribution_parameters = self.kwargs['_distributionParameters']

                eval_command = f'scipy.stats.{self.distribution_name[index]}'

                dist = eval(eval_command)   # check this need!

                return_dict.update(
                    {
                        self.fields[index]:
                        dist.rvs(
                            *self.distribution_parameters[index], size=self.number_of_samples
                        ).tolist()
                    }
                )

            # requires if self.kwargs['_includeBoundingBox'] is True: as well

        if self.sampling_type == 'sobol':
            '''
            '''
            # first dimension n samples
            self.number_of_samples = int(self.kwargs['_numberOfSamples'])
            if self.kwargs['_includeBoundingBox'] is True:
                self.number_of_bb_samples = int(2**self.number_of_fields)
            self.number_of_samples += self.number_of_bb_samples

            self.leading_zeros = int(math.log10(self.number_of_samples) - 1.e-06) + 1
            self.onset = int(self.kwargs['_onset'])
            self.bounds = self.kwargs['_ranges']
            self.case_names = [
                '%s_%s' % (self.base_name, format(i, '0%i' % self.leading_zeros))
                for i in range(self.number_of_samples)
            ]
            return_dict.update({'_case_name': self.case_names})

            # check length of nested lists
            if not len(self.kwargs['_names']) == len(self.kwargs['_ranges']):
                logger.error('lists: lenght of entries do not match')

            # check equality of nested lists
            for item in self.kwargs['_ranges']:
                if not len(item) == 2:
                    logger.error('ranges: lists in list of lists do not contain min and max')

            self.variables = self.generate_sobol()

            if self.kwargs['_includeBoundingBox'] is True:
                # permutate boundaries
                tmp = list(itertools.product(self.kwargs['_ranges'][0], self.kwargs['_ranges'][1]))
                for field_index in range(1, self.number_of_fields - 1):
                    tmp = list(itertools.product(tmp, self.kwargs['_ranges'][field_index + 1]))

                self.boundingBox = []
                for item in tmp:
                    self.boundingBox.append(list(self.flatten(item)))

                self.variables = np.concatenate(
                    (np.array(self.boundingBox).T, self.variables), axis=1
                )

            for index, item in enumerate(self.fields):
                return_dict.update({self.fields[index]: self.variables[index].tolist()})

        return return_dict

    def flatten(self, iterable: Sequence):
        '''flattens sequence... happens why?
        '''
        for element in iterable:
            if isinstance(element, Sequence) and not isinstance(element, (str, bytes)):
                yield from self.flatten(element)
            else:
                yield element

    def min_max_scale(self, field: np.ndarray, range: MutableMapping):
        '''might belong to different class in future
        from sklearn.preporcessing import minmax_scale
        '''
        scale = (range[1] - range[0]) / (field.max(axis=0) - field.min(axis=0))

        return scale * field + range[0] - field.min(axis=0) * scale

    def generate_uniform_lhs(self):
        '''
        alternative
        from pyDOE2 import lhs
        lhs_dist = lhs(n, samples=n_samples, criterion='corr', random_state=None)
        criterion: center|maximin|centermaximin|correlation
        '''
        from SALib.sample import latin

        problem = {
            'num_vars': self.number_of_fields,
            'names': self.fields,
            'bounds': self.bounds,
        }

        return latin.sample(problem, self.number_of_samples - self.number_of_bb_samples).T

    def generate_normal_lhs(self):
        '''gaussnormal lhs
        '''
        from pyDOE2 import lhs
        from scipy.stats import norm    # qmc, truncnorm

        lhs_distribution = lhs(
            self.number_of_fields,
            samples=self.number_of_samples - self.number_of_bb_samples,
            criterion="corr",
            random_state=None,
        )
        # criterion:center|c: center the points within the sampling intervals
        #          maximin|m: maximize the minimum distance between points, but place the point in a randomized location within its interval
        #          centermaximin|cm: same as “maximin”, but centered within the intervals
        #          correlation|corr: minimize the maximum correlation coefficient
        # lhs_distribution = qmc.LatinHypercube(d=self.number_of_fields, optimization="random-cd").random(n=self.number_of_samples - self.number_of_bb_samples)

        # std of type scalar (scale) or vector (stretch, scale), no rotation
        self.std = np.array(self.std)

        sample_set = norm(loc=self.mean, scale=self.std).ppf(lhs_distribution)

        # transpose to be aligned with uniformLhs output
        return sample_set.T

    # @TODO: Should be reimplemented using the scipy.stats.qmc.sobol
    #        https://scipy.github.io/devdocs/reference/generated/scipy.stats.qmc.Sobol.html#scipy-stats-qmc-sobol
    #        This to substitute the sobol-seq package, which is no longer maintained.
    #        (See https://github.com/naught101/sobol_seq)
    #        CLAROS, 2022-05-27
    def generate_sobol(self):
        '''
        '''
        import sobol_seq

        sequence = sobol_seq.i4_sobol_generate(
            self.number_of_fields, self.number_of_samples - self.number_of_bb_samples + self.onset
        )

        sample_set = sequence[self.onset:self.onset + self.number_of_samples
                              - self.number_of_bb_samples].T

        for index, item in enumerate(sample_set):
            sample_set[index] = self.min_max_scale(item, self.bounds[index])

        return sample_set

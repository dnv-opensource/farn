import logging
import math
from typing import Any, Dict, Generator, Iterable, List, Mapping, Sequence, Union

import numpy as np
from numpy import ndarray

logger = logging.getLogger(__name__)


class DiscreteSampling:
    """Class providing methods to run a discrete sampling of a specific layer,
    i.e. of all variables defined in the given layer.
    """

    def __init__(self):
        self.layer_name: str = ""
        self.sampling_parameters: Mapping[str, Any] = {}
        self.fields: List[str] = []
        self.values: List[Sequence[Any]] = []
        self.ranges: Sequence[Sequence[Any]] = []
        self.bounding_box: List[List[float]] = []
        self.minVals: List[Any] = []
        self.maxVals: List[Any] = []
        self.case_names: List[str] = []
        self.mean: Sequence[float] = []
        self.std: Union[float, Sequence[float], Sequence[Sequence[float]]] = 0.0
        self.onset: int = 0

        self.sampling_type: str = str()
        self.known_sampling_types: Dict[str, Dict[str, List[str]]] = {}
        self._set_up_known_sampling_types()

        self.number_of_fields: int = 0
        self.number_of_samples: int = 0
        self.number_of_bb_samples: int = 0
        self.leading_zeros: int = 0

        self.iteration_depth: int
        self.minIterationDepth: int
        self.maxIterationDepth: int
        self.include_bounding_box: bool = False

    def _set_up_known_sampling_types(self):
        self.known_sampling_types = {
            "fixed": {"required_args": ["_names", "_values"]},
            "linSpace": {"required_args": ["_names", "_ranges", "_numberOfSamples"]},
            "uniformLhs": {
                "required_args": [
                    "_names",
                    "_ranges",
                    "_numberOfSamples",
                ],
                "optional_args": [
                    "_includeBoundingBox",
                ],
            },
            "normalLhs": {
                "required_args": ["_names", "_numberOfSamples", "_mu", "_sigma"],
                "optional_args": ["_ranges", "_cov"],
            },
            "sobol": {
                "required_args": [
                    "_names",
                    "_ranges",
                    "_numberOfSamples",  # determines overall sobol set (+ _onset)
                    "_onset",  # skip first sobol points and start at _onset number
                ],
                "optional_args": [
                    "_includeBoundingBox",
                ],
            },
            "arbitrary": {
                "required_args": [
                    "_names",
                    "_ranges",
                    "_numberOfSamples",
                    "_distributionName",  # uniform|normal|exp... better to have a dedicated name in known_sampling_types
                    "_distributionParameters",  # mu|sigma|skew|camber not applicsble for uniform
                    "_includeBoundingBox",  # required
                ]
            },
            "hilbertCurve": {
                "required_args": [
                    "_names",
                    "_ranges",
                    "_numberOfSamples",
                ],
                "optional_args": [
                    "_includeBoundingBox",
                    "_iterationDepth",
                ],
            },
        }

    def set_sampling_type(self, sampling_type: str):
        """Set the sampling type.

        Valid values:
            "fixed"
            "linSpace"
            "uniformLhs"
            "normalLhs"
            "sobol"
            "arbitrary"
        """
        if sampling_type in self.known_sampling_types:
            self.sampling_type = sampling_type
        else:
            logger.error(f"sampling type {sampling_type} not implemented yet")
            exit(1)

    def set_sampling_parameters(
        self,
        sampling_parameters: Mapping[str, Any],
        layer_name: str = "",
    ):
        """Set the sampling parameters.

        The passed-in sampling parameters will be validated.
        Upon successful validation, the sampling is configured using the provided parameters.
        """

        self.layer_name = layer_name
        self.sampling_parameters = sampling_parameters

        # check if all required arguments are provided
        # todo: check argument types
        for kwarg in self.known_sampling_types[self.sampling_type]["required_args"]:
            if kwarg not in self.sampling_parameters:
                msg: str = (
                    f"The following required argument is missing to configure "
                    f"sampling type {self.sampling_type}: {kwarg}"
                )
                logger.error(msg)

        # read all fields
        for name in self.sampling_parameters["_names"]:
            self.fields.append(name)

        # determine the dimension (=number of fields)
        self.number_of_fields = len(self.fields)

        # ranges
        if "_ranges" in self.sampling_parameters and self._check_consistency_of_ranges(
            self.sampling_parameters["_ranges"]
        ):
            self.ranges = self.sampling_parameters["_ranges"]

        # extra bounding box samples are not treated by lhs algorithm, however part of the lists
        self.number_of_samples = 0
        self.number_of_bb_samples = 0

    def generate_samples(self) -> Dict[str, List[Any]]:
        """Return a dict with all generated samples for the layer this sampling is run on.

        The first element in the returned dict contains the case names generated.
        All following elements (second to last) contain the values sampled for each variable defined in the layer this sampling is run on.
        I.e.
        "names": (case_name_1, case_name_2, .., case_name_n)
        "variable_1": (value_1, value_2, .., value_n)
        ...
        "variable_m": (value_1, value_2, .., value_n)

        Returns
        -------
        Dict[str, List[Any]]
            the dict with all generated samples
        """

        samples: Dict[str, List[Any]] = {}

        if self.sampling_type == "fixed":
            samples = self._generate_samples_using_fixed_sampling()

        elif self.sampling_type == "linSpace":
            samples = self._generate_samples_using_linspace_sampling()

        elif self.sampling_type == "uniformLhs":
            samples = self._generate_samples_using_uniform_lhs_sampling()

        elif self.sampling_type == "normalLhs":
            samples = self._generate_samples_using_normal_lhs_sampling()

        elif self.sampling_type == "sobol":
            samples = self._generate_samples_using_sobol_sampling()

        elif self.sampling_type == "arbitrary":
            samples = self._generate_samples_using_arbitrary_sampling()

        elif self.sampling_type == "hilbertCurve":
            samples = self._generate_samples_using_hilbert_sampling()

        else:
            raise NotImplementedError(f"{self.sampling_type} not implemented yet.")

        return samples

    def _generate_samples_using_fixed_sampling(self) -> Dict[str, List[Any]]:
        samples: Dict[str, List[Any]] = {}
        _ = self._check_size_of_parameter_matches_number_of_names("_values")

        for item in self.sampling_parameters["_values"]:
            try:
                self.number_of_samples = len(item)
                break
            except Exception:
                logger.exception("values: list(dim names) of lists(dim _samples) required as input")

        # check equality of nested lists
        for item in self.sampling_parameters["_values"]:
            if self.number_of_samples != len(item):
                logger.error("values: lists in list of lists do not match")

        # get all the fields
        self.values = self.sampling_parameters["_values"]

        self.leading_zeros = int(math.log10(self.number_of_samples) - 1.0e-06) + 1

        self._generate_case_names(samples)

        for index, field in enumerate(self.fields):
            samples[field] = list(self.values[index])

        return samples

    def _generate_samples_using_linspace_sampling(self) -> Dict[str, List[Any]]:
        samples: Dict[str, List[Any]] = {}
        self.number_of_samples = int(self.sampling_parameters["_numberOfSamples"])

        _ = self._check_size_of_parameter_matches_number_of_names("_ranges")

        self.minVals = [x[0] for x in self.ranges]
        self.maxVals = [x[1] for x in self.ranges]

        self.leading_zeros = int(math.log10(self.number_of_samples) - 1.0e-06) + 1
        self._generate_case_names(samples)

        for index, _ in enumerate(self.fields):
            samples[self.fields[index]] = list(
                np.linspace(
                    self.minVals[index],
                    self.maxVals[index],
                    self.number_of_samples,
                )
            )

        return samples

    def _generate_samples_using_uniform_lhs_sampling(self) -> Dict[str, List[Any]]:
        samples: Dict[str, List[Any]] = {}

        if "_includeBoundingBox" in self.sampling_parameters.keys() and isinstance(
            self.sampling_parameters["_includeBoundingBox"], bool
        ):
            self.include_bounding_box = self.sampling_parameters["_includeBoundingBox"]

        # first dimension n samples
        self.number_of_samples = int(self.sampling_parameters["_numberOfSamples"])
        if self.include_bounding_box is True:
            self.number_of_bb_samples = int(2**self.number_of_fields)
        self.number_of_samples += self.number_of_bb_samples

        self.leading_zeros = int(math.log10(self.number_of_samples) - 1.0e-06) + 1

        self._generate_case_names(samples)

        values: ndarray[Any, Any] = self._generate_values_using_uniform_lhs_sampling()

        if self.include_bounding_box is True:
            self._create_bounding_box()
            values = np.concatenate((np.array(self.bounding_box).T, values), axis=1)  # type: ignore

        for index, _ in enumerate(self.fields):
            samples[self.fields[index]] = values[index].tolist()

        return samples

    def _generate_samples_using_normal_lhs_sampling(self) -> Dict[str, List[Any]]:
        """LHS using gaussian normal dstributions
        required input arguments:
        * _names: required names template
        * _numberOfSamples: required how many samples
        * _mu: required absolute location vector of distribution center point (origin)
        * _sigma: variation (vector), or required scalar, optional vector, optional cov
        or
        NOT IMPLEMENTED, DOES NOT MAKE MUCH SENSE!
        * _cov: @ _mu optional rotation (tensor), otherwise I(_numberOfSamples,_numberOfSamples).
        """
        samples: Dict[str, List[Any]] = {}
        self.number_of_samples = int(self.sampling_parameters["_numberOfSamples"])
        self.leading_zeros = int(math.log10(self.number_of_samples) - 1.0e-06) + 1
        self._generate_case_names(samples)
        _ = self._check_size_of_parameter_matches_number_of_names("_mu")

        self.mean = self.sampling_parameters["_mu"]
        if isinstance(self.sampling_parameters["_sigma"], list):
            _ = self._check_size_of_parameter_matches_number_of_names("_sigma")
        self.std = self.sampling_parameters["_sigma"]

        values: ndarray[Any, Any] = self._generate_values_using_normal_lhs_sampling()

        # optional clipping cube
        # ToDo:
        # clipping is implemented, resets the value to range value
        # if this is unaffordable, purgign should be considered, requiring a decrementation of number_of_samples
        if self.ranges:
            clipped: ndarray[Any, Any] = np.zeros(values.shape)
            for index, field in enumerate(values):
                clipped[index] = np.clip(field, self.ranges[index][0], self.ranges[index][1])  # type: ignore
            values = clipped

        for index, _ in enumerate(self.fields):
            samples[self.fields[index]] = values[index].tolist()

        return samples

    def _generate_samples_using_sobol_sampling(self) -> Dict[str, List[Any]]:
        samples: Dict[str, List[Any]] = {}
        samples = self._generate_samples_using_uniform_lhs_sampling()
        self.onset = int(self.sampling_parameters["_onset"])
        self._generate_case_names(samples)

        values: ndarray[Any, Any] = self._generate_values_using_sobol_sampling()

        if "_includeBoundingBox" in self.sampling_parameters.keys() and isinstance(
            self.sampling_parameters["_includeBoundingBox"], bool
        ):
            self.include_bounding_box = self.sampling_parameters["_includeBoundingBox"]

        if self.include_bounding_box is True:
            self._create_bounding_box()
            values = np.concatenate((np.array(self.bounding_box).T, values), axis=1)  # type: ignore

        for index, _ in enumerate(self.fields):
            samples[self.fields[index]] = values[index].tolist()

        return samples

    def _generate_samples_using_arbitrary_sampling(self) -> Dict[str, List[Any]]:
        """
        Purpose: To perform a sampling based on the pre-drawn sample.
        Pre-requisite:
            1. Since the most fitted distribution is unknown, it shall be found by using the fitter module.
            2. fitter module provides: 1) the name of the most fitted distribution, 2) relavant parameters
            3. relavent parameters mostly comprises with 3 components: 1) skewness 2) location 3) scale
            4. At this moment, those prerequisites shall be provided as arguments. This could be modified later
            5. refer to commented example below.
        """

        samples: Dict[str, List[Any]] = {}
        self.number_of_samples = int(self.sampling_parameters["_numberOfSamples"])
        self.leading_zeros = int(math.log10(self.number_of_samples) - 1.0e-06) + 1

        _ = self._check_size_of_parameter_matches_number_of_names("_ranges")

        self.minVals = [x[0] for x in self.ranges]
        self.maxVals = [x[1] for x in self.ranges]

        self._generate_case_names(samples)

        import scipy.stats  # noqa: F401

        distribution_name: Sequence[str]
        distribution_parameters: Sequence[Any]
        for index, _ in enumerate(self.fields):
            distribution_name = self.sampling_parameters["_distributionName"]
            distribution_parameters = self.sampling_parameters["_distributionParameters"]

            eval_command = f"scipy.stats.{distribution_name[index]}"

            dist = eval(eval_command)  # check this need!

            samples[self.fields[index]] = dist.rvs(
                *distribution_parameters[index],
                size=self.number_of_samples,
            ).tolist()

            # requires if self.kwargs['_includeBoundingBox'] is True: as well

        return samples

    def _generate_samples_using_hilbert_sampling(self) -> Dict[str, List[Any]]:
        samples: Dict[str, List[Any]] = {}
        # Depending on implementation
        self.minIterationDepth = 3
        self.maxIterationDepth = 15
        # for numpy: self.maxIterationDepth = 10

        if "_includeBoundingBox" in self.sampling_parameters.keys() and isinstance(
            self.sampling_parameters["_includeBoundingBox"], bool
        ):
            self.include_bounding_box = self.sampling_parameters["_includeBoundingBox"]

        # first dimension n samples
        self.number_of_samples = int(self.sampling_parameters["_numberOfSamples"])

        if self.include_bounding_box is True:
            self.number_of_bb_samples = int(2**self.number_of_fields)
        self.number_of_samples += self.number_of_bb_samples

        self.leading_zeros = int(math.log10(self.number_of_samples) - 1.0e-06) + 1

        self._generate_case_names(samples)

        values: ndarray[Any, Any] = self._generate_values_using_hilbert_sampling()

        if self.include_bounding_box is True:
            self._create_bounding_box()
            values = np.concatenate((np.array(self.bounding_box).T, values), axis=1)  # type: ignore

        for index, _ in enumerate(self.fields):
            samples[self.fields[index]] = values[index].tolist()

        return samples

    def _generate_values_using_uniform_lhs_sampling(self) -> ndarray[Any, Any]:
        """
        alternative
        from pyDOE2 import lhs
        lhs_dist = lhs(n, samples=n_samples, criterion='corr', random_state=None)
        criterion: center|maximin|centermaximin|correlation.
        """
        from SALib.sample import latin

        problem: Dict[str, Any] = {
            "num_vars": self.number_of_fields,
            "names": self.fields,
            "bounds": self.ranges,
        }

        sample_set: ndarray[Any, Any] = latin.sample(  # type: ignore
            problem, self.number_of_samples - self.number_of_bb_samples
        )

        return sample_set.T  # pyright: ignore

    def _generate_values_using_normal_lhs_sampling(self) -> ndarray[Any, Any]:
        """Gaussnormal LHS."""
        from pyDOE2 import lhs
        from scipy.stats import norm  # type: ignore

        lhs_distribution: Union[ndarray[Any, Any], None] = lhs(
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
        _std: ndarray[Any, Any] = np.array(self.std)

        sample_set: ndarray[Any, Any] = norm(loc=self.mean, scale=_std).ppf(lhs_distribution)  # type: ignore

        # transpose to be aligned with uniformLhs output
        return sample_set.T  # pyright: ignore

    def _generate_values_using_sobol_sampling(self) -> ndarray[Any, Any]:
        # @TODO: Should be reimplemented using the scipy.stats.qmc.sobol
        #        https://scipy.github.io/devdocs/reference/generated/scipy.stats.qmc.Sobol.html#scipy-stats-qmc-sobol
        #        This to substitute the sobol-seq package, which is no longer maintained.
        #        (See https://github.com/naught101/sobol_seq)
        #        CLAROS, 2022-05-27
        import sobol_seq

        sequence: ndarray[Any, Any] = sobol_seq.i4_sobol_generate(  # type: ignore
            self.number_of_fields,
            self.number_of_samples - self.number_of_bb_samples + self.onset,
        )

        start: int = self.onset
        end: int = self.onset + self.number_of_samples - self.number_of_bb_samples
        sample_set: ndarray[Any, Any] = sequence[start:end].T

        for index, item in enumerate(sample_set):
            sample_set[index] = self._min_max_scale(item, self.ranges[index])

        return sample_set

    def _generate_values_using_hilbert_sampling(self) -> ndarray[Any, Any]:
        """Source hilbertcurve pypi pkg or numpy
        it showed that hilbertcurve is a better choice and more precise with a higher iteration depth (<=15)
        pypi pkg Decimals is required for proper function up to (<=15)
        numpy approach instead has only (<=10).
        """
        from math import modf

        try:
            from decimal import Decimal
        except ImportError:
            logger.error("no module named Decimal")
            exit(1)
        try:
            from hilbertcurve.hilbertcurve import HilbertCurve
        except ImportError:
            logger.error("no module named HilbertCurve")
            exit(1)

        number_of_continuous_samples: int = self.number_of_samples - self.number_of_bb_samples

        if "_iterationDepth" in self.sampling_parameters.keys():
            if not isinstance(self.sampling_parameters["_iterationDepth"], int):
                logger.error(
                    f'_iterationDepth was not given as integer: {self.sampling_parameters["_iterationDepth"]}.'
                )
                exit(1)
            if self.sampling_parameters["_iterationDepth"] > self.maxIterationDepth:
                msg: str = f'_iterationDepth {self.sampling_parameters["_iterationDepth"]} given in farnDict is beyond the limit of {self.maxIterationDepth}...\n\t\tsetting to {self.maxIterationDepth}'
                logger.warning(msg)
                self.iteration_depth = self.maxIterationDepth
            elif self.sampling_parameters["_iterationDepth"] < self.minIterationDepth:
                msg: str = f'_iterationDepth {self.sampling_parameters["_iterationDepth"]} given in farnDict is below the limit of {self.minIterationDepth}...\n\t\tsetting to {self.minIterationDepth}'
                logger.warning(msg)
                self.iteration_depth = self.minIterationDepth
            else:
                self.iteration_depth = self.sampling_parameters["_iterationDepth"]
        else:
            self.iteration_depth = 10

        hc = HilbertCurve(self.iteration_depth, self.number_of_fields, n_procs=0)  # -1: all threads

        logger.info(
            f"The number of hilbert points is {hc.max_h}, the number of continuous samples is {number_of_continuous_samples}"
        )
        if hc.max_h <= int(10.0 * number_of_continuous_samples):
            logger.warning(
                'Try to set or increase "_iterationDepth" gradually to achieve a number of hilbert points of about 10-times higher than "_numberOfSamples".'
            )

        distribution = np.array(
            [Decimal(x) for x in np.linspace(int(hc.min_h), int(hc.max_h), number_of_continuous_samples)]
        )
        int_distribution = np.trunc(distribution)

        hilbert_points = hc.points_from_distances(int_distribution)

        points: List[List[float]] = []
        interpolation_hits = 0
        for hpt, dst, idst in zip(hilbert_points, distribution, int_distribution):
            if dst == idst:
                points.append(hpt)
            else:
                # interpolation starts: use idst to find integer neighbour of dst
                # nn: next neighbour
                dst_nn = idst + 1
                pt_from_dst = hpt
                pt_from_dst_nn = hc.point_from_distance(dst_nn)

                # find the index where both discrete points are different and interpolate that index
                # and create the new real-valued point
                point: List[float] = []
                for i, j in zip(pt_from_dst, pt_from_dst_nn):
                    if i != j:
                        # non-matching index found, i.e. points are in the same dimension and need to be interpolated alongside
                        smaller_index = min(i, j)
                        fraction, _ = modf(dst)
                        # add the component to real-valued vector
                        point.append(float(smaller_index) + fraction)
                        interpolation_hits += 1
                    else:
                        point.append(float(i))

                points.append(point)

        sample_set: ndarray[Any, Any] = np.array(points).T

        for index, item in enumerate(sample_set):
            sample_set[index] = self._min_max_scale(item, self.ranges[index])

        return sample_set

    def _generate_case_names(
        self,
        samples: Dict[str, List[Any]],
    ):
        self.case_names = [
            f'{self.layer_name}_{format(i, "0%i" % self.leading_zeros)}' for i in range(self.number_of_samples)
        ]
        samples["_case_name"] = self.case_names

    def _check_size_of_parameter_matches_number_of_names(
        self,
        parameter_name: str,
    ) -> bool:
        # check that size of a list/ vector equals the size of _names
        if len(self.sampling_parameters["_names"]) != len(self.sampling_parameters[parameter_name]):
            msg: str = f"lists _names and {parameter_name}: lengths of entries do not match"
            logger.error(msg)
            return False
        return True

    def _check_consistency_of_ranges(self, ranges: Sequence[Sequence[Any]]) -> bool:
        for item in ranges:
            if len(item) != 2:
                logger.error("The structure of min and max values in _ranges is inconsistent.")
                return False
        return self._check_size_of_parameter_matches_number_of_names("_ranges")

    def _create_bounding_box(self):
        import itertools

        tmp: List[Union[float, Sequence[float], Sequence[Any]]] = []
        if len(self.sampling_parameters["_ranges"]) == 1:
            # (only one single parameter defined)
            tmp = list(self.sampling_parameters["_ranges"][0])
        else:
            # permutate boundaries of all paramaters
            tmp = list(
                itertools.product(
                    self.sampling_parameters["_ranges"][0],
                    self.sampling_parameters["_ranges"][1],
                )
            )
            for field_index in range(1, self.number_of_fields - 1):
                tmp = list(itertools.product(tmp, self.sampling_parameters["_ranges"][field_index + 1]))
        self.bounding_box = []
        for item in tmp:
            if isinstance(item, Iterable):
                self.bounding_box.append(list(self._flatten(item)))
            else:
                self.bounding_box.append([item])
        return

    def _flatten(self, iterable: Sequence[Any]) -> Generator[Any, Any, Any]:
        """Flattens sequence... happens why?."""
        for element in iterable:
            if isinstance(element, Sequence) and not isinstance(element, (str, bytes)):
                yield from self._flatten(element)
            else:
                yield element

    def _min_max_scale(self, field: ndarray[Any, Any], range: Sequence[float]) -> ndarray[Any, Any]:
        """Might belong to different class in future
        from sklearn.preprocessing import minmax_scale.
        """
        scale = (range[1] - range[0]) / (field.max(axis=0) - field.min(axis=0))  # type: ignore
        return scale * field + range[0] - field.min(axis=0) * scale  # type: ignore

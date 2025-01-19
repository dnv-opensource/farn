import logging
import math
from collections.abc import Generator, Iterable, Mapping, Sequence
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class DiscreteSampling:
    """Class providing methods to run a discrete sampling of a specific layer,
    i.e. of all variables defined in the given layer.
    """

    def __init__(
        self,
        seed: int | None = None,
    ) -> None:
        self.layer_name: str = ""
        self.sampling_parameters: Mapping[str, Any] = {}
        self.fields: list[str] = []
        self.values: list[Sequence[Any]] = []
        self.ranges: Sequence[Sequence[Any]] = []
        self.bounding_box: list[list[float]] = []
        self.minVals: list[Any] = []
        self.maxVals: list[Any] = []
        self.case_names: list[str] = []
        self.mean: Sequence[float] = []
        self.std: float | Sequence[float] | Sequence[Sequence[float]] = 0.0
        self.onset: int = 0

        self.sampling_type: str = ""
        self.known_sampling_types: dict[str, dict[str, list[str]]] = {}
        self._set_up_known_sampling_types()

        self.number_of_fields: int = 0
        self.number_of_samples: int = 0
        self.number_of_bb_samples: int = 0
        self.leading_zeros: int = 0

        self.iteration_depth: int
        self.minIterationDepth: int
        self.maxIterationDepth: int
        self.include_bounding_box: bool = False
        self.seed: int | None = seed

    def _set_up_known_sampling_types(self) -> None:
        self.known_sampling_types = {
            "fixed": {
                "required_args": [
                    "_names",
                    "_values",
                ]
            },
            "linSpace": {
                "required_args": [
                    "_names",
                    "_ranges",
                    "_numberOfSamples",
                ]
            },
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
                "required_args": [
                    "_names",
                    "_numberOfSamples",
                    "_mu",
                    "_sigma",
                ],
                "optional_args": [
                    "_ranges",
                ],
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
                    "_distributionName",  # uniform|normal|exp...
                    "_distributionParameters",  # mu|sigma|skew|camber not applicable for uniform
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

    def set_sampling_type(self, sampling_type: str) -> None:
        """Set the sampling type.

        Valid values:
            "fixed"
            "linSpace"
            "uniformLhs"
            "normalLhs"
            "sobol"
            "arbitrary"
            "hilbertCurve"
        """
        if sampling_type in self.known_sampling_types:
            self.sampling_type = sampling_type
        else:
            msg: str = f"sampling type {sampling_type} not implemented yet"
            logger.error(msg)
            raise ValueError(msg)

    def set_sampling_parameters(
        self,
        sampling_parameters: Mapping[str, Any],
        layer_name: str = "",
    ) -> None:
        """Set the sampling parameters.

        The passed-in sampling parameters will be validated.
        Upon successful validation, the sampling is configured using the provided parameters.
        """
        self.layer_name = layer_name
        self.sampling_parameters = sampling_parameters

        # check if all required arguments are provided
        # TODO @CLAROS: check argument types
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

    def generate_samples(self) -> dict[str, list[Any]]:
        """Return a dict with all generated samples for the layer this sampling is run on.

        The first element in the returned dict contains the case names generated.
        All following elements (second to last) contain the values sampled
        for each variable defined in the layer this sampling is run on.
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
        samples: dict[str, list[Any]] = {}

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

    def _generate_samples_using_fixed_sampling(self) -> dict[str, list[Any]]:
        _ = self._check_length_matches_number_of_names("_values")
        samples: dict[str, list[Any]] = {}
        msg: str
        # Assert that the values per parameter are provided as a list
        for item in self.sampling_parameters["_values"]:
            if not isinstance(item, Sequence):
                msg = "_values: The values per parameter need to be provided as a list of values."
                logger.error(msg)
                raise TypeError(msg)

        # Assert that the number of values per parameter is the same for all parameters
        number_of_values_per_parameter: list[int] = [len(item) for item in self.sampling_parameters["_values"]]
        all_parameters_have_same_number_of_values: bool = all(
            number_of_values == number_of_values_per_parameter[0]  # (breakline)
            for number_of_values in number_of_values_per_parameter
        )
        if not all_parameters_have_same_number_of_values:
            msg = (
                "_values: The number of values per parameter need to be the same for all parameters. "
                "However, they are different."
            )
            logger.error(msg)
            raise ValueError(msg)

        self.number_of_samples = number_of_values_per_parameter[0]
        self.leading_zeros = int(math.log10(self.number_of_samples) - 1.0e-06) + 1
        self._generate_case_names(samples)

        self.values = self.sampling_parameters["_values"]

        for index, field in enumerate(self.fields):
            samples[field] = list(self.values[index])

        return samples

    def _generate_samples_using_linspace_sampling(self) -> dict[str, list[Any]]:
        _ = self._check_length_matches_number_of_names("_ranges")
        samples: dict[str, list[Any]] = self._generate_samples_dict()
        self.minVals = [x[0] for x in self.ranges]
        self.maxVals = [x[1] for x in self.ranges]

        for index, _ in enumerate(self.fields):
            samples[self.fields[index]] = list(
                np.linspace(
                    self.minVals[index],
                    self.maxVals[index],
                    self.number_of_samples,
                )
            )

        return samples

    def _generate_samples_using_uniform_lhs_sampling(self) -> dict[str, list[Any]]:
        _ = self._check_length_matches_number_of_names("_ranges")
        samples: dict[str, list[Any]] = self._generate_samples_dict()
        values: np.ndarray[Any, np.dtype[np.float64]] = self._generate_values_using_uniform_lhs_sampling()
        self._write_values_into_samples_dict(values, samples)

        return samples

    def _generate_samples_using_normal_lhs_sampling(self) -> dict[str, list[Any]]:
        """LHS using gaussian normal distributions.

        required input arguments:
        * _names: required names template
        * _numberOfSamples: required how many samples
        * _mu: required absolute location vector of distribution center point (origin)
        * _sigma: variation (vector), or required scalar, optional vector
        """
        _ = self._check_length_matches_number_of_names("_mu")
        if isinstance(self.sampling_parameters["_sigma"], Sequence):
            _ = self._check_length_matches_number_of_names("_sigma")

        samples: dict[str, list[Any]] = self._generate_samples_dict()
        self.mean = self.sampling_parameters["_mu"]
        self.std = self.sampling_parameters["_sigma"]

        values: np.ndarray[Any, np.dtype[np.float64]] = self._generate_values_using_normal_lhs_sampling()

        # Clipping
        # (optional. Clipping will only be performed if sampling parameter "_ranges" is defined.)
        # NOTE: In current implementation, sampled values exceeding a parameters valid range
        #       are not discarded but reset to the respective range upper or lower bound.
        #       If real clipping shall be implemented, it would require discarding exceeding values.
        #       As the number of values that would need to be discarded is different
        #       for each individual parameter (dimension),
        #       the necessary clipping logic will quickly become complex.
        #       Hence the somewhat simpler approach for now, where exceeding values
        #       simply get reset to the range bounderies.
        if self.ranges:
            range_lower_bounds: np.ndarray[Any, np.dtype[np.float64]] = np.array([r[0] for r in self.ranges])
            range_upper_bounds: np.ndarray[Any, np.dtype[np.float64]] = np.array([r[1] for r in self.ranges])
            values = np.clip(values, range_lower_bounds, range_upper_bounds)

        self._write_values_into_samples_dict(values, samples)

        return samples

    def _generate_samples_using_sobol_sampling(self) -> dict[str, list[Any]]:
        _ = self._check_length_matches_number_of_names("_ranges")
        self.onset = int(self.sampling_parameters["_onset"])

        samples: dict[str, list[Any]] = self._generate_samples_dict()
        values: np.ndarray[Any, np.dtype[np.float64]] = self._generate_values_using_sobol_sampling()
        self._write_values_into_samples_dict(values, samples)

        return samples

    def _generate_samples_using_arbitrary_sampling(self) -> dict[str, list[Any]]:
        """
        Purpose: To perform a sampling based on the pre-drawn sample.
        Pre-requisite:
            1. Since the most fitted distribution is unknown, it shall be found by using the fitter module.
            2. fitter module provides: 1) the name of the most fitted distribution, 2) relavant parameters
            3. relavent parameters mostly comprises with 3 components: 1) skewness 2) location 3) scale
            4. At this moment, those prerequisites shall be provided as arguments. This could be modified later
            5. refer to commented example below.
        """
        _ = self._check_length_matches_number_of_names("_ranges")

        samples: dict[str, list[Any]] = self._generate_samples_dict()
        self.minVals = [x[0] for x in self.ranges]
        self.maxVals = [x[1] for x in self.ranges]

        import scipy.stats  # noqa: F401

        distribution_name: Sequence[str]
        distribution_parameters: Sequence[Any]
        for index, _ in enumerate(self.fields):
            distribution_name = self.sampling_parameters["_distributionName"]
            distribution_parameters = self.sampling_parameters["_distributionParameters"]

            _eval_command = f"scipy.stats.{distribution_name[index]}"
            dist = eval(_eval_command)  # noqa: S307

            samples[self.fields[index]] = dist.rvs(
                *distribution_parameters[index],
                size=self.number_of_samples,
            ).tolist()

            # requires if self.kwargs['_includeBoundingBox'] is True: as well

        return samples

    def _generate_samples_using_hilbert_sampling(self) -> dict[str, list[Any]]:
        _ = self._check_length_matches_number_of_names("_ranges")
        samples: dict[str, list[Any]] = self._generate_samples_dict()
        # Depending on implementation
        self.minIterationDepth = 3
        self.maxIterationDepth = 15

        values: np.ndarray[Any, np.dtype[np.float64]] = self._generate_values_using_hilbert_sampling()
        self._write_values_into_samples_dict(values, samples)

        return samples

    def _generate_samples_dict(self) -> dict[str, list[Any]]:
        samples_dict: dict[str, list[Any]] = {}
        self._determine_number_of_samples()
        self._generate_case_names(samples_dict)
        return samples_dict

    def _generate_values_using_uniform_lhs_sampling(self) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Uniform LHS."""
        from pyDOE3 import lhs
        from scipy.stats import uniform

        lhs_distribution: np.ndarray[Any, np.dtype[np.float64]] | None = lhs(
            n=self.number_of_fields,
            samples=self.number_of_samples - self.number_of_bb_samples,
            criterion="corr",
            random_state=self.seed,
        )

        _range_lower_bounds: np.ndarray[Any, np.dtype[np.float64]] = np.array([r[0] for r in self.ranges])
        _range_upper_bounds: np.ndarray[Any, np.dtype[np.float64]] = np.array([r[1] for r in self.ranges])
        loc: np.ndarray[Any, np.dtype[np.float64]] = _range_lower_bounds
        scale: np.ndarray[Any, np.dtype[np.float64]] = _range_upper_bounds - _range_lower_bounds

        sample_set: np.ndarray[Any, np.dtype[np.float64]] = uniform(loc=loc, scale=scale).ppf(lhs_distribution)  # pyright: ignore[reportUnknownMemberType]

        return sample_set

    def _generate_values_using_normal_lhs_sampling(self) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Gaussnormal LHS."""
        from pyDOE3 import lhs
        from scipy.stats import norm

        lhs_distribution: np.ndarray[Any, np.dtype[np.float64]] | None = lhs(
            n=self.number_of_fields,
            samples=self.number_of_samples - self.number_of_bb_samples,
            criterion="corr",
            random_state=self.seed,
        )
        # criterion: a string that tells lhs how to sample the points
        #   (default: None, which simply randomizes the points within the intervals)
        #   - center|c: center the points within the sampling intervals
        #   - maximin|m: maximize the minimum distance between points, but place the point
        #                in a randomized location within its interval
        #   - centermaximin|cm: same as “maximin”, but centered within the intervals
        #   - correlation|corr: minimize the maximum correlation coefficient

        # std of type scalar (scale) or vector (stretch, scale), no rotation
        _std: np.ndarray[Any, np.dtype[np.float64]] = np.array(self.std)

        sample_set: np.ndarray[Any, np.dtype[np.float64]] = norm(loc=self.mean, scale=_std).ppf(lhs_distribution)  # pyright: ignore[reportUnknownMemberType]

        return sample_set

    def _generate_values_using_sobol_sampling(self) -> np.ndarray[Any, np.dtype[np.float64]]:
        from scipy.stats import qmc
        from scipy.stats.qmc import Sobol

        sobol_engine: Sobol = Sobol(
            d=self.number_of_fields,
            scramble=False,
            rng=None,
        )

        if self.onset > 0:
            _ = sobol_engine.fast_forward(n=self.onset)

        points: np.ndarray[Any, np.dtype[np.float64]] = sobol_engine.random(  # pyright: ignore[reportUnknownMemberType]
            n=self.number_of_samples - self.number_of_bb_samples,
        )

        # Upscale points from unit hypercube to bounds
        range_lower_bounds: np.ndarray[Any, np.dtype[np.float64]] = np.array([r[0] for r in self.ranges])
        range_upper_bounds: np.ndarray[Any, np.dtype[np.float64]] = np.array([r[1] for r in self.ranges])
        sample_set: np.ndarray[Any, np.dtype[np.float64]] = qmc.scale(  # pyright: ignore[reportUnknownMemberType]
            points,
            range_lower_bounds,
            range_upper_bounds,
        )

        return sample_set

    def _generate_values_using_hilbert_sampling(self) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Source hilbertcurve pypi pkg or numpy
        it showed that hilbertcurve is a better choice and more precise with a higher iteration depth (<=15)
        pypi pkg Decimals is required for proper function up to (<=15)
        numpy approach instead has only (<=10).
        """
        # sourcery skip: extract-duplicate-method
        from math import modf

        from scipy.stats import qmc

        msg: str
        try:
            from decimal import Decimal
        except ImportError:
            msg = "no module named Decimal"
            logger.exception(msg)
            raise
        try:
            from hilbertcurve.hilbertcurve import HilbertCurve
        except ImportError:
            msg = "no module named HilbertCurve"
            logger.exception(msg)
            raise

        number_of_continuous_samples: int = self.number_of_samples - self.number_of_bb_samples

        if "_iterationDepth" in self.sampling_parameters:
            if not isinstance(self.sampling_parameters["_iterationDepth"], int):
                msg = f"_iterationDepth was not given as integer: {self.sampling_parameters['_iterationDepth']}."
                logger.error(msg)
                raise ValueError(msg)
            if self.sampling_parameters["_iterationDepth"] > self.maxIterationDepth:
                msg = (
                    f"_iterationDepth {self.sampling_parameters['_iterationDepth']} "
                    f"given in farn dict file is beyond the limit of {self.maxIterationDepth}...\n"
                    f"\t\tsetting to {self.maxIterationDepth}"
                )
                logger.warning(msg)
                self.iteration_depth = self.maxIterationDepth
            elif self.sampling_parameters["_iterationDepth"] < self.minIterationDepth:
                msg = (
                    f"_iterationDepth {self.sampling_parameters['_iterationDepth']} "
                    f"given in farn dict file is below the limit of {self.minIterationDepth}...\n"
                    f"\t\tsetting to {self.minIterationDepth}"
                )
                logger.warning(msg)
                self.iteration_depth = self.minIterationDepth
            else:
                self.iteration_depth = self.sampling_parameters["_iterationDepth"]
        else:
            self.iteration_depth = 10

        hc = HilbertCurve(self.iteration_depth, self.number_of_fields, n_procs=0)  # -1: all threads

        logger.info(
            f"The number of hilbert points is {hc.max_h}, "
            f"the number of continuous samples is {number_of_continuous_samples}"
        )
        if hc.max_h <= int(10.0 * number_of_continuous_samples):
            logger.warning(
                'Try to set or increase "_iterationDepth" gradually to achieve '
                'a number of hilbert points of about 10-times higher than "_numberOfSamples".'
            )

        distribution: np.ndarray[Any, np.dtype[np.float64]] = np.array(
            [
                Decimal(x)
                for x in np.linspace(
                    int(hc.min_h),
                    int(hc.max_h),
                    number_of_continuous_samples,
                )
            ]
        )
        int_distribution: np.ndarray[Any, np.dtype[np.int32]] = np.trunc(distribution)

        hilbert_points: Iterable[Iterable[int]] = hc.points_from_distances(int_distribution)

        _points: list[Iterable[float]] = []
        interpolation_hits = 0
        for hpt, _dst, _idst in zip(hilbert_points, distribution, int_distribution, strict=False):
            dst = float(_dst)
            idst = int(_idst)
            if dst == idst:
                _points.append(hpt)
            else:
                # interpolation starts: use idst to find integer neighbour of dst
                # nn: next neighbour
                dst_nn = idst + 1
                pt_from_dst = hpt
                pt_from_dst_nn = hc.point_from_distance(dst_nn)

                # find the index where both discrete points are different and interpolate that index
                # and create the new real-valued point
                point: list[float] = []
                for i, j in zip(pt_from_dst, pt_from_dst_nn, strict=False):
                    if i != j:
                        # non-matching index found, e.g.
                        # points are in the same dimension and need to be interpolated alongside
                        smaller_index = min(i, j)
                        fraction, _ = modf(dst)
                        # add the component to real-valued vector
                        point.append(float(smaller_index) + fraction)
                        interpolation_hits += 1
                    else:
                        point.append(float(i))

                _points.append(point)
        points: np.ndarray[Any, np.dtype[np.float64]] = np.array(_points).astype(np.float64)

        # Downscale points from hilbert space to unit hypercube [0,1)*d
        points = qmc.scale(  # pyright: ignore[reportUnknownMemberType]
            points,
            points.min(axis=0),
            points.max(axis=0),
            reverse=True,
        )

        # Upscale points from unit hypercube to bounds
        range_lower_bounds: np.ndarray[Any, np.dtype[np.float64]] = np.array([r[0] for r in self.ranges])
        range_upper_bounds: np.ndarray[Any, np.dtype[np.float64]] = np.array([r[1] for r in self.ranges])
        sample_set: np.ndarray[Any, np.dtype[np.float64]] = qmc.scale(  # pyright: ignore[reportUnknownMemberType]
            points,
            range_lower_bounds,
            range_upper_bounds,
        )

        return sample_set

    def _determine_number_of_samples(self) -> None:
        if "_includeBoundingBox" in self.sampling_parameters and isinstance(
            self.sampling_parameters["_includeBoundingBox"], bool
        ):
            self.include_bounding_box = self.sampling_parameters["_includeBoundingBox"]
        self.number_of_samples = int(self.sampling_parameters["_numberOfSamples"])
        if self.include_bounding_box is True:
            self.number_of_bb_samples = int(2**self.number_of_fields)
        self.number_of_samples += self.number_of_bb_samples
        self.leading_zeros = int(math.log10(self.number_of_samples) - 1e-06) + 1

    def _generate_case_names(
        self,
        samples: dict[str, list[Any]],
    ) -> None:
        _format_specifier: str = f"0{self.leading_zeros}d"
        self.case_names = [f"{self.layer_name}_{format(i, _format_specifier)}" for i in range(self.number_of_samples)]
        samples["_case_name"] = self.case_names

    def _check_length_matches_number_of_names(
        self,
        parameter_name: str,
    ) -> bool:
        # check that size of a list/ vector equals the size of _names
        if len(self.sampling_parameters[parameter_name]) != len(self.sampling_parameters["_names"]):
            msg: str = f"lists _names and {parameter_name}: lengths of entries do not match"
            logger.error(msg)
            return False
        return True

    def _check_consistency_of_ranges(self, ranges: Sequence[Sequence[Any]]) -> bool:
        for item in ranges:
            if len(item) != 2:  # noqa: PLR2004
                logger.error("The structure of min and max values in _ranges is inconsistent.")
                return False
        return self._check_length_matches_number_of_names("_ranges")

    def _create_bounding_box(self) -> None:
        import itertools

        tmp: list[float | Sequence[float] | Sequence[Any]] = []
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

    def _write_values_into_samples_dict(
        self,
        values: np.ndarray[Any, np.dtype[np.float64]],
        samples: dict[str, list[Any]],
    ) -> None:
        if self.include_bounding_box is True:
            self._create_bounding_box()
            values = np.concatenate(
                (
                    np.array(self.bounding_box),
                    values,
                ),
                axis=0,
            )
        for index, _ in enumerate(self.fields):
            samples[self.fields[index]] = values.T[index].tolist()
        return

    def _flatten(
        self,
        iterable: Sequence[Any],
    ) -> Generator[Any, Any, Any]:
        """Flattens sequence... happens why?."""
        for element in iterable:
            if isinstance(element, Sequence) and not isinstance(element, str | bytes):
                yield from self._flatten(element)
            else:
                yield element

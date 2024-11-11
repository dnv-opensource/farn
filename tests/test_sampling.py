from typing import Any

import numpy as np
import pytest

from farn.sampling.sampling import DiscreteSampling


def test_fixed_sampling_one_param() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling()
    sampling.set_sampling_type(sampling_type="fixed")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1"],
            "_values": [(0.9, 1.3)],
        },
        layer_name="layer0",
    )
    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 2
    assert samples.keys() == {
        "_case_name",
        "param1",
    }
    assert len(samples["_case_name"]) == 2
    assert samples["_case_name"] == ["layer0_0", "layer0_1"]
    assert len(samples["param1"]) == 2
    assert samples["param1"] == [0.9, 1.3]


def test_fixed_sampling_two_params() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling()
    sampling.set_sampling_type(sampling_type="fixed")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2"],
            "_values": [(0.9, 1.3), (-0.5, 2.7)],
        },
        layer_name="layer0",
    )
    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 3
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
    }
    assert len(samples["_case_name"]) == 2
    assert samples["_case_name"] == ["layer0_0", "layer0_1"]
    assert len(samples["param1"]) == 2
    assert samples["param1"] == [0.9, 1.3]
    assert len(samples["param2"]) == 2
    assert samples["param2"] == [-0.5, 2.7]


def test_fixed_sampling_raise_value_error_if_parameter_values_have_different_length() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling()
    sampling.set_sampling_type(sampling_type="fixed")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2"],
            "_values": [(0.9, 1.3), (-0.5, 2.7, 4.1)],
        },
        layer_name="layer0",
    )
    # Assert that ValueError is raised
    with pytest.raises(ValueError):
        _ = sampling.generate_samples()


def test_linSpace_sampling_one_parameter() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling()
    sampling.set_sampling_type(sampling_type="linSpace")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1"],
            "_ranges": [(0.5, 0.9)],
            "_numberOfSamples": 5,
        },
        layer_name="layer0",
    )
    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 2
    assert samples.keys() == {
        "_case_name",
        "param1",
    }
    assert len(samples["_case_name"]) == 5
    assert samples["_case_name"] == ["layer0_0", "layer0_1", "layer0_2", "layer0_3", "layer0_4"]
    assert len(samples["param1"]) == 5
    assert np.allclose(samples["param1"], [0.5, 0.6, 0.7, 0.8, 0.9])


def test_linSpace_sampling_two_parameters() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling()
    sampling.set_sampling_type(sampling_type="linSpace")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2"],
            "_ranges": [(0.5, 0.9), (-0.3, 0.1)],
            "_numberOfSamples": 5,
        },
        layer_name="layer0",
    )
    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 3
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
    }
    assert len(samples["_case_name"]) == 5
    assert samples["_case_name"] == ["layer0_0", "layer0_1", "layer0_2", "layer0_3", "layer0_4"]
    assert len(samples["param1"]) == 5
    assert np.allclose(samples["param1"], [0.5, 0.6, 0.7, 0.8, 0.9])
    assert len(samples["param2"]) == 5
    assert np.allclose(samples["param2"], [-0.3, -0.2, -0.1, 0.0, 0.1])


def test_uniformLhs_sampling_three_parameters() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling(seed=42)
    sampling.set_sampling_type(sampling_type="uniformLhs")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_numberOfSamples": 20,
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
    ]
    param1_values_expected: list[float] = [
        -8.401341515802963,
        -4.8165954901465655,
        -7.9419163878318,
        9.195982862419147,
        -6.291927422203955,
        6.54671027934328,
        3.4401524937396015,
        -3.568054981357883,
        0.6075448519014373,
        -9.625459881152638,
        8.597899978811085,
        1.9488855372533358,
        -1.5439300157829638,
        -0.4857655615863887,
        -2.860506139347958,
        -5.167557359199578,
        4.03438852111522,
        7.775132823361115,
        2.304613769173372,
        5.662522284353983,
    ]
    param2_values_expected: list[float] = [
        2.679549438315647,
        2.1170926199511175,
        0.9282423925179192,
        0.2023032620774264,
        3.139412314773733,
        2.609131070363787,
        2.2963566910978366,
        0.5286022865017654,
        1.5374057932437775,
        2.093985605788048,
        1.1009650995346574,
        1.6786725495508574,
        0.7371593443686983,
        1.7798417216452762,
        0.16637500362173532,
        3.3329147755593445,
        0.5015808255106138,
        1.2761253134936634,
        2.8323495297169674,
        3.3113279911290454,
    ]
    param3_values_expected: list[float] = [
        0.3636519092097309,
        0.2183450418689097,
        0.9333271545270508,
        0.45098205801870983,
        0.4975547726995999,
        0.8536037411647797,
        0.06357969861849115,
        0.7842328989880011,
        0.6976328164581687,
        0.9842155042735208,
        1.0628931681919798,
        0.74223473005612,
        0.04025966679962728,
        0.9948670876128557,
        0.5535778376141904,
        0.3038616037397731,
        0.4051499013811531,
        0.6494618541464056,
        0.1430613256458765,
        0.23000037319639055,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_uniformLhs_sampling_three_parameters_including_bounding_box() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling(seed=42)
    sampling.set_sampling_type(sampling_type="uniformLhs")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_includeBoundingBox": True,
            "_numberOfSamples": 20,
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
        "layer0_20",
        "layer0_21",
        "layer0_22",
        "layer0_23",
        "layer0_24",
        "layer0_25",
        "layer0_26",
        "layer0_27",
    ]
    param1_values_expected: list[float] = [
        -10.0,
        -10.0,
        -10.0,
        -10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        -8.401341515802963,
        -4.8165954901465655,
        -7.9419163878318,
        9.195982862419147,
        -6.291927422203955,
        6.54671027934328,
        3.4401524937396015,
        -3.568054981357883,
        0.6075448519014373,
        -9.625459881152638,
        8.597899978811085,
        1.9488855372533358,
        -1.5439300157829638,
        -0.4857655615863887,
        -2.860506139347958,
        -5.167557359199578,
        4.03438852111522,
        7.775132823361115,
        2.304613769173372,
        5.662522284353983,
    ]
    param2_values_expected: list[float] = [
        0.0,
        0.0,
        3.5,
        3.5,
        0.0,
        0.0,
        3.5,
        3.5,
        2.679549438315647,
        2.1170926199511175,
        0.9282423925179192,
        0.2023032620774264,
        3.139412314773733,
        2.609131070363787,
        2.2963566910978366,
        0.5286022865017654,
        1.5374057932437775,
        2.093985605788048,
        1.1009650995346574,
        1.6786725495508574,
        0.7371593443686983,
        1.7798417216452762,
        0.16637500362173532,
        3.3329147755593445,
        0.5015808255106138,
        1.2761253134936634,
        2.8323495297169674,
        3.3113279911290454,
    ]
    param3_values_expected: list[float] = [
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        1.1,
        0.3636519092097309,
        0.2183450418689097,
        0.9333271545270508,
        0.45098205801870983,
        0.4975547726995999,
        0.8536037411647797,
        0.06357969861849115,
        0.7842328989880011,
        0.6976328164581687,
        0.9842155042735208,
        1.0628931681919798,
        0.74223473005612,
        0.04025966679962728,
        0.9948670876128557,
        0.5535778376141904,
        0.3038616037397731,
        0.4051499013811531,
        0.6494618541464056,
        0.1430613256458765,
        0.23000037319639055,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    assert len(samples["_case_name"]) == 28
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 28
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 28
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 28
    assert np.allclose(samples["param3"], param3_values_expected)


def test_normalLhs_sampling_three_parameters() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling(seed=42)
    sampling.set_sampling_type(sampling_type="normalLhs")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            # "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_numberOfSamples": 20,
            "_mu": (0.0, 1.75, 0.55),
            "_sigma": (6.0, 1.9, 0.6),
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
    ]
    param1_values_expected: list[float] = [
        -8.433137323079436,
        -3.8754339865832215,
        -7.591054033694368,
        10.49015985878194,
        -5.3697736159228215,
        5.6621295950450365,
        2.672781672060598,
        -2.7794219658703243,
        0.457309113195083,
        -12.484682340282504,
        8.850056715494961,
        1.4804245080207765,
        -1.1683595103421323,
        -0.3655160634818963,
        -2.1993428179595877,
        -4.206564869488459,
        3.1761132231965705,
        7.319654295083616,
        1.7578707049336253,
        4.696767268691877,
    ]
    param2_values_expected: list[float] = [
        3.126333090428874,
        2.2554158395249084,
        0.5580187332707216,
        -1.2396600537794171,
        4.152552727226888,
        3.004550367329945,
        2.513510470838818,
        -0.21085543632167658,
        1.4595874802728879,
        2.2229132878996234,
        0.8323727246872478,
        1.6528995584181772,
        0.2218634771390342,
        1.7906099478279733,
        -1.421540607768644,
        4.917654877282709,
        -0.2745848991222748,
        1.0922757504787726,
        3.4127072609805866,
        4.805396097326813,
    ]
    param3_values_expected: list[float] = [
        0.2870336284886436,
        0.04179554753128967,
        1.1679596991386783,
        0.413447839324621,
        0.4781226201090167,
        1.0052589480534089,
        -0.39410942995853404,
        0.8871947314124864,
        0.7558173570294064,
        1.301286617798792,
        1.6471303278491547,
        0.8218553556088548,
        -0.5249512750842165,
        1.3343094782343585,
        0.5548918590641632,
        0.1935672833295028,
        0.34821326359046445,
        0.6871750978519323,
        -0.12567657691724599,
        0.06425292885087203,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_normalLhs_sampling_three_parameters_with_clipping() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling(seed=42)
    sampling.set_sampling_type(sampling_type="normalLhs")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_numberOfSamples": 20,
            "_mu": (0.0, 1.75, 0.55),
            "_sigma": (6.0, 1.9, 0.6),
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
    ]
    param1_values_expected: list[float] = [
        -8.433137323079436,
        -3.8754339865832215,
        -7.591054033694368,
        10.0,  # 10.49015985878194
        -5.3697736159228215,
        5.6621295950450365,
        2.672781672060598,
        -2.7794219658703243,
        0.457309113195083,
        -10.0,  # -12.484682340282504
        8.850056715494961,
        1.4804245080207765,
        -1.1683595103421323,
        -0.3655160634818963,
        -2.1993428179595877,
        -4.206564869488459,
        3.1761132231965705,
        7.319654295083616,
        1.7578707049336253,
        4.696767268691877,
    ]
    param2_values_expected: list[float] = [
        3.126333090428874,
        2.2554158395249084,
        0.5580187332707216,
        0.0,  # -1.2396600537794171
        3.5,  # 4.152552727226888
        3.004550367329945,
        2.513510470838818,
        0.0,  # -0.21085543632167658
        1.4595874802728879,
        2.2229132878996234,
        0.8323727246872478,
        1.6528995584181772,
        0.2218634771390342,
        1.7906099478279733,
        0.0,  # -1.421540607768644
        3.5,  # 4.917654877282709
        0.0,  # -0.2745848991222748
        1.0922757504787726,
        3.4127072609805866,
        3.5,  # 4.805396097326813
    ]
    param3_values_expected: list[float] = [
        0.2870336284886436,
        0.04179554753128967,
        1.1,  # 1.1679596991386783
        0.413447839324621,
        0.4781226201090167,
        1.0052589480534089,
        0.0,  # -0.39410942995853404
        0.8871947314124864,
        0.7558173570294064,
        1.1,  # 1.301286617798792
        1.1,  # 1.6471303278491547
        0.8218553556088548,
        0.0,  # -0.5249512750842165
        1.1,  # 1.3343094782343585
        0.5548918590641632,
        0.1935672833295028,
        0.34821326359046445,
        0.6871750978519323,
        0.0,  # -0.12567657691724599
        0.06425292885087203,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_sobol_sampling_three_parameters() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling(seed=42)
    sampling.set_sampling_type(sampling_type="sobol")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_numberOfSamples": 20,
            "_onset": 0,
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
    ]
    param1_values_expected: list[float] = [
        -10.0,
        0.0,
        5.0,
        -5.0,
        -2.5,
        7.5,
        2.5,
        -7.5,
        -6.25,
        3.75,
        8.75,
        -1.25,
        -3.75,
        6.25,
        1.25,
        -8.75,
        -8.125,
        1.875,
        6.875,
        -3.125,
    ]
    param2_values_expected: list[float] = [
        0.0,
        1.75,
        0.875,
        2.625,
        1.3125,
        3.0625,
        0.4375,
        2.1875,
        1.09375,
        2.84375,
        0.21875,
        1.96875,
        0.65625,
        2.40625,
        1.53125,
        3.28125,
        1.640625,
        3.390625,
        0.765625,
        2.515625,
    ]
    param3_values_expected: list[float] = [
        0.0,
        0.55,
        0.275,
        0.8250000000000001,
        0.6875,
        0.1375,
        0.9625000000000001,
        0.41250000000000003,
        1.03125,
        0.48125000000000007,
        0.7562500000000001,
        0.20625000000000002,
        0.34375,
        0.89375,
        0.06875,
        0.61875,
        0.515625,
        1.065625,
        0.24062500000000003,
        0.790625,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_sobol_sampling_three_parameters_with_onset() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling(seed=42)
    sampling.set_sampling_type(sampling_type="sobol")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_numberOfSamples": 20,
            "_onset": 10,
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
    ]
    param1_values_expected: list[float] = [
        8.75,
        -1.25,
        -3.75,
        6.25,
        1.25,
        -8.75,
        -8.125,
        1.875,
        6.875,
        -3.125,
        -0.625,
        9.375,
        4.375,
        -5.625,
        -6.875,
        3.125,
        8.125,
        -1.875,
        -4.375,
        5.625,
    ]

    param2_values_expected: list[float] = [
        0.21875,
        1.96875,
        0.65625,
        2.40625,
        1.53125,
        3.28125,
        1.640625,
        3.390625,
        0.765625,
        2.515625,
        0.328125,
        2.078125,
        1.203125,
        2.953125,
        0.546875,
        2.296875,
        1.421875,
        3.171875,
        0.984375,
        2.734375,
    ]

    param3_values_expected: list[float] = [
        0.7562500000000001,
        0.20625000000000002,
        0.34375,
        0.89375,
        0.06875,
        0.61875,
        0.515625,
        1.065625,
        0.24062500000000003,
        0.790625,
        0.9281250000000001,
        0.37812500000000004,
        0.6531250000000001,
        0.10312500000000001,
        0.5843750000000001,
        0.034375,
        0.8593750000000001,
        0.309375,
        0.171875,
        0.721875,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    # print(repr(samples["param1"]))
    # print(repr(samples["param2"]))
    # print(repr(samples["param3"]))
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_sobol_sampling_three_parameters_including_bounding_box() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling(seed=42)
    sampling.set_sampling_type(sampling_type="sobol")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_numberOfSamples": 20,
            "_onset": 0,
            "_includeBoundingBox": True,
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
        "layer0_20",
        "layer0_21",
        "layer0_22",
        "layer0_23",
        "layer0_24",
        "layer0_25",
        "layer0_26",
        "layer0_27",
    ]
    param1_values_expected: list[float] = [
        -10.0,
        -10.0,
        -10.0,
        -10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        -10.0,
        0.0,
        5.0,
        -5.0,
        -2.5,
        7.5,
        2.5,
        -7.5,
        -6.25,
        3.75,
        8.75,
        -1.25,
        -3.75,
        6.25,
        1.25,
        -8.75,
        -8.125,
        1.875,
        6.875,
        -3.125,
    ]
    param2_values_expected: list[float] = [
        0.0,
        0.0,
        3.5,
        3.5,
        0.0,
        0.0,
        3.5,
        3.5,
        0.0,
        1.75,
        0.875,
        2.625,
        1.3125,
        3.0625,
        0.4375,
        2.1875,
        1.09375,
        2.84375,
        0.21875,
        1.96875,
        0.65625,
        2.40625,
        1.53125,
        3.28125,
        1.640625,
        3.390625,
        0.765625,
        2.515625,
    ]
    param3_values_expected: list[float] = [
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        0.55,
        0.275,
        0.8250000000000001,
        0.6875,
        0.1375,
        0.9625000000000001,
        0.41250000000000003,
        1.03125,
        0.48125000000000007,
        0.7562500000000001,
        0.20625000000000002,
        0.34375,
        0.89375,
        0.06875,
        0.61875,
        0.515625,
        1.065625,
        0.24062500000000003,
        0.790625,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    assert len(samples["_case_name"]) == 28
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 28
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 28
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 28
    assert np.allclose(samples["param3"], param3_values_expected)


def test_hilbertCurve_sampling_three_parameters() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling()
    sampling.set_sampling_type(sampling_type="hilbertCurve")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_numberOfSamples": 20,
            # "_iterationDepth": 5,
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
    ]
    param1_values_expected: list[float] = [
        -10.0,
        -2.0625610948191593,
        -10.0,
        -2.9114575295154648,
        -1.8084066471163247,
        -10.0,
        -0.9872922776148574,
        -3.978494623655914,
        -5.562072336265885,
        -8.030560271830852,
        8.03056027066556,
        5.562072336265885,
        3.978494623655914,
        0.9872922776148574,
        10.0,
        1.8084066471163247,
        2.911457528350173,
        10.0,
        2.0625610948191593,
        10.0,
    ]
    param2_values_expected: list[float] = [
        0.0,
        0.7426904253928639,
        1.773277701078467,
        0.0,
        1.1724494917718806,
        3.020830719013671,
        3.4971451875496222,
        2.5076232902309616,
        3.388881917286891,
        2.720416614360378,
        2.720416614360378,
        3.391297527764435,
        2.5076232902309616,
        3.5,
        3.020830719013671,
        1.1724494917718806,
        0.0,
        1.773277701078467,
        0.7426904253928639,
        0.0,
    ]
    param3_values_expected: list[float] = [
        0.0,
        0.14691640866416344,
        0.4258328173283269,
        1.1,
        1.061312693480183,
        0.8756408668405871,
        0.7971764705882354,
        0.7359442723849241,
        0.462,
        0.27047058823529413,
        0.27047058823529413,
        0.462,
        0.7354674922438229,
        0.7971764705882354,
        0.8753003094757306,
        1.0623343652276434,
        1.1,
        0.4269907120255863,
        0.14684829718926376,
        0.0,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_hilbertCurve_sampling_three_parameters_with_iteration_depth() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling()
    sampling.set_sampling_type(sampling_type="hilbertCurve")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_numberOfSamples": 20,
            "_iterationDepth": 5,
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
    ]
    param1_values_expected: list[float] = [
        -10.0,
        -1.8845500848896517,
        -9.898132427843818,
        -2.903225806451613,
        -1.612903225806452,
        -10.0,
        -0.9677419354838719,
        -4.193548387096774,
        -5.72156196943979,
        -8.064516129032258,
        8.064516129032256,
        5.721561969438616,
        4.193548387096774,
        0.9677419354838701,
        10.0,
        1.612903225806452,
        2.903225806451612,
        9.898132427842938,
        1.8845500848903836,
        10.0,
    ]
    param2_values_expected: list[float] = [
        0.0,
        0.6597222222222319,
        1.7152777777778028,
        0.0,
        1.0972222222222319,
        3.0208333333333393,
        3.493055555555657,
        2.3750000000000346,
        3.298611111111159,
        2.6388888888889275,
        2.6388888888889275,
        3.298611111111159,
        2.3750000000000346,
        3.5000000000000004,
        2.916666666666507,
        1.1458333333334763,
        0.0,
        1.7152777777778028,
        0.6597222222222319,
        0.0,
    ]
    param3_values_expected: list[float] = [
        0.0,
        0.12342519685039283,
        0.4114173228346427,
        1.1,
        1.0285433070866068,
        0.8639763779527497,
        0.7816929133858211,
        0.6604330708661055,
        0.452559055118107,
        0.25551181102364384,
        0.2793307086613917,
        0.452559055118107,
        0.6972440944882156,
        0.7816929133858211,
        0.8639763779527497,
        1.0285433070866068,
        1.0805118110236065,
        0.4114173228346427,
        0.12342519685039283,
        0.0,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_hilbertCurve_sampling_three_parameters_including_bounding_box() -> None:
    # Prepare
    sampling: DiscreteSampling = DiscreteSampling()
    sampling.set_sampling_type(sampling_type="hilbertCurve")
    sampling.set_sampling_parameters(
        sampling_parameters={
            "_names": ["param1", "param2", "param3"],
            "_ranges": [(-10.0, 10.0), (0.0, 3.5), (0.0, 1.1)],
            "_numberOfSamples": 20,
            "_includeBoundingBox": True,
        },
        layer_name="layer0",
    )
    case_names_expected: list[str] = [
        "layer0_00",
        "layer0_01",
        "layer0_02",
        "layer0_03",
        "layer0_04",
        "layer0_05",
        "layer0_06",
        "layer0_07",
        "layer0_08",
        "layer0_09",
        "layer0_10",
        "layer0_11",
        "layer0_12",
        "layer0_13",
        "layer0_14",
        "layer0_15",
        "layer0_16",
        "layer0_17",
        "layer0_18",
        "layer0_19",
        "layer0_20",
        "layer0_21",
        "layer0_22",
        "layer0_23",
        "layer0_24",
        "layer0_25",
        "layer0_26",
        "layer0_27",
    ]
    param1_values_expected: list[float] = [
        -10.0,
        -10.0,
        -10.0,
        -10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        -10.0,
        -2.0625610948191593,
        -10.0,
        -2.9114575295154648,
        -1.8084066471163247,
        -10.0,
        -0.9872922776148574,
        -3.978494623655914,
        -5.562072336265885,
        -8.030560271830852,
        8.03056027066556,
        5.562072336265885,
        3.978494623655914,
        0.9872922776148574,
        10.0,
        1.8084066471163247,
        2.911457528350173,
        10.0,
        2.0625610948191593,
        10.0,
    ]
    param2_values_expected: list[float] = [
        0.0,
        0.0,
        3.5,
        3.5,
        0.0,
        0.0,
        3.5,
        3.5,
        0.0,
        0.7426904253928639,
        1.773277701078467,
        0.0,
        1.1724494917718806,
        3.020830719013671,
        3.4971451875496222,
        2.5076232902309616,
        3.388881917286891,
        2.720416614360378,
        2.720416614360378,
        3.391297527764435,
        2.5076232902309616,
        3.5,
        3.020830719013671,
        1.1724494917718806,
        0.0,
        1.773277701078467,
        0.7426904253928639,
        0.0,
    ]
    param3_values_expected: list[float] = [
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        0.14691640866416344,
        0.4258328173283269,
        1.1,
        1.061312693480183,
        0.8756408668405871,
        0.7971764705882354,
        0.7359442723849241,
        0.462,
        0.27047058823529413,
        0.27047058823529413,
        0.462,
        0.7354674922438229,
        0.7971764705882354,
        0.8753003094757306,
        1.0623343652276434,
        1.1,
        0.4269907120255863,
        0.14684829718926376,
        0.0,
    ]

    # Execute
    samples: dict[str, list[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    # print(repr(samples["param1"]))
    # print(repr(samples["param2"]))
    # print(repr(samples["param3"]))
    assert len(samples["_case_name"]) == 28
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 28
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 28
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 28
    assert np.allclose(samples["param3"], param3_values_expected)

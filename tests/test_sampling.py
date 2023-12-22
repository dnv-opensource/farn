from typing import Any, Dict, List

import numpy as np
import pytest

from farn.sampling.sampling import DiscreteSampling


def test_fixed_sampling_one_param():
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
    samples: Dict[str, List[Any]] = sampling.generate_samples()
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


def test_fixed_sampling_two_params():
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
    samples: Dict[str, List[Any]] = sampling.generate_samples()
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


def test_fixed_sampling_raise_value_error_if_parameter_values_have_different_length():
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


def test_linSpace_sampling_one_parameter():
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
    samples: Dict[str, List[Any]] = sampling.generate_samples()
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


def test_linSpace_sampling_two_parameters():
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
    samples: Dict[str, List[Any]] = sampling.generate_samples()
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


def test_uniformLhs_sampling_three_parameters():
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
    case_names_expected: List[str] = [
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
    param1_values_expected: List[float] = [
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
    param2_values_expected: List[float] = [
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
    param3_values_expected: List[float] = [
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
    samples: Dict[str, List[Any]] = sampling.generate_samples()
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
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_uniformLhs_sampling_three_parameters_including_bounding_box():
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
    case_names_expected: List[str] = [
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
    param1_values_expected: List[float] = [
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
    param2_values_expected: List[float] = [
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
    param3_values_expected: List[float] = [
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
    samples: Dict[str, List[Any]] = sampling.generate_samples()
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


def test_normalLhs_sampling_three_parameters():
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
    case_names_expected: List[str] = [
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
    param1_values_expected: List[float] = [
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
    param2_values_expected: List[float] = [
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
    param3_values_expected: List[float] = [
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
    samples: Dict[str, List[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    print(repr(samples["param1"]))
    print(repr(samples["param2"]))
    print(repr(samples["param3"]))
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_normalLhs_sampling_three_parameters_with_clipping():
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
    case_names_expected: List[str] = [
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
    param1_values_expected: List[float] = [
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
    param2_values_expected: List[float] = [
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
    param3_values_expected: List[float] = [
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
    samples: Dict[str, List[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    print(repr(samples["_case_name"]))
    print(repr(samples["param1"]))
    print(repr(samples["param2"]))
    print(repr(samples["param3"]))
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_sobol_sampling_three_parameters():
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
    case_names_expected: List[str] = [
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
    param1_values_expected: List[float] = [
        2.220446049250313e-16,
        5.7142857142857135,
        -5.714285714285714,
        -2.8571428571428577,
        8.571428571428571,
        2.8571428571428577,
        -8.571428571428571,
        -7.142857142857143,
        4.2857142857142865,
        10.000000000000002,
        -1.4285714285714286,
        -4.285714285714286,
        7.142857142857144,
        1.428571428571429,
        -10.0,
        -9.285714285714286,
        2.1428571428571423,
        7.857142857142856,
        -3.571428571428571,
        -0.7142857142857133,
    ]
    param2_values_expected: List[float] = [
        1.6896551724137931,
        0.7241379310344828,
        2.6551724137931036,
        1.206896551724138,
        3.137931034482759,
        0.2413793103448276,
        2.1724137931034484,
        0.9655172413793103,
        2.8965517241379315,
        0.0,
        1.9310344827586208,
        0.48275862068965514,
        2.4137931034482762,
        1.4482758620689655,
        3.3793103448275867,
        1.5689655172413794,
        3.5000000000000004,
        0.603448275862069,
        2.53448275862069,
        0.12068965517241378,
    ]
    param3_values_expected: List[float] = [
        0.55,
        0.8642857142857144,
        0.23571428571428577,
        0.7071428571428572,
        0.07857142857142858,
        0.39285714285714296,
        1.0214285714285716,
        0.31428571428571433,
        0.942857142857143,
        0.6285714285714287,
        0.0,
        1.1000000000000003,
        0.4714285714285715,
        0.1571428571428572,
        0.7857142857142858,
        0.9821428571428573,
        0.35357142857142865,
        0.0392857142857143,
        0.6678571428571429,
        0.5107142857142858,
    ]

    # Execute
    samples: Dict[str, List[Any]] = sampling.generate_samples()
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


def test_sobol_sampling_three_parameters_with_onset():
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
    case_names_expected: List[str] = [
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
    param1_values_expected: List[float] = [
        -1.724137931034483,
        -4.482758620689655,
        6.5517241379310365,
        1.0344827586206913,
        -10.0,
        -9.310344827586206,
        1.724137931034483,
        7.24137931034483,
        -3.793103448275862,
        -1.0344827586206895,
        10.0,
        4.482758620689656,
        -6.551724137931035,
        -7.93103448275862,
        3.1034482758620703,
        8.620689655172413,
        -2.413793103448275,
        -5.1724137931034475,
        5.862068965517243,
        0.3448275862068977,
    ]
    param2_values_expected: List[float] = [
        1.9833333333333334,
        0.5833333333333333,
        2.45,
        1.5166666666666666,
        3.3833333333333333,
        1.6333333333333333,
        3.5,
        0.7,
        2.566666666666667,
        0.2333333333333333,
        2.1,
        1.1666666666666667,
        3.033333333333333,
        0.4666666666666667,
        2.3333333333333335,
        1.4,
        3.2666666666666666,
        0.9333333333333333,
        2.8,
        0.0,
    ]
    param3_values_expected: List[float] = [
        0.03666666666666667,
        1.0633333333333335,
        0.4766666666666666,
        0.18333333333333335,
        0.77,
        0.9533333333333334,
        0.36666666666666664,
        0.07333333333333333,
        0.66,
        0.5133333333333334,
        1.1,
        0.8066666666666668,
        0.21999999999999997,
        0.5866666666666667,
        0.0,
        0.29333333333333333,
        0.88,
        0.14666666666666667,
        0.7333333333333334,
        1.0266666666666666,
    ]

    # Execute
    samples: Dict[str, List[Any]] = sampling.generate_samples()
    # Assert
    assert len(samples) == 4
    assert samples.keys() == {
        "_case_name",
        "param1",
        "param2",
        "param3",
    }
    print(repr(samples["param1"]))
    print(repr(samples["param2"]))
    print(repr(samples["param3"]))
    assert len(samples["_case_name"]) == 20
    assert samples["_case_name"] == case_names_expected
    assert len(samples["param1"]) == 20
    assert np.allclose(samples["param1"], param1_values_expected)
    assert len(samples["param2"]) == 20
    assert np.allclose(samples["param2"], param2_values_expected)
    assert len(samples["param3"]) == 20
    assert np.allclose(samples["param3"], param3_values_expected)


def test_sobol_sampling_three_parameters_including_bounding_box():
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
    case_names_expected: List[str] = [
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
    param1_values_expected: List[float] = [
        -10.0,
        -10.0,
        -10.0,
        -10.0,
        10.0,
        10.0,
        10.0,
        10.0,
        2.220446049250313e-16,
        5.7142857142857135,
        -5.714285714285714,
        -2.8571428571428577,
        8.571428571428571,
        2.8571428571428577,
        -8.571428571428571,
        -7.142857142857143,
        4.2857142857142865,
        10.000000000000002,
        -1.4285714285714286,
        -4.285714285714286,
        7.142857142857144,
        1.428571428571429,
        -10.0,
        -9.285714285714286,
        2.1428571428571423,
        7.857142857142856,
        -3.571428571428571,
        -0.7142857142857133,
    ]
    param2_values_expected: List[float] = [
        0.0,
        0.0,
        3.5,
        3.5,
        0.0,
        0.0,
        3.5,
        3.5,
        1.6896551724137931,
        0.7241379310344828,
        2.6551724137931036,
        1.206896551724138,
        3.137931034482759,
        0.2413793103448276,
        2.1724137931034484,
        0.9655172413793103,
        2.8965517241379315,
        0.0,
        1.9310344827586208,
        0.48275862068965514,
        2.4137931034482762,
        1.4482758620689655,
        3.3793103448275867,
        1.5689655172413794,
        3.5000000000000004,
        0.603448275862069,
        2.53448275862069,
        0.12068965517241378,
    ]
    param3_values_expected: List[float] = [
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        1.1,
        0.0,
        1.1,
        0.55,
        0.8642857142857144,
        0.23571428571428577,
        0.7071428571428572,
        0.07857142857142858,
        0.39285714285714296,
        1.0214285714285716,
        0.31428571428571433,
        0.942857142857143,
        0.6285714285714287,
        0.0,
        1.1000000000000003,
        0.4714285714285715,
        0.1571428571428572,
        0.7857142857142858,
        0.9821428571428573,
        0.35357142857142865,
        0.0392857142857143,
        0.6678571428571429,
        0.5107142857142858,
    ]

    # Execute
    samples: Dict[str, List[Any]] = sampling.generate_samples()
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

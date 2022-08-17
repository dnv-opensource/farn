import logging
import os
import platform
import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, MutableMapping, MutableSequence, MutableSet, Sequence, Union

from dictIO import CppDict, DictReader, DictWriter, create_target_file_name
from dictIO.utils.strings import remove_quotes

from farn.run.subProcess import execute_in_sub_process
from farn.run.batchProcess import AsyncBatchProcessor
from farn.utils.logging import plural
from farn.utils.os import append_system_variable


__ALL__ = [
    'run_farn',
    'Parameter',
    'Case',
    'create_samples',
    'create_case_folders',
    'create_param_dict_files',
    'create_case_list_files',
    'execute_command_set',
]

logger = logging.getLogger(__name__)


def run_farn(
    farn_dict_file: Union[str, os.PathLike[str]],
    sample: bool = False,
    generate: bool = False,
    command: Union[str, None] = None,
    batch: bool = False,
    test: bool = False,
):
    """Runs farn.

    Runs the sampling for all layers as configured in farn dict,
    generates the corresponding case folder structure and
    executes user-defined shell command sets in all case folders.

    Parameters
    ----------
    farn_dict_file : Union[str, os.PathLike[str]]
        farnDict file. Contains the farn configuration.
    sample : bool, optional
        if True, runs the sampling defined for each layer and saves the sampled farnDict file with prefix sampled., by default False
    generate : bool, optional
        if True, generates the folder structure that spawns all layers and cases defined in farnDict, by default False
    command : Union[str, None], optional
        executes the given command set in all case folders. The command set must be defined in the commands section of the applicable layer in farnDict., by default None
    batch : bool, optional
        if True, executes the given command set in batch mode, i.e. asynchronously, by default False
    test : bool, optional
        if True, runs only first case and returns, by default False

    Raises
    ------
    FileNotFoundError
        if farn_dict_file does not exist
    """

    # Make sure farn_dict_file argument is of type Path. If not, cast it to Path type.
    farn_dict_file = farn_dict_file if isinstance(farn_dict_file, Path) else Path(farn_dict_file)

    # Check whether farn dict file exists
    if not farn_dict_file.exists():
        logger.error(f"run_farn: File {farn_dict_file} not found.")
        raise FileNotFoundError(farn_dict_file)

    # Set up farn environment
    farn_dirs: MutableMapping = _set_up_farn_environment(farn_dict_file)

    # Read farn dict
    farn_dict = DictReader.read(farn_dict_file, comments=False)

    # Run sampling and create the samples for all layers in farn dict
    if sample:
        create_samples(farn_dict)                                               # run sampling
        farn_dict.source_file = create_target_file_name(                        # change filename to 'sampled.*'
            farn_dict.source_file,                                              # type: ignore
            prefix='sampled.'
        )
        logger.info(f'Save sampled farn dict {farn_dict.name}...')              # 1
        DictWriter.write(farn_dict, mode='w')                                   # save sampled.* farn dict file
        logger.info(f'Saved sampled farn dict in {farn_dict.source_file}.')     # 1

    # Document CLI arguments of current farn call in the farn dict (for traceability)
    farn_opts = {
        'farnDict': farn_dict.name,
        'sample': sample,
        'generate': generate,
        'execute': command,
        'test': test
    }
    farn_dict.update({'_farnOpts': farn_opts})

    # Create all valid cases from the samples defined in farn dict.
    cases = create_cases(
        farn_dict=farn_dict,
        case_dir=farn_dirs['CASEDIR'],
        valid_only=True,
    )

    # Generate case folder structure
    # and create a case-specific paramDict file in each case folder
    if generate:
        create_case_folders(cases)
        create_param_dict_files(cases)
        create_case_list_files(
            cases=cases,
            target_dir=farn_dirs['ROOTDIR'],
        )

    # Execute a given command set in all case folders
    if command:
        execute_command_set(
            cases=cases,
            command_set=command,
            batch=batch,
            test=test,
        )

    logger.info('Successfully finished farn.\n')


@dataclass
class Parameter:
    """Dataclass holding the parameter attributes 'name' and 'value'
    """
    name: Union[str, None] = None
    value: Union[float, None] = None


@dataclass
class Case:
    """Dataclass holding case attributes

    The dataclass 'Case' holds all relevant case attributes needed by farn to process cases, e.g.
        - condition
        - parameter names and associated values
        - commands
        - ..
    """
    case: Union[str, None] = None
    layer: Union[str, None] = None
    level: int = 0
    no_of_samples: int = 0
    index: int = 0
    path: Path = Path.cwd()
    is_leaf: bool = False
    condition: Union[MutableMapping, None] = None
    parameters: Union[MutableSequence[Parameter], None] = None
    command_sets: Union[MutableMapping, None] = None

    @property
    def is_valid(self) -> bool:
        """Evaluates whether the case matches the configured filter expression.

        A case is considered valid if it fulfils the filter citeria configured in farnDict for the respective layer.

        Returns
        -------
        bool
            result of validity check. True indicates the case is valid, False not valid.
        """

        # Check whether the '_condition' element is defined.  Without it, case is in any case considered valid.
        if not self.condition or not isinstance(self.condition, MutableMapping):
            return True

        # Check whether filter expression is defined.
        # If filter expression is missing, condition cannot be evaluated but case is, by default, still considered valid.
        filter_expression = self.condition['_filter'] if '_filter' in self.condition else None
        if not filter_expression:
            logger.warning(
                f"Layer {self.layer}: _condition element found but no _filter element defined therein. "
                f"As the filter expression is missing, the condition cannot be evalued. Case {self.case} is hence considered valid. "
            )
            return True

        # Check whether optional argument '_action' is defined. Use default action, if not.
        action = self.condition['_action'] if '_action' in self.condition else None
        if not action:
            logger.warning(
                f"Layer {self.layer}: No _action defined in _condition element. Default action 'exclude' is used. "
            )
            action = 'exclude'

        # Check for formal errors that lead to invalidity
        if not self.parameters:
            logger.warning(
                f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                f"A filter expression {filter_expression} is defined, but no parameters exist. "
            )
            return False
        for parameter in self.parameters:
            if not parameter.name:
                logger.warning(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                    f"A filter expression {filter_expression} is defined, "
                    f"but at least one parameter name is missing. "
                )
                return False
            if not parameter.value:
                logger.warning(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                    f"A filter expression {filter_expression} is defined and parameter names exist, "
                    f"but parameter values are missing. "
                    f"Parameter name: {parameter.name} "
                    f"Parameter value: None "
                )
                return False

        # transfer a white list of case properties to locals() for subsequent filtering
        available_vars = set()
        for attribute in dir(self):
            try:
                if attribute in [
                    'case',
                    'layer',
                    'level',
                    'index',
                    'path'
                    'is_leaf',
                    'no_of_samples',
                    'condition',
                    'command_sets',
                ]:
                    locals()[attribute] = eval(f'self.{attribute}')
                    available_vars.add(attribute)
            except Exception:
                logger.exception(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                    f"Reading case property '{attribute}' failed."
                )
                return False

        # Read all parameter names and their associated values defined in current case, and assign them to local in-memory variables
        for parameter in self.parameters:
            if parameter.name and not re.match('^_', parameter.name):
                try:
                    exec(f'{parameter.name} = {parameter.value}')
                    available_vars.add(parameter.name)
                except Exception:
                    logger.exception(
                        f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                        f"Reading parameter {parameter.name} with value {parameter.value} failed. "
                    )
                    return False

        logger.debug(
            f"Layer {self.layer}, available filter variables in current scope: {'{'+', '.join(available_vars)+'}'}"
        )

        # Evaluate filter expression
        filter_expression_evaluates_to_true = False
        try:
            filter_expression_evaluates_to_true = eval(filter_expression)
        except Exception:
            # In case evaluation of the filter expression fails, processing will not stop.
            # However, a warning will be logged and the respective case will be considered valid.
            logger.warning(
                f"Layer {self.layer}, case {self.case} evaluation of the filter expression failed:\n"
                f"\tOne or more of the variables used in the filter expression are not defined or not accessible in the current layer.\n"
                f"\t\tLayer: {self.layer}\n"
                f"\t\tLevel: {self.level}\n"
                f"\t\tCase: {self.case}\n"
                f"\t\tFilter expression: {filter_expression}\n"
                f"\t\tParameter names: {[parameter.name for parameter in self.parameters]}\n"
                f"\t\tParameter values: {[parameter.value for parameter in self.parameters]} "
            )

        # Finally: Determine case validity based on filter expression and action
        if action == 'exclude':
            if filter_expression_evaluates_to_true:
                logger.debug(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid:\n"
                    f"\tThe filter expression '{filter_expression}' evaluated to True.\n"
                    f"\tAction '{action}' performed. Case {self.case} excluded."
                )
                return False
            return True
        if action == 'include':
            if filter_expression_evaluates_to_true:
                logger.debug(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is valid:\n"
                    f"\tThe filter expression '{filter_expression}' evaluated to True.\n"
                    f"\tAction '{action}' performed. Case {self.case} included."
                )
                return True
            return False

        return True

    def to_dict(self) -> dict:
        """Returns a dict with all case attributes

        Returns
        -------
        dict
            dict with all case attributes
        """
        return {
            '_case': self.case,
            '_layer': self.layer,
            '_level': self.level,
            '_index': self.index,
            '_path': self.path,
            '_is_leaf': self.is_leaf,
            '_no_of_samples': self.no_of_samples,
            '_condition': self.condition,
            '_parameters':
            {parameter.name: parameter.value
             for parameter in self.parameters or []},
            '_commands': self.command_sets,
        }


def create_samples(farn_dict: CppDict):
    """Run sampling and create the samples inside all layers of the passed in farn dict.

    Creates the _samples element in each layer and populates it with the discrete samples generated for the parameters defined and varied in the respective layer.
    In case the _samples element already exists in a layer, it will be overwritten.

    Parameters
    ----------
    farn_dict : CppDict
        farn dict the samples shall be created in
    """
    from farn.sampling.sampling import DiscreteSampling

    if '_layers' not in farn_dict:
        logger.error(f"no '_layers' element in farn dict {farn_dict.name}. Sampling not possible.")
        return

    def create_samples_in_layer(level: int, layer_name: str, layer: MutableMapping):
        '''
        runs sampling and generates the samples in the passed in layer
        '''
        if '_sampling' not in layer:
            logger.error("no '_sampling' element in layer")
            return
        if '_type' not in layer['_sampling']:
            logger.error("no '_type' element in sampling")
            return

        # instantiate and parameterize the sampling object
        sampling = DiscreteSampling()
        sampling.set_sampling_type(sampling_type=layer['_sampling']['_type'])
        sampling.set_sampling_parameters(base_name=layer_name, kwargs=layer['_sampling'])

        # in case a _samples element already exists (e.g. from a former run) -> delete it
        if '_samples' in layer:
            del layer['_samples']

        # generate the samples and write them into the _samples element of the layer
        samples = sampling.generate()
        layer['_samples'] = samples

        # if the layer does not have a _comment element yet: create a default comment
        if '_comment' not in layer:
            default_comment = f'level {level:2d}, layer {layer_name}'
            layer['_comment'] = default_comment

        return

    logger.info(f'Run sampling of {farn_dict.name}...')

    for index, (key, value) in enumerate(farn_dict['_layers'].items()):
        create_samples_in_layer(
            level=index,
            layer_name=key,
            layer=value,
        )

    logger.info(f'Successfully ran sampling of {farn_dict.name}.')

    return


def create_cases(
    farn_dict: MutableMapping,
    case_dir: Path,
    valid_only: bool = False,
) -> list[Case]:
    """Creates cases based on the layers, filter expressions and samples defined in the passed farn dict.

    Creates case objects for all cases derived by recursive permutation of layers and the case specific samples defined per layer.
    create_cases() creates one distinct case object for each case, holding all case attributes (parameters) set to their case specific values.

    Optionally, only _valid_ cases can be returned, i.e. cases which fulfill the filter criteria configured for the respective layer.
    Invalid cases then get excluded.

    Note:
    The corresponding case folder structure is not yet created by create_cases().
    Creating the case folder structure is the responsibility of create_case_folder_structure().
    However, the case_dir argument is passed in to allow create_cases() to already document in each case object
    its _intended_ case folder path. This information is then read and used in create_case_folder_structure()
    to actually create the case folders.

    Parameters
    ----------
    farn_dict : MutableMapping
        farn dict. The farn dict must be sampled, e.g. samples must have been generated for all layers defined in the farn dict.
    case_dir : Path
        directory the case folder structure is (intended) to be generated in.
    valid_only: bool
        whether or not only valid cases shall be returned, i.e. cases which fulfill the filter criteria configured for the respective layer., by default False

    Returns
    -------
    list[Case]
        list of case objects representing all created cases.
    """
    log_msg: str = 'List all valid cases..' if valid_only else 'List all cases..'
    logger.info(log_msg)

    # Check arguments.
    if '_layers' not in farn_dict:
        logger.error("create_cases: No '_layers' element contained in farn dict.")
        return []

    # Initialize cases list
    cases: list[Case] = []
    number_of_invalid_cases: int = 0

    # Create a local layers list that carries also the layers' name
    # to ease sequential and indexed access to individual layers in create_next_level_cases()
    layers: MutableSequence[MutableMapping] = []
    for layer_name, layer in farn_dict['_layers'].items():
        layer_copy = deepcopy(layer)
        layer_copy['_name'] = layer_name
        layers.append(layer_copy)

    def create_next_level_cases(
        level: int = 0,
        base_case: Union[Case, None] = None,
    ):
        nonlocal cases
        nonlocal number_of_invalid_cases
        nonlocal layers

        base_case = base_case or Case(path=Path.cwd())
        base_case.parameters = base_case.parameters or []

        current_layer: MutableMapping = layers[level]
        # validity checks for current layer
        if '_samples' not in current_layer:
            logger.warning(
                f"No _samples element found in layer {current_layer['_name']}.\n"
                f"Creation of cases for level {level:2d} aborted. "
            )
            return
        if '_case_name' not in current_layer['_samples']:
            logger.warning(
                f"The _samples element in layer {current_layer['_name']} is empty or does not have a _case_name element.\n"
                f"Creation of cases for level {level:2d} aborted. "
            )
            return

        current_layer_name: str = current_layer['_name']
        current_layer_is_leaf: bool = (level == len(layers) - 1)

        no_of_samples_in_current_layer: int = len(current_layer['_samples']['_case_name'])
        samples_in_current_layer: MutableMapping[str, MutableSequence[float]] = {
            param_name: param_values
            for param_name,
            param_values in current_layer['_samples'].items()
            if param_name != '_case_name'
        }

        parameter_names_used_in_preceeding_layers: MutableSet[str] = {
            parameter.name
            for parameter in base_case.parameters
            if parameter.name
        }

        parameter_names_in_current_layer: MutableSequence[str] = []
        for parameter_name in list(samples_in_current_layer.keys()):
            if parameter_name in parameter_names_used_in_preceeding_layers:
                logger.warning(
                    f'The parameter {parameter_name} defined in layer {current_layer_name} had already been defined in a preceeding layer.\n'
                    f'The preceeding definition prevails. The samples for parameter {parameter_name} defined in layer {current_layer_name} are skipped. '
                )
            else:
                parameter_names_in_current_layer.append(parameter_name)

        user_variables_in_current_layer: MutableSequence[Parameter] = []
        for key, item in current_layer.items():
            if not key.startswith('_'):
                user_variable = Parameter(name=key, value=item)
                if user_variable.name in parameter_names_used_in_preceeding_layers:
                    logger.warning(
                        f'The user variable {user_variable.name} defined in layer {current_layer_name} matches a parameter that\n'
                        f'had already been defined in a preceeding layer.\n'
                        f'The preceeding definition prevails. The user variable {user_variable.name} defined in layer {current_layer_name} is skipped. '
                    )
                elif user_variable.name in parameter_names_in_current_layer:
                    logger.warning(
                        f'The user variable {user_variable.name} defined in layer {current_layer_name} matches a parameter name defined in the same layer.\n'
                        f'The preceeding definition prevails. The user variable {user_variable.name} defined in layer {current_layer_name} is skipped. '
                    )
                else:
                    user_variables_in_current_layer.append(user_variable)

        condition_in_current_layer: Union[
            MutableMapping,
            None] = current_layer['_condition'] if '_condition' in current_layer else None
        commands_in_current_layer: Union[
            MutableMapping,
            None] = current_layer['_commands'] if '_commands' in current_layer else None

        for index, case_name in enumerate(current_layer['_samples']['_case_name']):
            case_name = remove_quotes(case_name)

            case_parameters: MutableSequence[Parameter] = [
                parameter for parameter in base_case.parameters if parameter.name
            ]
            case_parameters.extend(
                Parameter(parameter_name, samples_in_current_layer[parameter_name][index])
                for parameter_name in parameter_names_in_current_layer
            )
            case_parameters.extend(user_variables_in_current_layer)

            case = Case(
                case=case_name,
                layer=current_layer_name,
                level=level,
                no_of_samples=no_of_samples_in_current_layer,
                index=index,
                path=base_case.path / case_name,
                is_leaf=current_layer_is_leaf,
                condition=condition_in_current_layer,
                parameters=case_parameters,
                command_sets=commands_in_current_layer,
            )

            if not valid_only or case.is_valid:
                cases.append(case)
                if not case.is_leaf:            # Recursion for next level cases
                    create_next_level_cases(
                        level=level + 1,
                        base_case=case,
                    )
            else:
                number_of_invalid_cases += 1

        return

    # Commence recursive collection of cases among all layers
    base_case = Case(path=case_dir)
    create_next_level_cases(level=0, base_case=base_case)

    leaf_cases = [case for case in cases if case.is_leaf]

    log_msg = ''
    if valid_only:
        log_msg = (
            f'Successfully listed {len(leaf_cases)} valid case{plural(len(leaf_cases))}. '
            f'{number_of_invalid_cases} invalid case{plural(number_of_invalid_cases)} {plural(number_of_invalid_cases, "were")} excluded.'
        )
    else:
        log_msg = (f'Successfully listed {len(leaf_cases)} case{plural(len(leaf_cases))}. ')
    logger.info(log_msg)

    return cases


def create_case_folders(cases: MutableSequence[Case]) -> int:
    """Creates the case folder structure for the passed in cases.

    Parameters
    ----------
    cases : MutableSequence[Case]
        cases the case folders shall be created for.

    Returns
    -------
    int
        number of case folders created.
    """

    logger.info('Create case folder structure...')
    number_of_case_folders_created: int = 0

    for case in cases:
        logger.debug(f"creating case folder {case.path}")   # 1
        case.path.mkdir(parents=True, exist_ok=True)
        number_of_case_folders_created += 1

    logger.info(f'Successfully created {number_of_case_folders_created} case folders.')

    return number_of_case_folders_created


def create_param_dict_files(cases: MutableSequence[Case]) -> int:
    """Creates the case specific paramDict files in the case folders of the passed in cases.

    paramDict files contain the case specific parameters, meaning, via the paramDict files the case specific values
    for all parameters get distributed to and persisted in the case folders.

    Parameters
    ----------
    cases : MutableSequence[Case]
        cases the paramDict file shall be created for

    Returns
    -------
    int
        number of paramDict files created
    """

    logger.info('Create case-specific paramDict files in all case folders...')
    number_of_param_dicts_created: int = 0

    for case in cases:
        logger.debug(f"creating paramDict in {case.path}")  # 1
        target_file = case.path / 'paramDict'
        param_dict = CppDict(target_file)

        for parameter in case.parameters or []:
            if parameter.name and not re.match('^_', parameter.name):
                param_dict[parameter.name] = parameter.value

        param_dict['_case'] = case.to_dict()

        DictWriter.write(param_dict, target_file, mode='w')

        if case.is_leaf:
            number_of_param_dicts_created += 1

    leaf_cases = [case for case in cases if case.is_leaf]

    logger.info(
        f'Successfully created {number_of_param_dicts_created} '
        f'paramDict file{plural(number_of_param_dicts_created)} '
        f'in {len(leaf_cases)} case folder{plural(len(leaf_cases))}.'
    )

    return number_of_param_dicts_created


def create_case_list_files(
    cases: MutableSequence[Case],
    target_dir: Union[Path, None] = None,
    levels: Union[int, Sequence[int], None] = None
) -> list[Path]:
    """Create case list files for the specified nest levels.

    Case list files are simple text files containing a list of paths to all case folders that share a common nest level within the case folder structure.
    I.e. a case list file created for level 0 contains the paths to all case folders on level 0.
    A case list file for level 1 contains the paths to all case folders on level 1, and so on.

    These lists can be used i.e. in a batchProcess to execute shell commands
    in all case folders of a specific nest level inside the case folder structure.

    Parameters
    ----------
    cases : MutableSequence[Case]
        cases the case list files shall be created for
    target_dir : Path, optional
        directory in which the case list files shall be created. If None, current working directory will be used., by default None
    levels : Union[int, Sequence[int], None], optional
        list of integers indicating the nest levels for which case list files shall be created.
        If missing, by default a case list file for the deepest nest level (the leaf level) will becreated., by default None

    Returns
    -------
    list[Path]
        The case list files that have been created (returned as a list of Path objects)
    """

    _remove_old_case_list_files()
    target_dir = target_dir or Path.cwd()
    case_list_file_all_levels = target_dir / 'caseList'
    logger.info(
        f"Create case list file '{case_list_file_all_levels}', containing all case folders."
    )

    case_list_files_created: MutableSequence[Path] = []
    max_level: int = 0
    with case_list_file_all_levels.open(mode='w') as f:
        for case in cases:
            f.write(f"{case.path.absolute()}\n")
            max_level = max(max_level, case.level)
    case_list_files_created.append(case_list_file_all_levels)

    levels = levels or max_level
    levels = [levels] if isinstance(levels, int) else levels

    for level in levels:
        case_list_file_for_level = target_dir / f'caseList_level_{level:02d}'
        logger.info(
            f"Create case list file '{case_list_file_for_level}', containing the case folders of level {level}."
        )
        with case_list_file_for_level.open(mode='w') as f:
            for case in (case for case in cases if case.level == level):
                f.write(f"{case.path.absolute()}\n")
        case_list_files_created.append(case_list_file_for_level)

    case_list_files_created_log = ''.join(
        '\t' + path.name + '\n' for path in case_list_files_created
    )
    case_list_files_created_log = case_list_files_created_log.removesuffix('\n')
    logger.info(f"Successfully created following case list files:\n {case_list_files_created_log}")

    return case_list_files_created


def execute_command_set(
    cases: MutableSequence[Case],
    command_set: str,
    batch: bool = True,
    test: bool = False,
) -> int:
    """Executes the given command set in the case folders of the passed in cases.

    Parameters
    ----------
    cases : MutableSequence[Case]
        cases for which the specified command set shall be executed.
    command_set : str
        name of the command set to be executed, as defined in farnDict
    test : bool, optional
        if True, executes command set in only first case folder where command set is defined, by default False

    Returns
    -------
    int
        number of case folders in which the command set has been executed
    """

    logger.info(
        f"Execute command set '{command_set}' in all layers where '{command_set}' is defined..."
    )

    cases_registered: List[Case] = []
    number_of_cases_registered: int = 0
    reached_first_leaf: bool = False
    if test:
        logger.warning(
            f"farn.py called with option --test: Only first case folder where command set '{command_set}' is defined will be executed."
        )

    for case in cases:
        if not case.path.exists():
            logger.warning(
                f'Path {case.path} does not exist. '
                f'This most commonly happens if a filter expression was changed in between generating the folder structure (option --generate) \n'
                f'and executing a command set (option --execute). '
                f'If so, first generate the missing cases by calling farn with option --generate once again \n'
                f'and then retry to execute the command set with option --execute.'
            )
            continue
        if case.command_sets:
            if command_set in case.command_sets:
                cases_registered.append(case)
                number_of_cases_registered += 1
                if case.is_leaf:
                    reached_first_leaf = True
            else:
                logger.debug(f"Command set '{command_set}' not defined in case {case.case}")
        if test and reached_first_leaf:     # if test and at least one execution
            break

    number_of_cases_processed: int = 0

    if batch:
        cases_per_shell_command: Dict[str, List[Case]] = {}
        for case in cases_registered:
            if case.command_sets and command_set in case.command_sets:
                shell_commands: List[str] = case.command_sets[command_set]
                for shell_command in shell_commands:
                    if shell_command in cases_per_shell_command:
                        cases_per_shell_command[shell_command].append(case)
                    else:
                        cases_per_shell_command |= {shell_command: [case]}
        for index, (shell_command, cases) in enumerate(cases_per_shell_command.items()):
            case_list_file = Path.cwd() / f'caseList_for_command_{index}'
            with case_list_file.open(mode='w') as f:
                for case in cases:
                    f.write(f"{case.path.absolute()}\n")
            batch_processor = AsyncBatchProcessor(case_list_file, shell_command)
            batch_processor.run()
    else:
        for case in cases_registered:
            if case.command_sets and command_set in case.command_sets:
                shell_commands = case.command_sets[command_set]
                # logger.debug(f"Execute command set '{command_set}' in {case.path}")                # commented out as a similar message gets logged in also subProcess
                # Temporarily change cwd to case folder, to execute the shell commands from there
                current_dir = Path.cwd()
                os.chdir(case.path)
                # Execute shell commands
                _execute_shell_commands(shell_commands)
                # Change back cwd to current folder
                os.chdir(current_dir)
                number_of_cases_processed += 1

    # @TODO: This is only a temporary dummy.
    #        To be replaced by a smarter algorithm.
    #        CLAROS, 2022-08-16
    number_of_cases_processed = number_of_cases_registered

    if number_of_cases_processed > 0:
        if test:
            logger.info(
                f"Test finished. Executed command set '{command_set}' in following case folder:\n"
                f"\t {cases_registered[-1].path}"
            )
        else:
            logger.info(
                f"Successfully executed command set '{command_set}' "
                f"in {number_of_cases_registered} case folder{plural(number_of_cases_registered)}."
            )

    return number_of_cases_registered


def _set_up_farn_environment(farn_dict_file: Path) -> dict:
    """Reads the '_environment' section from farn dict and sets up the farn environment accordingly.

    Reads the '_environment' section from farnDict and sets up the farn environment directories as configured therein.
    If the '_environment' section or certain entries therein are missing in farn dict, default values will be used.

    Parameters
    ----------
    farn_dict_file : Path
        farnDict file

    Returns
    -------
    dict
        dict containing the environment directories set up for farn (matching the _environment section in farnDict)
    """

    logger.info('Set up farn environment...')

    # Set up farn environment.
    # 1: Define default values for environment
    # sourcery skip: merge-dict-assign
    environment: dict = {}
    environment['CASEDIR'] = 'cases'
    environment['DUMPDIR'] = 'dump'
    environment['LOGDIR'] = 'logs'
    environment['RESULTDIR'] = 'results'
    environment['TEMPLATEDIR'] = 'template'
    # 2: Overwrite default values with values defined in farn dict, if so
    if environment_from_farn_dict := DictReader.read(farn_dict_file, scope=['_environment']):
        environment |= environment_from_farn_dict
    else:
        logger.warning(
            f"Key '_environment' is missing in farn dict {farn_dict_file}. Using default values for farn environment."
        )

    # Read farn directories from environment
    farn_dirs: MutableMapping[str, Path] = {}
    farn_dirs.update({k: Path.joinpath(Path.cwd(), v) for k, v in environment.items()})
    farn_dirs.update({'ROOTDIR': Path.cwd()})
    # Configure logging handler to write the farn log (use an additional handler, exclusively for farn)
    _configure_additional_logging_handler_exclusively_for_farn(farn_dirs['LOGDIR'])

    # Set up system environment variables for each farn directory
    # This is necessary to enable shell commands defined in farnDict to point to them with i.e. %TEMPLATEDIR%
    for key, item in farn_dirs.items():
        append_system_variable(key, str(item))

    logger.info('Successfully set up farn environment.')

    return farn_dirs


def _configure_additional_logging_handler_exclusively_for_farn(log_dir: Path):
    """Creates an additional logging handler exclusively for the farn log.

    Parameters
    ----------
    log_dir : Path
        folder in which the log file will be created
    """
    # Create log file
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'farn.log'
    # Create logging file handler
    file_handler = logging.FileHandler(str(log_file.absolute()), 'a')
    file_handler.name = str(log_file.absolute())
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    # Register file handler at root logger
    root_logger = logging.getLogger()
    file_handler_already_exists: bool = any(
        handler.name == file_handler.name for handler in root_logger.handlers
    )
    if not file_handler_already_exists:
        root_logger.addHandler(file_handler)
    return


def _remove_old_case_list_files():  # sourcery skip: avoid-builtin-shadow
    """Removes old case list files, if existing.
    """
    logger.info('Remove old case list files...')

    lists = [list for list in Path.cwd().rglob('*') if re.search('(path|queue)List', str(list))]

    for list in lists:
        list = Path(list)
        list.unlink()

    logger.info('Successfully removed old case list files.')

    return


def _sys_call(shell_commands: MutableSequence):
    """Fallback function until _execute_command is usable under linux
    """

    for shell_command in shell_commands:
        os.system(shell_command)

    return


def _execute_shell_commands(shell_commands: MutableSequence):
    """Execute a sequence of shell commands using subprocess.

    Parameters
    ----------
    shell_commands : MutableSequence
        list with shell commands to be executed
    """

    # @TODO: until the problem with vanishing '.'s on Linux systems is solved (e.g. in command "ln -s target ."),
    #        reroute the function call to _sys_call instead, as a workaround.
    if platform.system() == 'Linux':
        _sys_call(shell_commands)
        return

    for shell_command in shell_commands:
        execute_in_sub_process(shell_command)

    return

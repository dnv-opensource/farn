import logging
import os
import platform
import re
import subprocess as sub
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import MutableMapping, MutableSequence, Sequence, Union

from dictIO.cppDict import CppDict
from dictIO.dictReader import DictReader
from dictIO.dictWriter import DictWriter, create_target_file_name
from dictIO.utils.strings import remove_quotes

from farn.utils.os import append_system_variable
from farn.run.subProcess import execute_in_sub_process


logger = logging.getLogger(__name__)


def run_farn(
    farn_dict_file: Path,
    sample: bool = False,
    generate: bool = False,
    command: str = None,
    ignore_errors: bool = False,
    test: bool = False,
):
    """Runs farn.

    Runs the sampling for all layers as configured in farnDict,
    generates the corresponding case folder structure and
    executes user-defined shell command sets in all case folders.

    Parameters
    ----------
    farn_dict_file : Path
        farnDict file. Contains the farn configuration.
    sample : bool, optional
        if True, runs the sampling defined for each layer and saves the sampled farnDict file with prefix sampled., by default False
    generate : bool, optional
        if True, generates the folder structure that spawns all layers and cases defined in farnDict, by default False
    command : str, optional
        executes the given command set in all case folders. The command set must be defined in the commands section of the applicable layer in farnDict., by default None
    ignore_errors : bool, optional
        if True, does not halt on errors, by default False
    test : bool, optional
        if True, runs only first case and returns, by default False
    """

    # Check whether farn dict file exists
    if not farn_dict_file.is_file():
        logger.error(f"farn: File {farn_dict_file} not found.")
        return

    # Set up farn environment
    farn_dirs: MutableMapping = _set_up_farn_environment(farn_dict_file)

    logger.info(
        f"Start farn with following arguments:\n"
        f"\t farn_dict_file: \t{farn_dict_file}\n"
        f"\t sample: \t\t{sample}\n"
        f"\t generate: \t\t{generate}\n"
        f"\t command: \t\t{command}\n"
        f"\t ignore_errors: \t{ignore_errors}\n"
        f"\t test: \t\t\t{test}"
    )

    # Read farn dict
    farn_dict = DictReader.read(farn_dict_file, comments=False)

    # Run sampling and create the samples for all layers in farn dict
    if sample:
        sampled_farn_dict = run_sampling(farn_dict)

        if sampled_farn_dict:
            logger.info(f'Save sampled farn dict {sampled_farn_dict.name}..')               # 1
            DictWriter.write(sampled_farn_dict)
            logger.info(f'Saved sampled farn dict in {sampled_farn_dict.source_file}.')     # 1

            # Reassign farn_dict so that it points to the newly created, sampled farn dict
            farn_dict = sampled_farn_dict

    # Document CLI arguments of current farn call in the farn dict
    farn_opts = {
        'farnDict': farn_dict.name,
        'runSampling': sample,
        'generate': generate,
        'execute': command,
        'ignore-errors': ignore_errors,
        'test': test
    }
    farn_dict.update({'_farnOpts': farn_opts})

    # @TODO: Ordering would be harmful now as we do not anylonger use a distinct
    #        'level' attribute for each layer, but derive levels implicitely
    #        following the order in which the layers are defined in the farn dict.
    #        We need to discuss, whether we want the order of layers in farn dict
    #        to determine their level, or whether we want to ignore their order of definition
    #        but set an explicit level attribute on each layer.
    # farn_dict.order_keys()

    # Create a backup copy of farn dict
    logger.info(f'Save backup copy of {farn_dict.name}..')
    farn_dict_backup_copy = Path(str(farn_dict.source_file) + '.copy')
    DictWriter.write(farn_dict, farn_dict_backup_copy)
    logger.info(f'Saved backup copy in {farn_dict_backup_copy}.')   # 1

    # Collect and register all cases that can be derived from the samples defined in farn dict
    cases = register_cases(farn_dict, farn_dirs['CASEDIR'])

    # Generate case folder structure
    # and create a case-specific paramDict file in each case folder
    if generate:
        generate_case_folder_structure(cases)
        generate_case_lists(
            cases=cases,
            target_dir=farn_dirs['ROOTDIR'],
        )
        _create_param_dict_file_in_case_folders(cases)

    # Execute a given command in all case folders
    if command:
        _execute_command_set_in_case_folders(
            cases=cases,
            command_set=command,
            ignore_errors=ignore_errors,
            test=test,
        )

    logger.info('Successfully finished farn.\n')


@dataclass
class Case:
    """Dataclass holding case attributes

    The dataclass 'Case' holds all relevant case attributes needed by farn to process cases, e.g.
        - condition
        - parameter names and associated values
        - commands
        - ..
    """
    layer: Union[str, None] = None
    level: int = 0
    no_of_samples: int = 0
    index: int = 0
    path: Path = Path.cwd()
    key: Union[str, None] = None
    is_leaf: bool = False
    condition: Union[MutableMapping, None] = None
    names: Union[MutableSequence[str], None] = None
    values: Union[MutableSequence[float], None] = None
    command_sets: Union[MutableMapping, None] = None

    @property
    def is_valid(self) -> bool:
        """Checks whether the case fulfills the configured filter criteria.

        A case is considered valid if it fulfills the filter criteria configured for the respective layer.

        Returns
        -------
        bool
            result of validity check. True indicates the case is valid, False not valid.
        """

        # Check whether the '_condition' element is defined.  Without it, case is in any case considered valid.
        if not self.condition or not isinstance(self.condition, MutableMapping):
            return True

        # Check whether filter expression is defined.
        # If filter expression is missing, condition cannot be evaluated but case is - as default - still considered valid.
        filter_expression = self.condition['_filter'] if '_filter' in self.condition else None
        if not filter_expression:
            logger.warning(
                f"layer {self.layer}: _condition element found but no filter expression defined therein."
                f"As the filter expression is missing, the condition cannot be evalued. Case {self.key} is hence still considered valid"
            )
            return True

        # Check whether optional argument '_action' is defined. Use default action, if not.
        action = self.condition['_action'] if '_action' in self.condition else None
        if not action:
            logger.warning(
                f"layer {self.layer}: No _action defined in _condition element. Default action 'exclude' is used."
            )
            action = 'exclude'

        # Check for formal errors that lead to invalidty
        if not self.names and not self.values:
            logger.warning(
                f"layer {self.layer}, case {self.key} validity check: case {self.key} is invalid:"
                f"A filter expression {filter_expression} is defined,"
                f"but no parameter names, nor parameter values exist."
            )
            return False
        if not self.names:
            logger.warning(
                f"layer {self.layer}, case {self.key} validity check: case {self.key} is invalid:"
                f"A filter expression {filter_expression} is defined,"
                f"but parameter names are missing."
            )
            return False
        if not self.values:
            logger.warning(
                f"layer {self.layer}, case {self.key} validity check: case {self.key} is invalid:"
                f"A filter expression {filter_expression} is defined and parameter names exist,"
                f"but parameter values are missing."
                f"Parameter names: {self.names}"
                f"Parameter values: None"
            )
            return False
        if len(self.names) != len(self.values):
            logger.warning(
                f"layer {self.layer}, case {self.key} validity check: case {self.key} is invalid:"
                f"A filter expression {filter_expression} is defined, and both parameter names and -values exist,"
                f"but the number of parameter names does not match the number of parameter values."
                f"Parameter names: {self.names}"
                f"Parameter values: {self.values}"
            )
            return False

        # Read all parameter names and their associated vales defined in current case, and assign them to local in-memory variables
        for parameter_name, parameter_value in zip(self.names, self.values):
            if not re.match('^_', parameter_name):
                try:
                    exec(f'{parameter_name} = {parameter_value}')
                except Exception:
                    logger.exception(
                        f"layer {self.layer}, case {self.key} validity check: case {self.key} is invalid:"
                        f"Reading parameter named {parameter_name} with value {parameter_value} failed."
                    )
                    return False

        # Evaluate filter expression
        filter_expression_evaluates_to_true = False
        try:
            filter_expression_evaluates_to_true = eval(filter_expression)
        except Exception:
            logger.exception(
                f"layer {self.layer}, case {self.key} validity check: case {self.key} is invalid:"
                f"The Evaluation of the filter expression failed."
                f"Possibly some of the parameters used in the filter expression are not defined yet in current level and case."
                f"Level: {self.level}"
                f"case: {self.key}"
                f"Filter expression: {filter_expression}"
                f"Parameter names: {self.names}"
                f"Parameter values: {self.values}"
            )
            return False

        # Finally: Determine case validity based on filter expression and action
        if filter_expression_evaluates_to_true and action == 'exclude':
            logger.debug(
                f"layer {self.layer}, case {self.key} validity check: case {self.key} is invalid:"
                f"The filter expression '{filter_expression}' evaluated to True."
                f"Action '{action}' performed. Case {self.key} excluded."
            )
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
            '_layer': self.layer,
            '_level': self.level,
            '_no_of_samples': self.no_of_samples,
            '_index': self.index,
            '_path': self.path,
            '_key': self.key,
            '_is_leaf': self.is_leaf,
            '_condition': self.condition,
            '_names': self.names,
            '_values': self.values,
            '_commands': self.command_sets,
        }


def run_sampling(farn_dict: CppDict) -> Union[CppDict, None]:
    """Runs the sampling for all layers and returns the sampled farnDict

    Parameters
    ----------
    farn_dict : CppDict
        farnDict for which sampling shall be run

    Returns
    -------
    Union[CppDict, None]
        sampled farnDict
    """
    from farn.sampling.sampling import DiscreteSampling

    if '_layers' not in farn_dict:
        logger.error(
            f"no '_layers' element in farn dict {farn_dict.name}. Conversion to sampled dict not possible."
        )
        return None

    def populate_layer(index: int, key: str, layer: MutableMapping):
        '''
        populates the layer with dynamically generated samples
        '''
        if '_sampling' not in layer:
            logger.error("no '_sampling' element in layer")
            return None
        if '_type' not in layer['_sampling']:
            logger.error("no '_type' element in sampling")
            return None

        sampling = DiscreteSampling()
        sampling.set_sampling_type(sampling_type=layer['_sampling']['_type'])
        # parameterize the sampling
        sampling.set_sampling_parameters(base_name=key, kwargs=layer['_sampling'])

        # in case the layer contains an (old) samples section -> delete it
        if '_samples' in layer:
            del layer['_samples']

        # generate the samples and write them into the keys element of the populated layer
        samples = sampling.generate()

        layer.update({'_samples': samples})

        # update the comment element in the populated layer
        fallback_comment = f'level {index:d} for basename {key}'
        comment = layer['_comment'] if '_comment' in layer else fallback_comment
        layer.update({'_comment': comment})

        return layer

    sampled_farn_dict = deepcopy(farn_dict)
    sampled_farn_dict.source_file = create_target_file_name(
        farn_dict.source_file, prefix='sampled.'
    )

    logger.info(f'Run sampling in {farn_dict.name}..')

    for index, (key, layer) in enumerate(sampled_farn_dict['_layers'].items()):
        populate_layer(index, key, layer)

    logger.info(f'Successfully ran sampling in {farn_dict.name}.')

    return sampled_farn_dict


def register_cases(
    farn_dict: MutableMapping,
    case_dir: Path,
) -> list[Case]:
    """Generates a list of case objects representing all valid cases.

    Recursively creates case objects for all valid cases, each case representing a valid permutation of samples acrosss the layers defined in farnDict.
    register_cases() creates one distinct case object for each case, holding all case attributes readily parameterized and set to their case specific values.
    Only valid cases will be registered, i.e. cases which fulfill the filter criteria configured for the respective layer.
    Invalid cases get excluded.

    Note:

    The actual case folders are not yet generated by register_cases().
    Generating the case folder structure is the responsibility of generate_case_folder_structure().
    However, the case_dir argument is passed in to allow register_cases() to already document in each case object
    its _intended_ case folder path. This information is then read and used in generate_case_folder_structure()
    to actually create the case folders.

    Parameters
    ----------
    farn_dict : MutableMapping
        farnDict, containing the farn configuration.
    case_dir : Path
        directory the case folder structure is intended to be generated in.

    Returns
    -------
    list[Case]
        list of case objects representing all valid cases. The attributes of each case object are readily parameterized and set to their case specific values.
    """
    logger.info('Register all valid cases..')

    # Check arguments.
    if '_layers' not in farn_dict:
        logger.error("register_cases: No '_layers' element contained in farn dict.")
        return []

    # Create cases list
    cases: list[Case] = []
    number_of_invalid_cases: int = 0
    # Create a local layers copy and turn that from dict format into list format
    # in order to ease sequential and indexed access to individual layers in create_next_level_cases()
    layers_copy: MutableMapping = deepcopy(farn_dict['_layers'])
    layers: MutableSequence = []
    for key, layer in layers_copy.items():
        layer.update({'_name': key})
        layers.append(layer)

    def create_next_level_cases(
        level: int = 0,
        base_case: Case = None,
    ):
        nonlocal cases
        nonlocal number_of_invalid_cases
        nonlocal layers

        base_case = base_case or Case(path=Path.cwd())
        base_case.names = base_case.names or []
        base_case.values = base_case.values or []

        layer: MutableMapping = layers[level]

        if '_samples' not in layer or '_keys' not in layer['_samples']:
            return

        layer_name: str = layer['_name']
        no_of_samples: int = len(layer['_samples']['_keys'])
        is_leaf: bool = (level == len(layers) - 1)
        condition: Union[MutableMapping,
                         None] = layer['_condition'] if '_condition' in layer else None
        commands: Union[MutableMapping,
                        None] = layer['_commands'] if '_commands' in layer else None

        samples_without_keys: MutableMapping = {
            name: values
            for name, values in layer['_samples'].items()
            if name != '_keys'
        }
        names: MutableSequence[str] = deepcopy(base_case.names)
        names.extend(list(samples_without_keys.keys()))
        values: MutableSequence[float] = []

        for index, key in enumerate(layer['_samples']['_keys']):
            key = remove_quotes(key)
            values = deepcopy(base_case.values)
            values.extend([values[index] for values in samples_without_keys.values()])

            case = Case(
                layer=layer_name,
                level=level,
                no_of_samples=no_of_samples,
                index=index,
                path=base_case.path / key,
                key=key,
                is_leaf=is_leaf,
                condition=condition,
                names=names,
                values=values,
                command_sets=commands,
            )

            if case.is_valid:
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

    logger.info(
        f'Successfully registered {len(cases)} valid cases. {number_of_invalid_cases} invalid cases were excluded.'
    )

    return cases


def generate_case_folder_structure(cases: MutableSequence[Case]) -> int:
    """Generates the case folder structure for the passed in cases.

    Generates the case folder structure based on a list of parameterized cases
    as generated by e.g. register_cases().

    Parameters
    ----------
    cases : MutableSequence[Case]
        cases the case folder structure shall be generated for.

    Returns
    -------
    int
        number of case folders generated.
    """

    logger.info('Generate case folder structure..')
    number_of_case_folders_generated: int = 0

    for case in cases:
        logger.debug(f"creating case folder {case.path}")   # 1
        case.path.mkdir(parents=True, exist_ok=True)
        number_of_case_folders_generated += 1

    logger.info(f'Successfully generated {number_of_case_folders_generated} case folders.')

    return number_of_case_folders_generated


def generate_case_lists(
    cases: MutableSequence[Case],
    target_dir: Path = None,
    levels: Union[int, Sequence[int], None] = None
) -> Path:
    """Generates case list files documenting all case folders per level.

    Case list files are generated per level, meaning i.e. the case list file for level 0
    contains the paths to all case folders on level 0.
    A case list for level 1 contains the paths to all case folders on level 1, and so on.

    These lists can then be used with i.e. the batchProcess command line script to execute shell commands
    in all case folders belonging to a specific nest level in the case folder structure.

    Parameters
    ----------
    cases : MutableSequence[Case]
        cases the case list files shall be generated for (as generated i.e. by register_cases())
    target_dir : Path, optional
        directory in which the case list files shall be created. If None, current working directory will be used., by default None
    levels : Union[int, Sequence[int], None], optional
        list of integers indicating the individual levels for which case list files shall be generated.
        If None, by default only a case list file for the deepest level (the leaf level) will be generated., by default None

    Returns
    -------
    Path
        [description]
    """

    _remove_old_case_lists()
    target_dir = target_dir or Path.cwd()
    case_list = target_dir / 'caseList'
    logger.info(f"Generate case list: {case_list}")

    case_lists_generated: MutableSequence[Path] = []
    max_level: int = 0
    with case_list.open(mode='w') as f:
        for case in cases:
            f.write(f"{case.path.absolute()}\n")
            max_level = max(max_level, case.level)
    case_lists_generated.append(case_list)

    levels = levels or max_level
    levels = [levels] if isinstance(levels, int) else levels

    for level in levels:
        case_list_for_level = target_dir / f'caseList_level_{level:02d}'
        logger.info(f"Generate case list for level {level}: {case_list_for_level}")
        with case_list_for_level.open(mode='w') as f:
            for case in (case for case in cases if case.level == level):
                f.write(f"{case.path.absolute()}\n")
        case_lists_generated.append(case_list_for_level)

    case_lists_log = ''.join('\t' + path.name + '\n' for path in case_lists_generated)
    case_lists_log = case_lists_log.removesuffix('\n')
    logger.info(f"Successfully generated following case lists:\n {case_lists_log}")

    return case_list


def _create_param_dict_file_in_case_folders(cases: MutableSequence[Case]) -> int:
    """Creates the paramDict file in the case folders of the passed in cases.

    The paramDict file contains the case specific parameters.

    Parameters
    ----------
    cases : MutableSequence[Case]
        cases for which the paramDict file shall be created

    Returns
    -------
    int
        number of paramDict files created
    """

    logger.info('Drop case-specific paramDict files in all case folders..')
    number_of_param_dicts_created: int = 0

    for case in cases:
        logger.debug(f"creating paramDict in {case.path}")  # 1
        target_file = case.path / 'paramDict'
        param_dict = CppDict(target_file)

        if case.names and case.values and len(case.names) == len(case.values):
            for parameter_name, parameter_value in zip(case.names, case.values):
                if not re.match('^_', parameter_name):
                    param_dict.update({parameter_name: parameter_value})

        param_dict.update({'_case': case.to_dict()})

        DictWriter.write(param_dict, target_file)

        number_of_param_dicts_created += 1

    logger.info(
        f'Successfully dropped {number_of_param_dicts_created} paramDict files in {len(cases)} case folders.'
    )

    return number_of_param_dicts_created


def _execute_command_set_in_case_folders(
    cases: MutableSequence[Case],
    command_set: str,
    ignore_errors: bool = False,
    test: bool = False,
) -> int:
    """Executes the given command set in the case folders of the passed in cases.

    Parameters
    ----------
    cases : MutableSequence[Case]
        cases for which the specified command set shall be executed.
    command_set : str
        name of the command set to be executed, as defined in farnDict
    ignore_errors : bool, optional
        if True, does not hold on errors, by default False
    test : bool, optional
        if True, executes command set in only first case folder where command set is defined, by default False

    Returns
    -------
    int
        number of case folders in which the command set has been executed
    """

    logger.info(
        f"Execute command set '{command_set}' in all layers where '{command_set}' is defined.."
    )
    number_of_cases_processed: int = 0

    if test:
        logger.warning(
            f"farn.py called with option --test: Only first case folder where command set '{command_set}' is defined will be executed."
        )

    for case in cases:
        if case.command_sets:
            if command_set in case.command_sets:
                shell_commands: MutableSequence[str] = []
                shell_commands = case.command_sets[command_set]
                logger.debug(f"Execute command set '{command_set}' in {case.path}")                 # level
                                                                                                    # push cwd into case folder to execute the shell commands from there
                old_dir = Path.cwd()
                os.chdir(case.path)
                                                                                                    # Execute shell commands
                _execute_shell_commands(shell_commands, ignore_errors=ignore_errors)
                                                                                                    # pop
                os.chdir(old_dir)
                number_of_cases_processed += 1
            else:
                logger.warning(f"Command set '{command_set}' not defined in case {case.key}")
        if test and number_of_cases_processed >= 1:                                                 # if test and at least one execution
            logger.warning(
                f"Test finished. Executed command set '{command_set}' in following case folder:\n"
                f"\t {case.path}"
            )
            break

    logger.info(
        f"Successfully executed command set '{command_set}' in {number_of_cases_processed} case folders"
    )

    return number_of_cases_processed


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

    logger.info('Set up farn environment..')

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
    environment_from_farn_dict = DictReader.read(farn_dict_file, scope=['_environment'])
    if environment_from_farn_dict:
        environment.update(environment_from_farn_dict)
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
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'farn.log'
    file_handler = logging.FileHandler(str(log_file.absolute()), 'a')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    return


def _remove_old_case_lists():
    """Removes old case list files, if existing.
    """
    logger.info('Remove old case list files..')

    lists = [list for list in Path.cwd().rglob('*') if re.search('(path|queue)List', str(list))]

    for list in lists:
        list = Path(list)
        list.unlink()

    logger.info('Successfully removed old case list files.')

    return


def _sys_call(shell_commands: MutableSequence, ignore_errors: bool = False):
    """Fallback function until _execute_command is usable under linux
    """

    for shell_command in shell_commands:
        os.system(shell_command)

    return


def _execute_shell_commands(shell_commands: MutableSequence, ignore_errors: bool = False):
    """Execute a sequence of shell commands using subprocess.

    Parameters
    ----------
    shell_commands : MutableSequence
        list with shell commands to be executed
    ignore_errors : bool, optional
        if True, does not hold on errors, by default False
    """

    # @TODO: until the problem with vanishing '.'s on Linux systems is solved (e.g. in command "ln -s target ."),
    #        reroute the function call to _sys_call instead, as a workaround.
    if platform.system() == 'Linux':
        _sys_call(shell_commands, ignore_errors=ignore_errors)
        return

    for shell_command in shell_commands:

        stdout, stderr = execute_in_sub_process(shell_command)

        out: str = str(stdout, encoding='utf-8')
        if out != '':
            logger.info(out)    # level

        err: str = str(stderr, encoding='utf-8')
        if err != '':
            logger.warning(err)     # level

        # shell_command = re.sub(
        #     r'(^\'|\'$)', '', shell_command
        # )                                       # temporary unless the formatter is made
        # shell_command = re.split(r'\s+', shell_command.strip())

        # sub_process = sub.Popen(
        #     shell_command, stdout=sub.PIPE, stderr=sub.PIPE, shell=True, cwd=r"%s" % os.getcwd()
        # )
        # # @TODO: This kills the process and waiting for job to be finished
        # #        Solution?
        # # @TODO: We need to check and possibly adjust the algorith to detect errors.
        # #        CLAROS, 2022-02-03
        # stdout, stderr = sub_process.communicate()
        # out: str = str(stdout, encoding='utf-8')
        # err: str = str(stderr, encoding='utf-8')

        # if out != '':
        #     logger.debug('STDOUT:')     # level
        #     logger.debug('%s' % out)    # level

        # if err != '':
        #     logger.debug('STDERR:')     # level
        #     logger.debug('%s' % err)    # level

        # if re.search('error', out, re.I) or err != '':
        #     if ignore_errors:
        #         logger.warning(
        #             '_execute_command: execution of %s continued on error: %s %s' %
        #             (' '.join(shell_command), out, err)
        #         )
        #     else:
        #         sub_process.kill()
        #         logger.error(
        #             '_execute_command: execution of %s stopped on error: %s %s' %
        #             (' '.join(shell_command), out, err)
        #         )

    return

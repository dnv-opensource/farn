import os

__all__ = ['append_system_variable']


def append_system_variable(variable, value):
    '''
    append system variable depending on system
    '''
    os.environ[f'{variable}'] = str(value)
    return

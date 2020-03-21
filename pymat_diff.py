"""Check diff status between python and matlab codebase."""
import os

import difflib
from pathlib import Path


class PymatDiffException(Exception):
    """Exception class for pymat_diff module."""


def get_filenames(path, ext, exclude=None):
    """Get list of all filenames of a given extension in a directory.

    Parameters
    ----------
    path : str
        Full path of directory.
    ext : str
        Extension of files to be searched.
    exclude : list, optional
        List of names to exclude. Defaults to None.

    Returns
    -------
    out : list
        List of filenames stripped of extensions.

    """
    path = Path(path)
    if not path.is_dir():
        raise PymatDiffException('No such directory: {:}'.format(path))

    if not exclude:
        exclude = []

    return sorted([f for f in path.rglob('*.' + ext) if f.stem not in exclude])


def matlabize(text_py):
    """Make a python file text more matlab.

    Parameters
    ----------
    text_py : list
        Text of python file.

    Returns
    -------
    modified_py : list
        Text of edited python file.

    """
    modified_py = []

    # Line by line modifications
    for line in text_py:
        # Remove import statements
        if line[:6] == 'import':
            continue
        elif line[:4] == 'from':
            continue

        # Remove leading whitespace
        line = line.lstrip()

        # Remove numpy and scipy
        line = line.replace('np.', '')

        modified_py.append(line)

    # File modifications
    # Remove encoding declaration
    modified_py.remove('# -*- coding: utf-8 -*-')
    if modified_py[0][:3] == '"""':
        del modified_py[0]

    return modified_py


def pythonize(text_mat):
    """Make a matlab file text more python.

    Parameters
    ----------
    text_mat : list
        Text of matlab file.

    Returns
    -------
    modified_mat : list
        Text of modified matlab file.

    """
    modified_mat = []

    # Line by line modifications
    for line in text_mat:
        # Remove leading whitespace
        line = line.lstrip()

        # Remove end statements
        if line == 'end':
            continue

        # Remove terminating semicolons even if followed by comments
        line = line.rstrip(';')
        line = line.replace(';  %', '  %')

        # Replace equivalent syntax
        line = line.replace('% ', '# ')
        line = line.replace('^', '**')

        # Remove elementwise symbol
        line = line.replace('.*', '*')
        line = line.replace('./', '/')

        # Replace indexing commas with brackets
        line = line.replace('(i)', '[i]')

        # Modify function calls
        if line[:8] == 'function':
            equals_i = line.index('=')
            line = 'def' + line[equals_i+1:] + ':'

        modified_mat.append(line)

    # File modifications

    return modified_mat


if __name__ == '__main__':
    current_path = Path(os.path.dirname(__file__))
    dir_py = Path(current_path, 'emccd_detect')
    dir_mat = Path(current_path, 'emccd_detect_m')

    exclude_py = ['__init__', 'config', 'imagesc']
    exclude_mat = ['autoArrangeFigures', 'histbn']
    list_py = get_filenames(dir_py, 'py', exclude_py)
    list_mat = get_filenames(dir_mat, 'm', exclude_mat)

    stems_py = [f.stem for f in list_py]
    stems_mat = [f.stem for f in list_mat]
    common_stems = sorted(set(stems_py).intersection(stems_mat))

    common_py = sorted([f for f in set(list_py) if f.stem in common_stems])
    common_mat = sorted([f for f in set(list_mat) if f.stem in common_stems])
    diff_py = [f for f in set(list_py) if f.stem not in set(stems_mat)]
    diff_mat = [f for f in set(list_mat) if f.stem not in set(stems_py)]

    # Disply filenames that exist only in either the matlab or python directory
    if diff_py:
        print('Python directory contains extra files not in Matlab:\n')
        for name in diff_py:
            print('   + ' + str(name))
    print('')
    if diff_mat:
        print('Matlab directory contains extra files not in Python:\n')
        for name in diff_mat:
            print('   + ' + str(name))
    print('')

    # Open files side by side for comparison
    for py, mat in zip(common_py, common_mat):
        with open(py, 'r') as file_py:
            text_py = file_py.read().splitlines()
        with open(mat, 'r') as file_mat:
            text_mat = file_mat.read().splitlines()

        # Remove blank lines
        text_py = list(filter(None, text_py))
        text_mat = list(filter(None, text_mat))

        # Modify files to remove irrelevant language-specific syntax
        modified_py = matlabize(text_py)
        modified_mat = pythonize(text_mat)

        # Take diff and create html for each common file
        diff = difflib.HtmlDiff().make_file(modified_py, modified_mat,
                                            '{:}'.format(py.name),
                                            '{:}'.format(mat.name))
        with open('diff/diff_{:}.html'.format(py.stem), 'w') as file:
            file.write(diff)

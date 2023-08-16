"""Python package for creating and managing sparse files"""
from importlib.metadata import version
__version__ = version("sparse_file")

from platform import system
os = system()
if os == 'Windows':
    from .sparse_win import open_sparse
elif os == 'Linux':
    from .sparse_nix import open_sparse
else:
    raise NotImplementedError('The {0} os is not supported at this time.'.format(os))
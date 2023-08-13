"""Python package for creating and managing sparse files"""

__version__ = "0.0.1"

from platform import system
os = system()
if os == 'Windows':
    from .sparse_win import open_sparse
elif os == 'Linux': 
    from .sparse_nix import open_sparse
else:
    raise NotImplementedError('The {0} os is not supported at this time.'.format(os))
__version__ = "0.0.1"

# Import overrides to ensure monkey patching happens
try:
    from . import overrides
except ImportError:
    pass

import sys


def normalize_path(path):
    """Convert a pathlib object to a string"""
    return str(path)


def sysexit(code=1):
    """sys.exit wrapper with default code"""
    sys.exit(code)

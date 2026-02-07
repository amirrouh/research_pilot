"""Helper for managing optional dependencies with helpful error messages."""


def require_package(package_name: str, extras_group: str, pip_package: str = None):
    """
    Check if a package is installed and provide helpful error message if not.

    Args:
        package_name: Python package name to import
        extras_group: Which Trion extras group contains this (e.g., 'research', 'web')
        pip_package: PyPI package name if different from package_name

    Raises:
        ImportError: With helpful installation instructions
    """
    pip_package = pip_package or package_name

    try:
        __import__(package_name)
    except ImportError:
        raise ImportError(
            f"This tool requires {package_name}. Install it with:\n"
            f"  pip install {pip_package}\n"
            f"Or install Trion with {extras_group} extras:\n"
            f"  pip install trion[{extras_group}]\n"
            f"Or install all extras:\n"
            f"  pip install trion[all]"
        )

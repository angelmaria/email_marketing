"""Minimal distutils shim for Python 3.12+.

Provides only what's needed by third-party packages that import
`distutils.version.LooseVersion`. This avoids failures where the
stdlib `distutils` was removed.
"""

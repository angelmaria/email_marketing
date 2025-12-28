try:
    from packaging.version import Version
except Exception as e:
    raise ImportError("The distutils shim requires the 'packaging' library") from e


class LooseVersion:
    """Lightweight replacement for distutils.version.LooseVersion.

    Implements basic rich comparisons using `packaging.version.Version`.
    Falls back to string comparison for unparsable versions.
    """

    def __init__(self, v):
        self._text = str(v)
        # Public attribute expected by callers
        self.vstring = self._text
        try:
            self._version = Version(self._text)
        except Exception:
            self._version = None
        # Public API expected by callers: a list-like `version` attribute
        # where index 0 is the major version.
        if self._version is not None:
            self.version = list(self._version.release)
        else:
            # Fallback: best-effort parse into list of ints/strings
            parts = []
            for p in self._text.split('.'):
                try:
                    parts.append(int(p))
                except ValueError:
                    parts.append(p.lower())
            self.version = parts

    def __repr__(self):
        return f"LooseVersion('{self._text}')"

    def __str__(self):
        return self._text

    def _coerce_other(self, other):
        if isinstance(other, LooseVersion):
            return other
        return LooseVersion(other)

    def _cmp_tuple(self):
        if self._version is not None:
            # Use packaging's normalized release segment for tuple comparison
            return tuple(self._version.release)
        # Fallback: split by dots and try ints, else lowercased strings
        parts = []
        for p in self._text.split('.'):
            try:
                parts.append(int(p))
            except ValueError:
                parts.append(p.lower())
        return tuple(parts)

    def __eq__(self, other):
        other = self._coerce_other(other)
        if self._version is not None and other._version is not None:
            return self._version == other._version
        return self._cmp_tuple() == other._cmp_tuple()

    def __lt__(self, other):
        other = self._coerce_other(other)
        if self._version is not None and other._version is not None:
            return self._version < other._version
        return self._cmp_tuple() < other._cmp_tuple()

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        other = self._coerce_other(other)
        if self._version is not None and other._version is not None:
            return self._version > other._version
        return self._cmp_tuple() > other._cmp_tuple()

    def __ge__(self, other):
        return self == other or self > other

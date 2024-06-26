"""
Utility to generate terminology.py from PITerminology.h and
PIStringTerminology.h in the Photoshop SDK. Use with Python 3.

Usage:

    python3 tools/extract_terminology.py \
        photoshopsdk/PITerminology.h \
        src/psd_tools/terminology.py

.. note:: Adobe explicitly prohibits Photoshop SDK to be used for Open source
    software. Therefore, psd-tools does not bundle the official header files.
    https://www.adobe.com/devnet/photoshop/sdk/eula.html
"""
from __future__ import print_function

import re
import sys

FILE_HEADER = '''"""
Constants for descriptor.

This file is automaticaly generated by tools/extract_terminology.py
"""
from enum import Enum as _Enum'''


TERM_DEF = '''class {0}(_Enum):
    """
    {0} definitions extracted from PITerminology.h.

    See https://www.adobe.com/devnet/photoshop/sdk.html
    """'''


TERM_PATTERN = re.compile(
    r"^#define\s+(?P<key>\w+)\s+'(?P<value>....)'(\s+//\s(?P<comment>.*))?$"
)


STERM_DEF = '''class StringTerm(Enum):
    """
    String terms extracted from PIStringTerminology.h in Photoshop SDK.

    This defines constants for the strings used to access descriptor events,
    keys, classes, enum types, and enum values.

    See https://www.adobe.com/devnet/photoshop/sdk.html
    """'''


STERM_PATTERN = re.compile(
    r'^#define\s+(?P<key>\w+)\s+"(?P<value>[^"]+)"(\s+//\s(?P<comment>.*))?$'
)


def extract_terminology(filepath, pattern=None):
    terms = {}
    keys = set()
    with open(filepath, "r") as f:
        for line in f:
            m = re.match(pattern or TERM_PATTERN, line)
            if m:
                key = m.group("key")
                if key in keys:
                    continue
                upper = re.search(r"[0-9A-Z]", key)
                kls, name = key[: upper.start()], key[upper.start() :]
                if re.match(r"[0-9]", name[0]) or name in ("None", "True", "False"):
                    name = "_" + name
                kls = kls.capitalize().replace("Class", "Klass")
                if kls in terms:
                    terms[kls].append((name, m.group("value")))
                else:
                    terms[kls] = [(name, m.group("value"))]
    return terms


def print_class(name, fields, header=None, **kwargs):
    print("\n", **kwargs)
    print((header or "class {0}:").format(name), **kwargs)
    for field in fields:
        print("    %s = b%r" % field, **kwargs)


def main():
    terms = extract_terminology(sys.argv[1])

    with open(sys.argv[2], "w") as f:
        print(FILE_HEADER, file=f)
        for name in terms:
            print_class(name, terms[name], TERM_DEF, file=f)


if __name__ == "__main__":
    main()

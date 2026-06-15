# -*- coding: utf-8 -*-
"""Assert the Python package reproduces vectors/vectors.json (the golden output set shared
with the JS port). Run: pytest  (or: python -m pytest)  from py/  — or python tests/test_vectors.py."""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import sanskrit_util as su  # noqa: E402

VECTORS = os.path.join(HERE, '..', '..', 'vectors', 'vectors.json')


def load():
    with open(VECTORS, encoding='utf-8') as f:
        return json.load(f)


def test_all_vectors():
    data = load()
    fails = []
    for fn, cases in data.items():
        f = getattr(su, fn, None)
        assert callable(f), f'missing function: {fn}'
        for c in cases:
            got = f(c['in'])
            if got != c['out']:
                fails.append(f"{fn}({c['in']!r}): got {got!r} expected {c['out']!r}")
    assert not fails, '\n'.join(fails[:30])


if __name__ == '__main__':
    test_all_vectors()
    n = sum(len(v) for v in load().values())
    print(f'OK: {n} vectors match (Python package == golden)')

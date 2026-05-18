---
inclusion: auto
---

# Python Compatibility Rules for CalcPaper

CalcPaper targets Python 3.7+ compatibility. Follow these rules strictly:

## Required in every .py file

Every Python source file MUST have `from __future__ import annotations` as the first non-comment, non-docstring line. This ensures type annotations are treated as strings and never evaluated at runtime.

## Forbidden syntax (runtime errors on Python < 3.10)

- **NEVER** use `X | Y` union type syntax (e.g., `int | None`, `str | list`). Use `Optional[X]` or `Union[X, Y]` from typing instead.
- **NEVER** use `list[str]`, `dict[str, int]`, `tuple[int, ...]` as runtime type annotations without `from __future__ import annotations`. With the future import, these are safe.
- **NEVER** use `match/case` statements (Python 3.10+).
- **NEVER** use walrus operator `:=` (Python 3.8+, but avoid for 3.7 compat).

## Safe patterns (with `from __future__ import annotations`)

```python
from __future__ import annotations

# These are ALL safe because annotations are strings:
def foo(x: list[str]) -> dict[str, int]: ...
def bar(x: int | None) -> str | None: ...

class MyClass:
    items: list[str] = field(default_factory=list)
    parent: MyClass | None = None
```

## Runtime type checks

If you need runtime type checking (isinstance, dataclass field defaults, etc.), use typing imports:

```python
from typing import Optional, List, Dict, Tuple, Union
```

## Version check in main.py

`main.py` includes a version check that exits with a clear message if Python < 3.7.

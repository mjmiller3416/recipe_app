"""core/helpers/singleton_mixin.py

Provides a mixin for creating singleton classes.
"""

# ── Singleton Mixin ─────────────────────────────────────────────────
class SingletonMixin:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

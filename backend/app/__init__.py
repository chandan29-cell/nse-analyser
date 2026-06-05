# Package init for backend.app
# Avoid importing `app` here to prevent side-effects when importing
# submodules (tests import core modules and should not require FastAPI).
__all__ = []

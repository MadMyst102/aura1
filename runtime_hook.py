
import os
import sys
import asyncio

# Ensure _cffi_backend is properly imported at runtime
try:
    import _cffi_backend
except ImportError:
    pass

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

"""Optional local configuration for PowerToys Run Browse.

Copy this file to config.py and edit the values for your own LLM server or
compatible API endpoint. config.py is ignored by Git so private settings stay
on your machine.
"""

SERVER_URL = "http://192.168.1.88:5000"
TARGET_TPS = 50
LLM_MODEL = "local-model"
DEFAULT_CONTEXT_TOKENS = 8192
MAX_INPUT_CONTEXT_RATIO = 0.4
EXIT_PAUSE_SECONDS = 2

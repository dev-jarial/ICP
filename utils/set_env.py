import os

import environ

# Initialize environment variables
env = environ.Env()

environ.Env.read_env(os.path.join(os.path.dirname(__file__), "../.env"))

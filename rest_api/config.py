import os

# Get the absolute path to project.sqlite, assuming it's in the parent directory of rest_api/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "project.sqlite")

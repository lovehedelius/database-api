import os

# Get the absolute path to lab3.sqlite, assuming it's in the parent directory of rest_api/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Gets the rest_api directory
DB_PATH = os.path.join(BASE_DIR, "..", "project.sqlite")  # Points to lab3.sqlite
"""DenseEdia module endpoint"""

from .api.launch import launch_server
from .constants import DEFAULT_FILE_NAME, ROOT_PATH
from .storage.tables import use_database

use_database(ROOT_PATH / DEFAULT_FILE_NAME)
launch_server()

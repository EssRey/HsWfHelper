import config
from list_copy import copy_all_lists
from workflow_copy import copy_all_workflows
import logger
# create_input_files will create "inputs/id_mappings.json" and 'inputs/active_list_ids.json'
import create_input_files

copy_all_lists(simulate=False)
copy_all_workflows(simulate=False)
logger.write_log("full_migration_log")
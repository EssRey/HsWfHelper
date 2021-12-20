import config
from list_copy import copy_all_lists
from workflow_copy import copy_all_workflows, copy_workflow
import logger

copy_all_lists(simulate=True)
#copy_all_workflows(simulate=True)

#copy_workflow(123, simulate=True)

#logger.write_log("real_copy_log")
logger.write_todo("debug_todo")
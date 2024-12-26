from enum import StrEnum


class CapabilityEnums(StrEnum):
    SHOW_DBS = "show_dbs"
    SHOW_SCHEMAS = "show_schemas"
    SHOW_TABLES = "show_tables"
    SHOW_COLUMNS = "show_columns"
    RUN_SINGLE_QUERY = "run_single_query"
    RUN_SINGLE_FILE = "run_single_file"

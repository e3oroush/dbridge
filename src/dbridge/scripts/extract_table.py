import re
import sys

import sqlparse
from sqlparse.sql import Identifier
from sqlparse.tokens import Keyword


def extract_select_statement(query: str) -> str | None:
    """Split multiple statements and return the first select statement"""
    statements = sqlparse.split(
        re.sub(r",\s+from", " from", query.lower()), strip_semicolon=True
    )
    for statement in statements:
        if "select" in statement.lower():
            return statement


def extract_table(statement: str) -> str | None:
    parts = sqlparse.parse(statement)[0]
    from_seen = False
    for item in parts.tokens:
        if from_seen and isinstance(item, Identifier):
            return item.value
        if item.ttype is Keyword and item.value.lower() == "from":
            from_seen = True


def main(query: str):
    select_statement = extract_select_statement(query)
    if not select_statement:
        return
    table_name = extract_table(select_statement)
    if table_name:
        print(table_name)


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    main(query)

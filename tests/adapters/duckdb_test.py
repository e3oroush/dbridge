import pytest

from dbridge.adapters.dbs.duckdb import DuckdbAdapter


def init_db():
    db = DuckdbAdapter({"uri": ":memory:"})
    queries = [
        """CREATE TABLE contacts (
	contact_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email TEXT NOT NULL UNIQUE,
	phone TEXT NOT NULL UNIQUE
);""",
        """CREATE TABLE groups (
   group_id INTEGER PRIMARY KEY,
   name TEXT NOT NULL
);""",
        """CREATE TABLE contact_groups(
   contact_id INTEGER,
   group_id INTEGER,
   PRIMARY KEY (contact_id, group_id),
   FOREIGN KEY (contact_id) 
      REFERENCES contacts (contact_id),
   FOREIGN KEY (group_id) 
      REFERENCES groups (group_id) 
);""",
    ]
    for q in queries:
        db.run_query(q)
    return queries, db


def test_show_tables():
    queries, sqlite = init_db()
    catalog = sqlite.show_tables_schema_dbs()
    tables = catalog[0].schemas[0].tables
    assert len(tables) == len(queries)
    assert "contacts" in tables
    assert "groups" in tables
    assert "contact_groups" in tables


@pytest.mark.parametrize(
    "table_name,wanted_columns",
    [
        ("contacts", {"contact_id", "first_name", "last_name", "email", "phone"}),
        ("groups", {"group_id", "name"}),
        ("contact_groups", {"contact_id", "group_id"}),
    ],
)
def test_show_columns(table_name, wanted_columns):
    _, sqlite = init_db()
    columns = sqlite.show_columns(table_name)
    assert len(wanted_columns.union(columns)) == len(wanted_columns)


def test_run_query():
    _, sqlite = init_db()
    query = "insert into contacts(contact_id, first_name, last_name, email, phone) values (1, 'ebi', 'ebi', 'email', '123')"
    sqlite.run_query(query)
    query = "select * from contacts;"
    fetch = sqlite.run_query(query)
    assert len(fetch) == 1
    assert fetch[0]["first_name"]

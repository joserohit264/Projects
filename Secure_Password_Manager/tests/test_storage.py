from storage import init_db, add_entry, view_entries

def test_storage():
    init_db()
    add_entry("test.com", "admin", "1234", "none")
    rows = view_entries()
    assert len(rows) > 0

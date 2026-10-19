from pathlib import Path
from unittest.mock import patch

from app.indexer import get_document_changes

def test_unchanged_documents():
    
    fake_file=Path("java.txt")
    
    with(
        patch("app.indexer.load_metadata",
              return_value={"java.txt":{"hash":"abc123"}}),
        patch("app.indexer.discover_documents",
              return_value=[fake_file]),
         patch("app.indexer.load_document",
              return_value=[
                  {"page_number": None, "content": "Java is a programming language."}
              ]),
        patch("app.indexer.calculate_hash",
              return_value="abc123"),
        patch("app.indexer.get_indexed_filenames", return_value=set())
    ):
        changes = get_document_changes()
    
    
    assert "java.txt" in changes["unchanged"]
    assert changes["added"]==set()
    assert changes["changed"]==set()
    assert changes["removed"]==set()
    

def test_changed_document():
    
    fake_file=Path("java.txt")
    
    with(
        patch("app.indexer.load_metadata",
              return_value={"java.txt":{"hash":"abc123"}}),
        patch("app.indexer.discover_documents",
              return_value=[fake_file]),
        patch("app.indexer.load_document",
              return_value=[
                  {"page_number":None , "content":"Java is a programming Language"}
              ]),
        patch("app.indexer.calculate_hash",
              return_value="xyz789"),
        patch("app.indexer.get_indexed_filenames", return_value=set())
    ):
        changes=get_document_changes()
        
    assert "java.txt" in changes["changed"]
    assert changes["added"]==set()
    assert changes["unchanged"]==set()
    assert changes["removed"]==set()
    
    
def fake_load_document(file):
    if file.name == "java.txt":
        return [
            {"page_number": None, "content": "Java content"}
        ]
    elif file.name == "python.txt":
        return [
            {"page_number": None, "content": "Python content"}
        ]
        
def fake_calculate_hash(content):
    
    if content == "Java content":
        return "abc123"
    
    elif content == "Python content":
        return "xyz789"
        

    
def test_added_documents():
    
    fake_file1=Path("java.txt")
    fake_file2=Path("python.txt")
    
    with(
        patch("app.indexer.load_metadata",
              return_value={"java.txt":{"hash":"abc123"}}),
        patch("app.indexer.discover_documents",
              return_value=[fake_file1,fake_file2]),
        patch("app.indexer.load_document",side_effect=fake_load_document),
        patch("app.indexer.calculate_hash",side_effect=fake_calculate_hash),
        patch("app.indexer.get_indexed_filenames", return_value=set())
    ):
        changes=get_document_changes()
        
    assert "java.txt" in changes["unchanged"]
    assert "python.txt" in changes["added"]
    assert changes["changed"]==set()
    assert changes["removed"]==set()
    
    
def test_removed_documents():
    
    python_file=Path("python.txt")
    
    with(
        patch("app.indexer.load_metadata",
              return_value={"java.txt":{"hash":"abc123"},"python.txt":{"hash":"xyz789"}}),
        patch("app.indexer.discover_documents",
              return_value=[python_file]),
        patch("app.indexer.load_document",
              return_value=[{"page_number":None,"content":"Python content"}]),
        patch("app.indexer.calculate_hash",
              return_value="xyz789"),
        patch("app.indexer.get_indexed_filenames",return_value=set())
    ):
        changes=get_document_changes()
        
    assert "java.txt" in changes["removed"]
    assert "python.txt" in changes["unchanged"]
    assert changes["changed"]==set()
    assert changes["added"]==set()
    
def test_update_index_removes_document():
    
    with(
        patch("app.indexer.get_document_changes",
              return_value={
                  "unchanged":{"python.txt"},
                  "removed":{"java.txt"},
                  "added":set(),
                  "changed":set(),
                  "stale":set()
              }),
        patch("app.indexer.discover_documents",
              return_value=[Path("python.txt")]),
        patch("app.indexer.load_metadata",
              return_value={"java.txt":{"hash":"abc123"},"python.txt":{"hash":"xyz789"}}),
        patch("app.indexer.delete_document") as mock_delete,
        patch("app.indexer.save_metadata") as mock_save,
    ):
        from app.indexer import update_index
        update_index()
        
     # Verify Java's vectors are scheduled for deletion.
    mock_delete.assert_called_once_with("java.txt")

    # Verify only Python remains in the saved metadata.
    mock_save.assert_called_once_with({
        "python.txt": {"hash": "xyz789"}
    })
    
    
def test_update_index_adds_document():
    
    with(
        patch("app.indexer.get_document_changes",
                      return_value={
                          "unchanged":{"python.txt"},
                          "removed":set(),
                          "added":{"java.txt"},
                          "changed":set(),
                          "stale":set(),
                          "new_metadata": {
                            "java.txt": {"hash": "abc123"}
                          }
                      }),
        patch("app.indexer.discover_documents",
                return_value=[Path("python.txt"),Path("java.txt")]),
        patch("app.indexer.load_metadata",
                return_value={"python.txt":{"hash":"xyz789"}}),
        patch("app.indexer.index_new_document") as mock_add,
        patch("app.indexer.save_metadata") as mock_save,
    ):
        from app.indexer import update_index
        update_index()
        
    mock_add.assert_called_once_with(Path("java.txt"))
    mock_save.assert_called_once_with({"python.txt":{"hash":"xyz789"},"java.txt":{"hash":"abc123"}})
    

def test_update_index_updates_document():
    
    with(
        patch("app.indexer.get_document_changes",
              return_value={
                  "added":set(),
                  "removed":set(),
                  "changed":{"java.txt"},
                  "unchanged":{"python.txt"},
                  "stale":set(),
                  "new_metadata":{"java.txt":{"hash":"def456"}}
              }),
        patch("app.indexer.discover_documents",
              return_value=[Path("python.txt"),Path("java.txt")]),
        patch("app.indexer.load_metadata",
              return_value={"python.txt":{"hash":"xyz789"},"java.txt":{"hash":"abc123"}}),
        patch("app.indexer.update_document") as mock_update,
        patch("app.indexer.save_metadata") as mock_save,
    ):
        from app.indexer import update_index
        update_index()
        
    mock_update.assert_called_once_with(Path("java.txt"))
    mock_save.assert_called_once_with({"python.txt":{"hash":"xyz789"},"java.txt":{"hash":"def456"}})
    
    
def test_update_index_removes_stale_document():
    
    with(
        patch("app.indexer.get_document_changes",
              return_value={
                  "added":set(),
                  "removed":set(),
                  "unchanged":{"python.txt"},
                  "changed":set(),
                  "stale":{"orphan.txt"},
                  "new_metadata": {
                    "python.txt": {"hash": "xyz789"}
                    }
              }),
        patch("app.indexer.discover_documents",
              return_value=[Path("python.txt")]),
        patch("app.indexer.load_metadata",
              return_value={"python.txt":{"hash":"xyz789"}}),
        patch("app.indexer.delete_document") as mock_delete,
        patch("app.indexer.save_metadata") as mock_save,
    ):
        from app.indexer import update_index
        update_index()
        
    mock_delete.assert_called_once_with("orphan.txt")
    mock_save.assert_called_once_with({"python.txt":{"hash":"xyz789"}})
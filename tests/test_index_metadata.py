from app.index_metadata import calculate_hash

def test_hash():
    assert isinstance(calculate_hash("Hello"),str)
    
def test_same():
    hash_value=calculate_hash("Hello")
    
    assert hash_value==calculate_hash("Hello")
    
def test_change():
    hashValue=calculate_hash("Hello")
    
    assert hashValue!=calculate_hash("hello")
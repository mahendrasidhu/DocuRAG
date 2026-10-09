import hashlib
from pathlib import Path
import json

METADATA_FILE = Path("index_metadata.json")

def calculate_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def load_metadata():
    if not METADATA_FILE.exists():
        return {}
    
    with open(METADATA_FILE, 'r',encoding='utf-8') as file:
        return json.load(file)
    
def save_metadata(metadata):
    with open(METADATA_FILE,"w",encoding='utf-8') as file:
        json.dump(metadata,file,indent=4)
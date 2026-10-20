"""Write SHA-256 checksums for the public package files."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = ['README.md','MODEL.md','CHANGELOG.md','CITATION.cff','requirements.txt']

def write_checksums(root=ROOT):
    paths = [root/name for name in ROOT_FILES]
    for directory in ['code','data','figures']:
        paths.extend(p for p in (root/directory).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts
                     and not p.name.startswith('.') and p.suffix not in {'.pyc','.pyo'})
    lines = [hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()
             for p in sorted(paths) if p.is_file()]
    (root/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    write_checksums()

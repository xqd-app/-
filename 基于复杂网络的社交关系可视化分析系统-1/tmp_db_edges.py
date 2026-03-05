import os,sys
project_root=os.getcwd()
sys.path.insert(0,project_root)
from src.backend.data_processing.dao import DataDAO

dao=DataDAO(use_database=True)
edges=dao.load_edges()
print('count', len(edges))
if edges:
    print(edges[:10])
    print('fields', edges[0].keys())
    zero = [e for e in edges if e.get('source_id')==0 or e.get('target_id')==0]
    print('zero edge count', len(zero))

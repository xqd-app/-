import os,sys
project_root = os.getcwd()
sys.path.insert(0, project_root)
from src.backend.data_processing.dao import DataDAO

dao = DataDAO(use_database=True)
edges = dao.load_edges()
print('total edges', len(edges))
c0 = [e for e in edges if e.get('source')==0 or e.get('source_id')==0 or e.get('target')==0 or e.get('target_id')==0]
print('edges with id0', len(c0))
print(c0[:10])

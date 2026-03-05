import os, sys
project_root = os.getcwd()
sys.path.insert(0, project_root)
from src.backend.data_processing.dao import DataDAO

dao = DataDAO(use_database=True)
nodes = dao.load_nodes()
print('total nodes', len(nodes))
for i, n in enumerate(nodes[:5]):
    print(i, n)

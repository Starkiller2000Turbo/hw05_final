import os

os.chmod('manage.py', 0o777)
print(os.access('manage.py', os.X_OK))

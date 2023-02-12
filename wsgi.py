from app import app 
from app import db
from socket import gethostname



import sys
path = '/python_any'
if path not in sys.path:
   sys.path.insert(0, path)


if __name__ == '__main__':
    db.create_all()
    if 'liveconsole' not in gethostname():
        app.run()



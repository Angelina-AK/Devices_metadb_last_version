import sys 
sys.path.append('..')

from app.models import db, Object
from app import app


with app.app_context():
    objects = db.session.query(Object).all()
    for obj in objects:
        print(obj.get_attributes())
    # print(objects)
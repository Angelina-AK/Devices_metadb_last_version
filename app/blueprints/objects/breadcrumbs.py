from flask import request
from app.models import db, Attribute





# +-----------------------------------------------------------
# Атрибуты                                                     |
# +-----------------------------------------------------------
def edit_attribute_dlc():
    attribute_id: str = request.view_args['id']
    atr: Attribute = db.session.query(Attribute).where(Attribute.id == attribute_id).first()
    return [{
            'text': f'Editing attribute "{atr.attribute_name}"',
            'url': f'/attributes/edit/{attribute_id}'}]
# from alchemy_mock.mocking import AlchemyMagicMock
import sys 

# sys.path.append('..')


import pytest
from app import app
from app.models import db

@pytest.fixture
def test_session():
    with app.app_context():
        session = db.session
        yield session

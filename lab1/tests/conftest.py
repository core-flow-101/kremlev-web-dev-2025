from datetime import datetime
import pytest
from flask import template_rendered
from contextlib import contextmanager
from app import app as application

@pytest.fixture
def app():
    return application

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

@pytest.fixture
def posts_list():
    return [
        {
            'title': 'Заголовок',
            'text': 'Текст',
            'author': 'Креммлев Михаил',
            'date': datetime(2025, 3, 23),
            'image_id': '123.jpg',
            'comments': []
        }
    ]

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_client(app):
    class TestResponse:
        def __init__(self, response):
            self.response = response

        @property
        def text(self):
            return self.response.get_data(as_text=True)

    client = app.test_client()
    client.response_class = TestResponse
    return client
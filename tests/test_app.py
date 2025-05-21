import pytest
from app import app
from users import User
from flask import session
from flask_login import logout_user

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess.clear()
        yield client

def login(client, username="user", password="qwerty", remember=False):
    return client.post('/login', data={
        'username': username,
        'password': password,
        'remember': 'y' if remember else ''
    }, follow_redirects=True)

def test_visit_counter_isolated_per_user(client):
    with client.session_transaction() as sess:
        sess['visits'] = 0
    res1 = client.get('/')
    res1_as_text = res1.get_data(as_text=True)
    assert 'Вы посетили эту страницу <strong>1</strong> раз' in res1_as_text
    res2 = client.get('/')
    assert 'Вы посетили эту страницу <strong>2</strong> раз' in res2.get_data(as_text=True)

def test_successful_login_redirects_to_index(client):
    response = login(client)
    assert 'Вы успешно вошли в систему.' in response.get_data(as_text=True)
    assert 'Вы посетили эту страницу' in response.get_data(as_text=True)

def test_failed_login_shows_error(client):
    response = login(client, username='wrong', password='wrong')
    assert 'Неверный логин или пароль' in response.get_data(as_text=True)
    assert 'Вход' in response.get_data(as_text=True)

def test_authenticated_user_can_access_secret(client):
    login(client)
    response = client.get('/secret')
    assert 'Секретная страница' in response.get_data(as_text=True)

def test_unauthenticated_user_redirected_from_secret(client):
    response = client.get('/secret', follow_redirects=True)
    assert 'Для доступа необходимо войти' in response.get_data(as_text=True)
    assert 'Вход' in response.get_data(as_text=True)

def test_redirect_back_to_secret_after_login(client):
    response = client.get('/secret', follow_redirects=False)
    assert response.status_code == 302
    assert '/login?next=%2Fsecret' in response.headers['Location']

    login_response = client.post('/login?next=/secret', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)

    assert 'Секретная страница' in login_response.get_data(as_text=True)

def test_remember_me_login_successful(client):
    response = login(client, remember=True)
    assert 'Вы успешно вошли в систему.' in response.get_data(as_text=True)
    assert 'Вы посетили эту страницу' in response.get_data(as_text=True)

def test_navbar_links_authenticated(client):
    login(client)
    response = client.get('/')
    assert 'Секретная' in response.get_data(as_text=True)
    assert 'Выход' in response.get_data(as_text=True)
    assert 'Вход' not in response.get_data(as_text=True)

def test_navbar_links_anonymous(client):
    response = client.get('/')
    assert 'Вход' in response.get_data(as_text=True)
    assert 'Секретная' not in response.get_data(as_text=True)
    assert 'Выход' not in response.get_data(as_text=True)

def test_visits_not_shared_between_sessions():
    app.config['TESTING'] = True
    with app.test_client() as client1:
        client1.get('/')
        client1.get('/')
        res1 = client1.get('/')
        assert 'Вы посетили эту страницу <strong>3</strong> раз' in res1.get_data(as_text=True)

    with app.test_client() as client2:
        res2 = client2.get('/')
        assert 'Вы посетили эту страницу <strong>1</strong> раз' in res2.get_data(as_text=True)

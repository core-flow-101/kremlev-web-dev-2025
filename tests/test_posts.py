
def test_index_template(client, captured_templates):
    response = client.get('/')
    assert response.status_code == 200
    assert captured_templates[0][0].name == 'index.html'

def test_posts_template(client, captured_templates):
    response = client.get('/posts')
    assert response.status_code == 200
    assert captured_templates[0][0].name == 'posts.html'
    assert 'posts' in captured_templates[0][1]

def test_posts_data(client):
    response = client.get('/posts')
    assert response.status_code == 200
    assert 'Заголовок поста' in response.get_data(as_text=True)

def test_post_template(client, captured_templates):
    response = client.get('/posts/0')
    assert response.status_code == 200
    assert captured_templates[0][0].name == 'post.html'
    assert 'post' in captured_templates[0][1]


def test_post_data(client):
    response = client.get('/posts/0')

    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    assert 'Заголовок поста' in response_as_text
    author_name = response_as_text.split('<span class="author fw-bold">')[1].split('</span>')[0]
    assert author_name in response_as_text

    
def test_post_date_format(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    assert any(b'202' in response.data for year in range(0, 5))

def test_post_404(client):
    response = client.get('/posts/999')
    assert response.status_code == 404

def test_about_template(client, captured_templates):
    response = client.get('/about')
    assert response.status_code == 200
    assert captured_templates[0][0].name == 'about.html'

def test_about_data(client):
    response = client.get('/about')
    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    assert 'Об авторе' in response_as_text

def test_index_status_code(client):
    response = client.get('/')
    assert response.status_code == 200

def test_posts_status_code(client):
    response = client.get('/posts')
    assert response.status_code == 200

def test_post_status_code(client):
    response = client.get('/posts/0')
    assert response.status_code == 200

def test_post_comments(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    assert 'Комментарии' in response_as_text


def test_post_form_validation(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    assert 'textarea' in response_as_text
    assert 'minlength' in response_as_text or 'required' in response_as_text

def test_post_submit_button(client):
    
    response = client.get('/posts/0') 
    response_as_text = response.get_data(as_text=True) 
    assert response.status_code == 200
    assert 'Отправить' in response_as_text

def test_post_images(client):
    response = client.get('/posts')
    assert response.status_code == 200
    assert any(image_id.encode() in response.data for image_id in ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c.jpg'])

def test_non_existing_route(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404
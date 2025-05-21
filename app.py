import random
import re
from functools import lru_cache
from flask import Flask, render_template, request, abort,make_response, redirect, url_for
from faker import Faker

fake = Faker()

app = Flask(__name__)
application = app

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']



PHONE_PATTERN = re.compile(r"^[\d\s\-\.\(\)\+]+$")


def format_phone_number(phone):
   
    digits = re.sub(r"\D", "", phone)
    
    
    if len(digits) not in [10, 11]:
        return None, "Недопустимый ввод. Неверное количество цифр."
    
    
    if not PHONE_PATTERN.match(phone):
        return None, "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
    
    
    if (phone.startswith('+7') or phone.startswith('8')) and len(digits) != 11:
        return None, "Недопустимый ввод. Неверное количество цифр."
    
    
    if not (phone.startswith('+7') or phone.startswith('8')) and len(digits) != 10:
        return None, "Недопустимый ввод. Неверное количество цифр."
    
   
    if len(digits) == 11:
        if digits.startswith("7"):
            digits = "8" + digits[1:]
        return f"{digits[0]}-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:11]}", None
    else:
        return f"8-{digits[0:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:10]}", None

def generate_comments(replies=True):
    comments = []
    for _ in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

@lru_cache
def posts_list():
    return sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list())

@app.route('/posts/<int:index>')
def post(index):
    posts = posts_list()
    if index < 0 or index >= len(posts):
        abort(404)
    
    post = posts[index]
    
    return render_template('post.html', title=post['title'], post=post)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/request-info')
def request_info():
    return render_template(
        'request_info.html',
        url_params=request.args,
        headers=request.headers,
        cookies=request.cookies,
        form_data=request.form
    )


@app.route('/cookies')
def cookies():
    cookie_value = request.cookies.get('my_cookie')

    if not cookie_value:
        generated_cookie = fake.word()
        response = make_response(redirect(url_for('cookies')))
        response.set_cookie('my_cookie', generated_cookie, max_age=60)
        return response

    return render_template('cookies.html', cookie_value=cookie_value)


@app.route('/delete_cookie', methods=['POST'])
def delete_cookie():
    response = make_response(redirect(url_for('cookies')))
    response.delete_cookie('my_cookie')
    return response



@app.route('/phone', methods=['GET', 'POST'])
def phone():
    error = None
    formatted_phone = None
    phone_input = None

    if request.method == 'POST':
        phone_input = request.form.get('phone', '').strip()
        formatted_phone, error = format_phone_number(phone_input)

    return render_template('phone.html', 
                         error=error, 
                         formatted_phone=formatted_phone,
                         phone=phone_input)


if __name__ == '__main__':
    app.run(debug=True, port=8080)

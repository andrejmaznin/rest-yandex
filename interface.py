from flask import Flask
from flask import render_template

user = True
app = Flask(__name__)


@app.route('/')
@app.route('/main')
def main():
    # словарик для теста формы
    # todo: заменить чем-то нормальным
    test = {'orders': [{'weight': '234', 'region': 'ural'},
                       {'weight': '234', 'region': 'ural'},
                       {'weight': '234',     'region': 'ural'}]}

    return render_template('main.html', orders=test, user=user)


@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')


@app.route('/profile')
def profile():
    if user:
        return render_template('profile.html')
    return render_template('sign_in.html')


@app.route('/order')
def order():
    if user:
        return render_template('order.html')
    return render_template('sign_in.html')


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')

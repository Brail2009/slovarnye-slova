from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import random
from data import ALL_WORDS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

def normalize(word):
    return word.lower().replace('ё', 'е')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset_and_start')
def reset_and_start():
    session.clear()
    return redirect(url_for('study'))

@app.route('/study', methods=['GET', 'POST'])
def study():
    if 'words_left' not in session:
        keys = list(ALL_WORDS.keys())
        random.shuffle(keys)
        session['words_left'] = keys
        session['current_index'] = 0
    else:
        words_left = session.get('words_left', [])
        filtered = [w for w in words_left if w in ALL_WORDS]
        if len(filtered) != len(words_left):
            session['words_left'] = filtered
            if session.get('current_index', 0) >= len(filtered):
                session['current_index'] = 0

    # Обработка POST
    if request.method == 'POST':
        user_input = request.form.get('word', '').strip()
        # Проверка на пустое поле
        if not user_input:
            session['error'] = 'Пожалуйста, введите слово.'
            return redirect(url_for('study'))

        current_index = session.get('current_index', 0)
        words_left = session.get('words_left', [])

        if current_index < len(words_left):
            current_word_key = words_left[current_index]
            if current_word_key not in ALL_WORDS:
                session['words_left'] = [w for w in words_left if w != current_word_key]
                return redirect(url_for('study'))

            session['user_input'] = user_input
            if normalize(user_input) == normalize(current_word_key):
                session['result'] = 'correct'
            else:
                session['result'] = 'incorrect'
            session['correct_word'] = current_word_key
            session['correct_meaning'] = ALL_WORDS[current_word_key]['значение']
            session['current_index'] = current_index + 1
        return redirect(url_for('study'))

    # GET – отображение
    result = session.pop('result', None)
    correct_word = session.pop('correct_word', None)
    correct_meaning = session.pop('correct_meaning', None)
    user_input = session.pop('user_input', None)
    error = session.pop('error', None)  # извлекаем ошибку

    words_left = session.get('words_left', [])
    current_index = session.get('current_index', 0)

    if not words_left or current_index >= len(words_left):
        return render_template('finish.html', total=len(words_left))

    current_word_key = words_left[current_index]
    if current_word_key not in ALL_WORDS:
        session['words_left'] = [w for w in words_left if w != current_word_key]
        return redirect(url_for('study'))

    word_data = ALL_WORDS[current_word_key]
    sentence = word_data['sentence']
    meaning = word_data['значение']
    progress = f"{current_index + 1}/{len(words_left)}"

    return render_template(
        'study.html',
        sentence=sentence,
        meaning=meaning,
        result=result,
        correct_word=correct_word,
        correct_meaning=correct_meaning,
        user_input=user_input,
        progress=progress,
        error=error  # передаём ошибку
    )

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
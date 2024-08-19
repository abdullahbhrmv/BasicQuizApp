from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secretkey'
db = SQLAlchemy(app)

# Kullanıcı tablosu
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    best_score = db.Column(db.Float, default=0)

# Quiz Soruları tablosu
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(200), nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)

# Veritabanını oluştur
@app.before_first_request
def create_tables():
    db.create_all()
    if not Question.query.first():
        questions = [
            Question(
                question_text="Python'da AI geliştirmek için en popüler kütüphane hangisidir?",
                option1="NumPy", option2="Pandas", option3="TensorFlow", option4="Django",
                correct_answer="TensorFlow"),
            Question(
                question_text="Python'da makine öğrenmesi algoritmaları için hangi kütüphane kullanılır?",
                option1="Scikit-learn", option2="Flask", option3="Keras", option4="Pillow",
                correct_answer="Scikit-learn"),
            Question(
                question_text="Derin öğrenme modelleri için kullanılan Python kütüphanesi nedir?",
                option1="Seaborn", option2="Keras", option3="Requests", option4="Flask",
                correct_answer="Keras"),
            Question(
                question_text="Yapay sinir ağları geliştirmek için kullanılan Python kütüphanesi hangisidir?",
                option1="TensorFlow", option2="Django", option3="Matplotlib", option4="Scikit-learn",
                correct_answer="TensorFlow"),
            Question(
                question_text="Python'da veri analizi için en çok kullanılan kütüphanelerden biri nedir?",
                option1="NumPy", option2="Pandas", option3="Pygame", option4="Flask",
                correct_answer="Pandas"),
        ]
        db.session.bulk_save_objects(questions)
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect('/index')
        else:
            return render_template('login.html', error='Yanlış e-posta veya şifre!')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('registration.html', error='Bu e-posta zaten kayıtlı!')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('registration.html')

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect('/')
    
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        correct_answers = 0
        questions = Question.query.all()
        for question in questions:
            user_answer = request.form.get(str(question.id))
            if user_answer == question.correct_answer:
                correct_answers += 1
        score = (correct_answers / len(questions)) * 100
        
        # En iyi puanı güncelle
        if score > user.best_score:
            user.best_score = score
            db.session.commit()
        
        return redirect(f'/result?score={score}')

    questions = Question.query.all()
    return render_template('quiz.html', questions=questions, best_score=user.best_score)

@app.route('/result')
def result():
    score = request.args.get('score')
    return render_template('result.html', score=score)

@app.route('/logout', methods=['POST'])
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
    return redirect('/')

if __name__ == "__main__":
    # Veritabanını sıfırdan oluşturmak için
    db.create_all()
    app.run(debug=True)

''' ===================================================
    app.py
    
    We imported Flask, SQLAlchemy to help our
    Python application communicate with a database, 
    Bcrypt for passsword hashing, Migrate for database
    migrations, and several other methods from Flask-Logic 
    for session management
    =================================================== '''

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)



login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)

    app.secret_key = 'secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    return app

''' ===================================================
    end of app.py
    =================================================== '''



''' ===================================================
    models.py
    =================================================== '''

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


class Dish1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    ingredient = db.Column(db.String(100), nullable=False)
    content1 = db.Column(db.String(100), nullable=False)
    content2 = db.Column(db.String(100), nullable=False)
    content3 = db.Column(db.String(100), nullable=False)
    content4 = db.Column(db.String(100), nullable=False)
    content5 = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(10000), nullable=False)

    def __repr__(self):
        return f'{self.username} {self.ingredient} 추천 by {self.username}'


db.create_all()

# from app import db
class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username
'''====================================================
other things

========================================================'''






''' ===================================================
    manage.py
    =================================================== '''

def deploy():
	"""Run deployment tasks."""
	# from app import create_app,db
	from flask_migrate import upgrade,migrate,init,stamp

	app = create_app()
	app.app_context().push()
	db.create_all()

	# migrate database to latest revision
	init()
	stamp()
	migrate()
	upgrade()

import os

directory_name = "migrations"
if os.path.exists(directory_name):
	pass
else:
	deploy()

''' ===================================================
    forms.py
    =================================================== '''
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
)

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp ,Optional
import email_validator
from flask_login import current_user
from wtforms import ValidationError,validators


class login_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )


class register_form(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            ),
        ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(
        validators=[
            InputRequired(),
            Length(8, 72),
            EqualTo("pwd", message="비밀버호는 일치해야 합니다!"),
        ]
    )


    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("이 메일은 지금 쓰이고있습니다.")

    def validate_uname(self, uname):
        if User.query.filter_by(username=uname.data).first():
            raise ValidationError("유저 이름은 벌써쓰이고 있습니다")
        


    
''' ===================================================
    main.py
    =================================================== '''

from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session
)

from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError


from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app,db,login_manager,bcrypt
# from models import User
# from forms import login_form,register_form



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)

@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template("index.html",title="Home")

@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('main'))
            else:
                flash("틀린 유저이름이나 비밀번호를 입력하셨습니다!", "danger")
        except Exception as e:
            flash("틀린 유저이름이나 비밀번호를 입력하셨습니다!", "danger")

    return render_template("auth.html",
        form=form,
        text="로그인",
        title="Login",
        btn_action="Login"
        )




# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"계정 만들기가 완료 됐습니다. 축하합니다!", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:

            db.session.rollback()
            flash(f"Something went wrong!", "danger")

        except IntegrityError:

            db.session.rollback()
            flash(f"이 유저는 이미 가입 되었습니다!", "warning")

        except DataError:

            db.session.rollback()
            flash(f"Invalid Entry", "warning")

        except InterfaceError:

            db.session.rollback()
            flash(f"Error connecting to the database", "danger")

        except DatabaseError:

            db.session.rollback()
            flash(f"Error connecting to the database", "danger")

        except BuildError:

            db.session.rollback()
            flash(f"An error occured !", "danger")
            
    return render_template("auth.html",
        form=form,
        text="계정 만들기",
        title="회원가입",
        btn_action="가입하기"
        )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/main', methods=("GET", "POST"), strict_slashes=False)

def main():
    recipe_list = Dish1.query.all()
    return render_template('main.html', data=recipe_list)

@app.route('/detail/<username>')
def detail(username):
    dish = Dish1.query.filter_by(username=username).all()
    return render_template('detail.html', data=dish)


@app.route('/main/delete/<int:id>')
def recipe_delete(id):
    
    recipe_to_delete = Dish1.query.get_or_404(id)

    try:
        db.session.delete(recipe_to_delete)
        db.session.commit()
        return redirect('/main/')
    except:
        return "There was a problem deleting that song"

@app.route('/main/create/')
def recipe_create():
    # form으로 데이터 입력 받기
    username_receive = request.args.get("username")
    ingredient_receive = request.args.get("ingredient")
    content_receive1 = request.args.get("content1")
    content_receive2 = request.args.get("content2")
    content_receive3 = request.args.get("content3")
    content_receive4 = request.args.get("content4")
    content_receive5 = request.args.get("content5")
    image_receive = request.args.get("image_url")

    # 데이터를 DB에 저장하기
    dish = Dish1(username=username_receive, ingredient=ingredient_receive, content1=content_receive1, content2=content_receive2,content3=content_receive3,content4=content_receive4, content5=content_receive5,image_url=image_receive)
    db.session.add(dish)
    db.session.commit()
    return redirect(url_for('recipe', username=username_receive))


if __name__ == "__main__":
    app.run(debug=True)
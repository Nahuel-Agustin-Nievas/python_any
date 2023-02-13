from io import BytesIO

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, send_file, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import io
import os
import uuid
from functools import wraps
import functools





# configuration of a context path for database

# UPLOAD_FOLDER = os.path.abspath("./uploads/")  probar en caso de que la ruta de abajo falle

f = os.path.abspath('app.py')
 
BASE_DIR = os.path.dirname(f)
DB_FILE = os.path.join(BASE_DIR, "database", "blog.db")
DB_URI = "sqlite:///" + DB_FILE
SECRET_KEY = "1234"
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = set(["pdf", "doc", "docx", "txt"])


# the next function checks the files extension

def allowed_files(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
# app.secret_key = SECRET_KEY  # linea para testear multiple usuarios
db = SQLAlchemy(app)
# login_manager = LoginManager()
# login_manager.init_app(app)


@app.context_processor
def make_context_current_user():
    current_user = None
    if 'current_user' in session:
        current_user = session['current_user']
    return dict(current_user=current_user)


def current_user():
    user_id = session.get("user_id")
    if user_id is not None:
        return User.query.get(user_id)
    return None

def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper





#the following lines help with the redirection to the login page in case the user is not logged in
# login_manager.login_view = "login"


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# the next line helps with the RuntimeError: Working Outside of Application Context
app.app_context().push()
       

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)
    # is_active = db.Column(db.Boolean, default=True)

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.id

    def is_user_active(self):
        return self.is_active
 

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    text = db.Column(db.String, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    


class PostFile(db.Model):
    __tablename__ = "post_files"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    filename = db.Column(db.String(50), nullable=True)
    data = db.Column(db.LargeBinary, nullable=True)
    file_type = db.Column(db.String(10), nullable=True)
    download_url = db.Column(db.String(200), nullable=True)


# nueva tabla para probar multiple usuarios

# class Session(db.Model):
#     __tablename__ = "sessions"
#     id = db.Column(db.Integer, primary_key=True)
#     session_id = db.Column(db.String(50), unique=True, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def index():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        posts = Post.query.filter_by(is_published=True).all()
        post_files = PostFile.query.all()
        return render_template("index.html", posts=posts, post_files=post_files, current_user=user)
    else:
        return redirect("/login")
    


@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error_message = "Usuario ya existente."
        else:
            password = request.form.get('password')
            hashed_password = generate_password_hash(password, method='sha256')
            user = User(username=username, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
    return render_template('register.html', error_message=error_message)


# The following lines are the default login route

@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Aquí debes hacer la verificación del usuario y la contraseña
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/")
        else:
            # Mensaje de error para el usuario
            error_message = "Usuario o contraseña incorrecta."
    return render_template("login.html", error_message=error_message)
    
    

#new route for login and try multiple users 


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error_message = ""
#     if request.method == "POST":
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = User.query.filter_by(username=username).first()

#         if user and check_password_hash(user.password, password):
#             session_id = str(uuid.uuid4()) # Genera un ID de sesión único
#             session['session_id'] = session_id # Guarda el ID de sesión en la sesión actual
#             new_session = Session(session_id=session_id, user_id=user.id)
#             db.session.add(new_session)
#             db.session.commit()
#             login_user(user)
#             return redirect('/')
#         else:
#             error_message = "Usuario o contraseña incorrecta."
#     return render_template('login.html', error_message=error_message)




# the following lines are the default logout routes
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     session.pop('session_id', None) # Elimina el ID de sesión de la sesión actual
#     return redirect('/')


@app.route('/add') 
def add():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("add.html") 



@app.route('/create', methods=['GET','POST'])
@login_required
def create_post():
    error_message = ""
    if request.method == 'POST':
        title = request.form.get('titulo')
        text = request.form.get('texto')
        status = request.form.get('status')
        is_published = False
        if status == "published":
            is_published = True
        files = request.files.getlist("ourfile[]")
        post = Post(title=title, text=text, author=current_user(), is_published=is_published)
        db.session.add(post)
        db.session.flush()  # flush to get the post's ID
        if files and files[0].filename != '':
            for f in files: # iterate over the uploaded files
                if f.filename.lower().endswith(".pdf") or f.filename.lower().endswith(".txt") or f.filename.lower().endswith(".doc") or f.filename.lower().endswith(".jpg") or f.filename.lower().endswith(".jpeg") or f.filename.lower().endswith(".png"):
                    if f.filename.lower().endswith(".jpg") or f.filename.lower().endswith(".png") or f.filename.lower().endswith(".jpeg"):
                        # Open image and resize while maintaining aspect ratio
                        image = Image.open(f)
                        file_type = image.format
                        width = image.width
                        height = image.height
                        if width > height:
                            image.thumbnail((1920, 1080))
                        else:
                            image.thumbnail((1080, 1920))
                        # convert image to bytes
                        img_bytes = io.BytesIO()
                        image.save(img_bytes, format=image.format)
                        img_bytes = img_bytes.getvalue()
                        # generate a unique download URL for the file
                        download_url = f"/download2/{post.id}/{f.filename}"
                        post_file = PostFile(post_id=post.id, filename=f.filename, data=img_bytes, download_url=download_url, file_type=file_type)
                        db.session.add(post_file)
                    else:
                        # generate a unique download URL for the file
                        download_url = f"/download2/{post.id}/{f.filename}"
                        post_file = PostFile(post_id=post.id, filename=f.filename, data=f.read(), download_url=download_url)
                        db.session.add(post_file)
                else:
                    error_message = "Solo se permiten archivos pdf, txt, doc, jpg o png."
                if error_message:
                    return render_template("add.html", error_message=error_message)
        db.session.commit()
        return render_template("add.html")
        
    





@app.route('/drafts', methods=['GET'])
@login_required
def drafts():
    post_id = request.args.get('post_id')
    drafts = Post.query.filter_by(id=post_id).all()
    post_files = PostFile.query.filter_by(post_id=post_id).all()
    return render_template("drafts.html", drafts=drafts, post_files=post_files)




@app.route('/post_action/<int:post_id>', methods=['POST'])
@login_required
def post_action(post_id):
    post = Post.query.filter_by(id=post_id, user_id=current_user().id).first()
    files = request.files.getlist("ourfile[]")
    error_message = ""
    if post:
        action = request.form.get('action')
        if action == "publish":
            post.is_published = True
            post.is_deleted = False
            post.title = request.form.get('title')
            post.text = request.form.get('text')
            post.date = datetime.now()
            if files and files[0].filename != '':
                for f in files: # iterate over the uploaded files
                    if f.filename.lower().endswith(".pdf") or f.filename.lower().endswith(".txt") or f.filename.lower().endswith(".doc") or f.filename.lower().endswith(".jpg") or f.filename.lower().endswith(".jpeg") or f.filename.lower().endswith(".png"):
                        if f.filename.lower().endswith(".jpg") or f.filename.lower().endswith(".png") or f.filename.lower().endswith(".jpeg"):
                            # Open image and resize while maintaining aspect ratio
                            image = Image.open(f)
                            file_type = image.format
                            image.thumbnail((1920, 1080))
                            # convert image to bytes
                            img_bytes = io.BytesIO()
                            image.save(img_bytes, format=image.format)
                            img_bytes = img_bytes.getvalue()
                            # generate a unique download URL for the file
                            download_url = f"/download2/{post.id}/{f.filename}"
                            post_file = PostFile(post_id=post.id, filename=f.filename, data=img_bytes, download_url=download_url, file_type=file_type)
                            db.session.add(post_file)
                        else:
                            # generate a unique download URL for the file
                            download_url = f"/download2/{post.id}/{f.filename}"
                            post_file = PostFile(post_id=post.id, filename=f.filename, data=f.read(), download_url=download_url)
                            db.session.add(post_file)
                    else:
                        error_message = "Solo se permiten archivos pdf, txt, doc, jpg o png." 
                    if error_message:
                        return render_template("drafts.html", error_message=error_message)
        elif action == "edit":
            post.title = request.form.get('title')
            post.text = request.form.get('text')
            post.date = datetime.now()
            if files and files[0].filename != '':
                for f in files: # iterate over the uploaded files
                    if f.filename.lower().endswith(".pdf") or f.filename.lower().endswith(".txt") or f.filename.lower().endswith(".doc") or f.filename.lower().endswith(".jpg") or f.filename.lower().endswith(".jpeg") or f.filename.lower().endswith(".png"):
                        if f.filename.lower().endswith(".jpg") or f.filename.lower().endswith(".png") or f.filename.lower().endswith(".jpeg"):
                            # Open image and resize while maintaining aspect ratio
                            image = Image.open(f)
                            file_type = image.format
                            image.thumbnail((1920, 1080))
                            # convert image to bytes
                            img_bytes = io.BytesIO()
                            image.save(img_bytes, format=image.format)
                            img_bytes = img_bytes.getvalue()
                            # generate a unique download URL for the file
                            download_url = f"/download2/{post.id}/{f.filename}"
                            post_file = PostFile(post_id=post.id, filename=f.filename, data=img_bytes, download_url=download_url, file_type=file_type)
                            db.session.add(post_file)
                        else:
                            # generate a unique download URL for the file
                            download_url = f"/download2/{post.id}/{f.filename}"
                            post_file = PostFile(post_id=post.id, filename=f.filename, data=f.read(), download_url=download_url)
                            db.session.add(post_file)
                    else:
                        error_message = "Solo se permiten archivos pdf, txt, doc, jpg o png."

                    if error_message:
                        return render_template("drafts.html", error_message=error_message)
    db.session.commit()
    return redirect(url_for('drafts', post_id=post_id))

   



@app.route('/all_posts')
@login_required
def all_posts():
    posts = Post.query.filter_by(user_id=current_user().id).all()
    post_files = PostFile.query.all()
    return render_template("all_posts.html", posts=posts, post_files=post_files)



@app.route('/posts', methods=['GET'])
def posts():
  status = request.args.get('status')
  posts = Post.query.filter_by(user_id=current_user().id).all()
  if status == 'published':
    posts = Post.query.filter_by(user_id=current_user().id, is_published=True).all()
    post_files = PostFile.query.all()
  elif status == 'archived':
    posts = Post.query.filter_by(user_id=current_user().id, is_deleted=True).all()
    post_files = PostFile.query.all()
  elif status == 'draft':
    posts = Post.query.filter_by(user_id=current_user().id, is_published=False, is_deleted=False).all()
    post_files = PostFile.query.all()
  else:
    posts = Post.query.filter_by(user_id=current_user().id).all()
    post_files = PostFile.query.all()
  return render_template('all_posts.html', posts=posts, post_files=post_files)






@app.route('/delete_final', methods=['POST'])
def delete_final():
    post_id = request.form.get('post_id')
    post = db.session.query(Post).filter(Post.id == post_id).first()
    db.session.delete(post)
    post_files= db.session.query(PostFile).filter(PostFile.post_id == post_id).all()
    for post_file in post_files:
        db.session.delete(post_file) 
    db.session.commit()
    return render_template('all_posts.html')



@app.route('/delete', methods=['POST'])
@login_required
def delete():
    post_id = request.form.get('post_id')
    post = db.session.query(Post).filter(Post.id == post_id).first()
    post.is_deleted = True
    post.is_published = False
    db.session.commit()
    return redirect('/')


@app.route('/delete_draft', methods=['POST'])
def delete_draft():
    post_id = request.form.get('post_id')
    post = db.session.query(Post).filter(Post.id == post_id).first()
    if post:
        db.session.delete(post)
        post_files = db.session.query(PostFile).filter(PostFile.post_id == post_id).all()
        for post_file in post_files:
            db.session.delete(post_file) 
        db.session.commit()
    return redirect(url_for('drafts'))


@app.route('/delete_file', methods=['POST'])
def delete_file():
    file_id = request.form.get('file_id')
    file_to_delete = PostFile.query.filter_by(id=file_id).first()
    post_id = file_to_delete.post_id  
    db.session.delete(file_to_delete)
    db.session.commit()
    return redirect(url_for('drafts', post_id=post_id))  # pasa post_id como argumento





# the following route works only saving the files in a local folder


# @app.route('/upload', methods=['GET','POST'])
# def upload():
#     if request.method == 'POST':
#         if "ourfile" not in request.files:
#             return "The form has no file part."
#         f = request.files["ourfile"]
#         if f.filename == "":
#             return "No File Selected."  
#         if f and allowed_files(f.filename):
#             filename = secure_filename(f.filename)
#             f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
#             return redirect(url_for("get_file", filename=filename))
#         return "File not allowed"

@app.route('/download',  methods=['POST'])
def download():
    post_id = request.form.get('post_download_id')
    return redirect('/download2/' + post_id)

@app.route('/image/<int:id>')
def image(id):
    post_file = PostFile.query.get(id)
    if post_file:
        return send_file(io.BytesIO(post_file.data), mimetype=f'image/{post_file.file_type.lower()}')
    else:
        return "Archivo no encontrado", 404
    




@app.route('/download2/<upload_id>/<filename>', methods=['POST'])
def download_file(upload_id, filename):
    post_file = PostFile.query.filter_by(post_id=upload_id, filename=filename).first()
    if not post_file:
        return "File not found"
    # print (post_file)
    return send_file(BytesIO(post_file.data), as_attachment=True, download_name=post_file.filename)
    
    


@app.before_first_request
def create_tables():
    db.create_all()





# if __name__ == "__main__":
#     # db.create_all()
#     app.run(debug=True, port = 7060)  

# if __name__ == "__main__":
#     db.create_all()
#     app.run(debug=False, host='0.0.0.0', port=80)
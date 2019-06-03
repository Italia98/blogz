from flask import Flask, flash ,request, redirect, render_template , session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "blah"


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer , db.ForeignKey('user.id'))

    def __init__(self,title,body,owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog" ,backref="owner")

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.route('/blog')
def index():
    id = request.args.get('id')
    
    if id:
        id = int(id)
        blog = Blog.query.get(id)
        return render_template("blogentry.html",blog = blog, blogname=blog.title , blogtext=blog.body)
    else:
        blogs = Blog.query.all()
        return render_template("main.html",title="My title",blogs=blogs)

@app.route('/newpost' , methods=['GET'])
def new_post():
    if 'user' not in session:
        return redirect('/login')
    else:
        return render_template("newblog.html")

@app.route('/newpost' , methods=['POST'])
def add_new_post():
    if 'user' not in session:
        redirect('/login')
    blogname = request.form['blogname']
    blogtext = request.form['blogtext']

    name_error="Enter a title please"
    text_error="Enter a text please"
    if not blogname and not blogtext:
        flash(name_error)
        flash(text_error)
        return redirect('/newpost')
    elif not blogname:
        flash(name_error)
        return redirect('/newpost')
    elif not blogtext:
        flash(text_error)
        return redirect('/newpost')
    else:
        #session['user'] = user.username
        owner = User.query.filter_by(username=session['user']).first()
        new_blog_post = Blog(blogname,blogtext,owner)
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect("blog"+"?id="+str(new_blog_post.id))


@app.route('/login', methods=['GET','POST'])
def log_in():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            password = request.form['password']
            my_pw = user.password
            if password == my_pw:
                session['user'] = user.username
                flash('welcome back, '+user.username)
                return redirect("/newpost")
        flash('bad username or password')
        return redirect("/login")

@app.route('/signup' , methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if len(username) < 3:
            flash('zoiks! "' + username + '" does not seem like a valid username')
            return redirect('/signup')
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash('yikes! "' + username + '" is already taken and password reminders are not implemented')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/")
    else:
        return render_template('signup.html')


@app.route("/logout", methods=['GET','POST'])
def logout():
    if 'user' in session:
        del session['user']
    return redirect("/")

@app.route("/")
def home():
    id = request.args.get('user')
    
    if id:
        id = int(id)
        blogs = Blog.query.filter_by(owner_id=id).all()
        return render_template("main.html", blogs=blogs)
    else:
        usernames = User.query.all()
        return render_template('index.html',usernames=usernames)

@app.before_request
def before_request():
    if 'user' not in session and request.endpoint == 'newpost':
        return redirect('/login')





if __name__ == '__main__':
    app.run()
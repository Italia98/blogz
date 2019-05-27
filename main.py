from flask import Flask, flash ,request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:beproductive@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "blah"


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self,title,body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    blogs = Blog.query.all()
    return render_template("main.html",title="My title",blogs=blogs)

@app.route('/newpost' , methods=['GET'])
def new_post():
    return render_template("newblog.html")

@app.route('/newpost' , methods=['POST'])
def add_new_post():
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
        new_blog_post = Blog(blogname,blogtext)
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect("blog"+"?id="+str(new_blog_post.id))

@app.route('/blog' , methods=['GET'])
def blog_entry():
    id = int(request.args.get('id'))
    blog = Blog.query.get(id)
    return render_template("blogentry.html", blogname=blog.title , blogtext=blog.body)




if __name__ == '__main__':
    app.run()
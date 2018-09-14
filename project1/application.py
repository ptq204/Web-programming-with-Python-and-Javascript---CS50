import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('sign_up.html')

@app.route("/login", methods=["POST"])
def check_login():
    usr = request.form.get('username')
    pas = request.form.get('password')
    user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
        {"username":usr, "password":pas}).fetchone()
    if(user is None):
        return render_template('error.html', message='User does not exist, try again or', flag=1)
    session['userID'] = user.userid
    session['username'] = user.username
    return redirect(url_for('search', check=user.userid))

@app.route("/signup", methods=["POST"])
def check_signup():
    usr = request.form.get('username')
    pas = request.form.get('password')
    user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
                           {"username":usr, "password":pas}).rowcount

    users_cnt = db.execute("SELECT * FROM users").rowcount
    if(user != 0):
        return render_template('error.html', message='User has existed, try another account', flag=2)
    db.execute("INSERT INTO users VALUES(:userid, :username, :password)", 
              {"userid":str(users_cnt+1), "username":usr, "password":pas})
    db.commit()
    session['userID'] = int(users_cnt + 1)
    session['username'] = usr
    return redirect(url_for('search', check=int(users_cnt+1)))


@app.route("/search/<int:check>")
def search(check):
    if(check != 0):
        return render_template("search.html")

@app.route('/results', methods=["POST"])
def results():
    books = []
    query = request.form.get('query')
    query = '%'+query+'%'
    try:
        books = db.execute("SELECT * FROM books WHERE (isbn LIKE :query) OR (title LIKE :query) OR (author LIKE :query) OR (year LIKE :query)"
        , {"query" : query}).fetchall()
    except ValueError:
        return render_template('error.html', message='Some error occured', flag=0)

    if(len(books) > 0):
        return render_template('search_results.html', books=books)
    else:
        return render_template('error.html', message='Can not find any books', flag=0)

@app.route('/book/<string:ISBN>/<string:Author>/<string:Title>/<string:Year>')
def book(ISBN, Title, Author, Year):
    reviews = db.execute("SELECT * FROM reviews WHERE bookid = :bookid", {"bookid" : ISBN}).fetchall()
    return render_template('book_info.html', ISBN = ISBN, Title = Title, Author = Author, Year = Year, reviews = reviews, userid=session['userID'])

@app.route('/comment/<string:ISBN>/<string:userid>', methods=["POST"])
def add_comment(ISBN, userid):
    cmt = request.form.get('comment')
    rating = float(request.form.get('rating'))
    user = db.execute("SELECT * FROM reviews WHERE bookid = :bookid AND userid = :userid",
                      {"bookid":ISBN, "userid":userid}).rowcount
    if(user != 0):
        return render_template('error.html', message='You can not comment on one book twice', flag=0)
    db.execute("INSERT INTO reviews VALUES(:bookid, :userid, :username, :comment, :rating)",
               {"bookid":ISBN, "userid":userid, "username":session['username'], "comment":cmt, "rating":rating})
    db.commit()
    return render_template('success.html', message='Uploaded your comment!')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
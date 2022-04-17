from flask import Flask, render_template, redirect, request, url_for, abort
from flask_login import LoginManager, login_user, login_required, \
    logout_user, current_user
from data import db_session
from data.users_model import User, subscriptions
from data.register_form import RegisterForm
from sqlalchemy import or_, and_
from data.login_form import LoginForm
from data.post_form import PostForm
from data.posts_model import Post
from data.search_form import SearchForm
import os
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


@app.route('/', methods=['GET'])
def empty():
    return redirect(url_for('feed'))


@app.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
    search = SearchForm()
    db_sess = db_session.create_session()
    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        post = Post(
            text=form.text.data,
            author=current_user.id
        )
        db_sess.add(post)
        db_sess.commit()
        return redirect(url_for('feed'))
    page = request.args.get('page', 0, type=int)
    per_page = 7
    subs = db_sess.query(subscriptions).filter(subscriptions.c.user == current_user.id).all()
    subs = [current_user.id] + [i[1] for i in subs]
    posts = db_sess.query(Post).order_by(Post.created.desc()).filter(Post.author.in_(subs)).all()
    posts = posts[page * per_page:(page + 1) * per_page]
    if page != 0:
        return render_template('posts.html', posts=posts, page=page + 1)
    return render_template('index.html', form=form, posts=posts, title='новости', page=page + 1,
                           search=search)


@app.route('/register', methods=['GET', 'POST'])
def register():
    search = SearchForm()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match", search=search)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(or_(User.email == form.email.data, User.id == form.id.data)) \
                .first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists", search=search)
        user = User(
            id=form.id.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, search=search)


@app.route('/login', methods=['GET', 'POST'])
def login():
    search = SearchForm()
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == form.id.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/feed")
        return render_template('login.html', message="Wrong login or password", form=form,
                               search=search)
    return render_template('login.html', title='Authorization', form=form, search=search)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/user/', methods=['POST'])
def profile_():
    search = SearchForm()
    id = search.id.data
    if id:
        return redirect(url_for('profile', id=id))


@app.route('/user/<id>', methods=['GET', 'POST'])
def profile(id):
    search = SearchForm()
    form = PostForm()
    db_sess = db_session.create_session()
    if request.method == 'POST' and form.validate_on_submit():
        post = Post(
            text=form.text.data,
            author=current_user.id
        )
        db_sess.add(post)
        db_sess.commit()
        return redirect(url_for('profile', id=id))

    page = request.args.get('page', 0, type=int)
    per_page = 7
    posts = db_sess.query(Post).filter(Post.author == id).order_by(Post.created.desc())
    posts = posts[page * per_page:(page + 1) * per_page]
    if page != 0:
        return render_template('posts.html', posts=posts, page=page + 1, nickname=id)

    sub = False
    if current_user.is_authenticated and db_sess.query(subscriptions).filter(
            and_(subscriptions.c.user == current_user.id,
                 subscriptions.c.subscribe_on == id)).first():
        sub = True

    if not db_sess.query(User).filter(User.id == id).first():
        id = None

    return render_template('profile.html', posts=posts, title=id, nickname=id, form=form,
                           page=page + 1, is_sub=sub, search=search)


@app.route('/subscribe/<id>', methods=['POST', 'GET'])
@login_required
def subscribe(id):
    db_sess = db_session.create_session()
    if id != current_user.id and db_sess.query(User).filter(User.id == id).first():
        subscribe = db_sess.query(subscriptions).filter(subscriptions.c.user == current_user.id,
                                                        subscriptions.c.subscribe_on == id).first()
        if subscribe:
            d = subscriptions.delete().where(
                and_(subscriptions.c.user == current_user.id, subscriptions.c.subscribe_on == id))
            db_sess.execute(d)
            db_sess.commit()
        else:
            d = subscriptions.insert().values({'user': current_user.id, 'subscribe_on': id})
            db_sess.execute(d)
            db_sess.commit()
    return redirect(url_for('profile', id=id))


@app.route('/post_delete/<int:id>')
@login_required
def delete_post(id):
    redirect_url = request.args.get('redirect_url')
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id, Post.author == current_user.id).first()
    if post:
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    print(redirect_url)
    return redirect(redirect_url, code=302)


def main():
    db_session.global_init("db/social.sqlite")
    port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    serve(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()

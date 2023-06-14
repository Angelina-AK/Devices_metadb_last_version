from flask import Blueprint, request, render_template, flash, url_for, redirect
from flask_login import login_required
from app.models import Post, User

from app.models import db
from werkzeug.exceptions import abort

posts_api = Blueprint('posts_api', __name__, template_folder='templates/posts')


def get_post(id):
    post = Post.query.get(id)
    if post is None:
        abort(404)
    return post


@posts_api.route('/posts')
@login_required
def posts_view():
    posts = Post.query.all()
    namepage = "Записи"
    return render_template('posts.html', posts=posts, namepage=namepage)


@posts_api.route('/posts/create', methods=('GET', 'POST'))
@login_required
def post_create():
    namepage = "Создание записи"
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Post(title, content)
        if not title:
            flash('Title is required!')
        else:
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('posts_api.posts_view'))
    """elif request.method == 'GET':
        posts = Post.query.all()
        results = [
            {
                "title": post.title,
                "content": post.content
            } for post in posts]

        return {"count": len(results), "posts": results}
        """
    return render_template('post_create.html', namepage=namepage)


@posts_api.route('/posts/<int:id>')
@login_required
def post_view(id):
    post = get_post(id)
    return render_template('post.html', post=post)


@posts_api.route('/posts/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def post_edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            user = User.query.get(1)
            post.title = title
            post.content = content
            db.session.commit()

            return redirect(url_for('posts_api.posts_view'))

    return render_template('post_edit.html', post=post)


@posts_api.route('/posts/<int:id>/delete', methods=('POST',))
@login_required
def post_delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('posts_api.posts_view'))

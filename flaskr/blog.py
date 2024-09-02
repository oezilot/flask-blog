from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# this is the route to where you create blog posts
@bp.route('/create', methods=('GET', 'POST'))
@login_required # the login is required so that the user can upload blog posts...otherwise its not possible!
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        # here is defined what happens if the user doesnt fill out the full blog
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        # here the data of the blog posts are inserted into the table called post
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            # this generates the url for the index-function which displays all the blog posts
            # redirect sends a http redirect response to the client
            # redirects the user to the blog page
            return redirect(url_for('blog.index'))

    # if the request method is GET the function renders the create.html template
    # the user creates a blo on the create.html template but ends up on the blog.html when created a post to view the othre posts
    return render_template('blog/create.html')

# blog update, delete and avoid duplicates
def get_post(id, check_author=True): # chacks if the loggedin user is the author of the post
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


# updating the blog posts
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

# deleting files (a part of the update template) the deleted content goes to the path id/delete
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

    
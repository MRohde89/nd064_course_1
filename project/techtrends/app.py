import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(message)s'
        )

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.config['connection_count'] += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['connection_count'] = 0

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logger.debug(f"Article with id: {post_id} not found")
      return render_template('404.html'), 404
    else:
      logger.debug(f"Article: '{post['title']}' Retrieved")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.debug('Retrieved About us page')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            logger.debug(f"New Article Created: '{title}'")
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz', methods=('GET',))
def healthz():
    return jsonify(result= 'OK - healthy')

@app.route('/metrics', methods=('GET',))
def metrics():
    conn = get_db_connection()
    number_of_posts = conn.execute('SELECT COUNT(*) FROM posts').fetchall()
    return jsonify(
            db_connection_count= app.config['connection_count'],
            post_count = number_of_posts[0][0]
            )


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')

import secrets
import os
from zipfile import ZipFile
import zipfile
import io

from PIL import Image

from flask import render_template, url_for, flash, redirect, request, abort
from goc_portal import app, db, bcrypt, mail
from goc_portal.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm, ClassifierMLForm
from goc_portal.models import User, Post, MLClassifier
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

cwd = os.getcwd()

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    # get 5 posts from db for every page order by create date descending
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    # if current user is authentificated redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # hash pwd
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        # create new user
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        # add user to db
        db.session.add(user)
        db.session.commit()
        # show success msg
        flash(f'Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # if current user is authentificated redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # check suer esists
        user = User.query.filter_by(email=form.email.data).first()
        # if user exists and password is valid
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # login user
            login_user(user, remember=form.remember.data)
            # get next parameter from url
            next_page = request.args.get('next')
            # redirect used ternary conditional
            #return redirect(next_page) if next_page else (url_for('home'))
            return redirect (url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    # logout user
    logout_user()
    # redirect to home
    return redirect(url_for('home'))

def save_picture(form_picture):
    # generate rnd hex
    rnd_hex = secrets.token_hex(8)
    # get file extension
    _, f_ext = os.path.splitext(form_picture.filename)
    # combine hex with file extension
    picture_fn = rnd_hex + f_ext
    # join root path file with filename
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    # resize and save image
    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn
    
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        # check and save picture data
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        # update current name and email
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your acount has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        # fill username and email
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    
    if form.validate_on_submit():
        t_tags = form.tag.data.split(',')
        # add hashtag prefix if it not existing
        a_tags = ["#" + tag.strip() for tag in t_tags]
        tags = str(a_tags).replace('[','').replace(']','')
        
        # save post to db
        post = Post(title=form.title.data, content = form.content.data, tag=str(tags), author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form = form, legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    #post = Post.query.get_or_404(post_id)
    post = Post.query.get(post_id)
    
    if post is None:
        return render_template('errors/404.html')
    
    
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        #abort(403)
        return render_template('errors/403.html')
        
    form = PostForm()
    # update post
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        
        t_tags = form.tag.data.split(',')
        tags = ' #'.join(t_tags).join(', ')
        post.tag = tags
        db.session.commit()
        flash("Your post has been updated", 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        # write existing content
        form.title.data = post.title
        form.content.data = post.content
        form.tag.data = post.tag

    return render_template('create_post.html', title="Update Post", form = form, legend = "Update Post")

@app.route("/classifier/new", methods=['GET', 'POST'])
@login_required
def new_classifierml():
    form = ClassifierMLForm()
    
    if form.validate_on_submit():
        title = form.title.data
        if request.method == 'POST':
        # Get the uploaded file from the form
            zip_file = request.files['zipedclassifier']
            print(zip_file)

            if zip_file:
            # Read the contents of the zip file into memory
                zip_contents = io.BytesIO(zip_file.read())
            
                zip_path = os.path.join(app.root_path, 'static/projects', str(title) )
                print(zip_path)
                
                # Unzip the contents of the file into a temporary directory
                with zipfile.ZipFile(zip_contents) as myzip:
                    myzip.extractall(zip_path)
                
                # Read the contents of the unzipped file and print it out
                # list to store files
                for root, dirs, files in os.walk(zip_path):
                    level = root.replace(zip_path, '').count(os.sep)
                    indent = ' ' * 4 * (level)
                    print('{}{}/'.format(indent, os.path.basename(root)))
                    subindent = ' ' * 4 * (level + 1)
                    for f in files:
                        print('{}{}'.format(subindent, f))
                flash('File uploaded and unzipped successfully!')
                    
                #flash('File uploaded and unzipped successfully!')

        
        
        # save post to db
        # post = MLClassifier(title=form.title.data, image_file = '')
        # db.session.add(post)
        # db.session.commit()
        #flash('Your post has been created!','success')
        return redirect(url_for('home'))
    return render_template('ml_classifier_new.html', title='New ML Classifier', form = form, legend='New ML Classifier')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        #abort(403)
        return render_template('errors/403.html')
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    # get user or not found error
    user = User.query.filter_by(username=username).first_or_404()
    # get 5 posts from db for every page order by create date descending
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    
    return render_template('user_posts.html', posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='goc_noreply@insaindev.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
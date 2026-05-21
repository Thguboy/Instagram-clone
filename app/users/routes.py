import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.forms import EditProfileForm
from PIL import Image

users_bp = Blueprint('users', __name__)


def save_avatar(form_image):
    random_hex = uuid.uuid4().hex
    _, ext = os.path.splitext(form_image.filename)
    filename = 'avatar_' + random_hex + ext
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    img = Image.open(form_image)
    img = img.resize((300, 300), Image.Resampling.LANCZOS)
    img.save(filepath, quality=90)
    return filename


@users_bp.route('/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    from app.models import Post
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template('users/profile.html', user=user, posts=posts)


@users_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        if form.avatar.data:
            # Delete old avatar if not default
            if current_user.avatar != 'default_avatar.png':
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)
            current_user.avatar = save_avatar(form.avatar.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        current_user.website = form.website.data
        db.session.commit()
        flash('Profil yangilandi!', 'success')
        return redirect(url_for('users.profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.full_name.data = current_user.full_name
        form.bio.data = current_user.bio
        form.website.data = current_user.website
    return render_template('users/edit_profile.html', form=form)


@users_bp.route('/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        return jsonify({'error': "O'zingizni kuzata olmaysiz"}), 400
    current_user.follow(user)
    db.session.commit()
    return jsonify({
        'following': True,
        'followers_count': user.followers_count
    })


@users_bp.route('/<username>/unfollow', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        return jsonify({'error': "O'zingizni kuzatishdan chiqara olmaysiz"}), 400
    current_user.unfollow(user)
    db.session.commit()
    return jsonify({
        'following': False,
        'followers_count': user.followers_count
    })


@users_bp.route('/<username>/followers')
@login_required
def followers_list(username):
    user = User.query.filter_by(username=username).first_or_404()
    followers = user.followers_list.all()
    return render_template('users/followers.html', user=user, users_list=followers, title='Kuzatuvchilar')


@users_bp.route('/<username>/following')
@login_required
def following_list(username):
    user = User.query.filter_by(username=username).first_or_404()
    following = user.followed.all()
    return render_template('users/followers.html', user=user, users_list=following, title='Kuzatilganlar')

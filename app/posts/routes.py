import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Post, Comment, Like
from app.forms import PostForm, CommentForm
from PIL import Image

posts_bp = Blueprint('posts', __name__)


def save_image(form_image):
    """Save uploaded image with UUID name and resize."""
    random_hex = uuid.uuid4().hex
    _, ext = os.path.splitext(form_image.filename)
    filename = random_hex + ext
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    # Resize image
    img = Image.open(form_image)
    max_size = (1080, 1080)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    img.save(filepath, quality=85)

    return filename


@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        image_file = save_image(form.image.data)
        post = Post(
            image=image_file,
            caption=form.caption.data or '',
            location=form.location.data or '',
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Post muvaffaqiyatli yaratildi!', 'success')
        return redirect(url_for('main.feed'))
    return render_template('posts/create.html', form=form)


@posts_bp.route('/<int:post_id>')
@login_required
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    comments = post.comments.order_by(Comment.created_at.desc()).all()
    return render_template('posts/detail.html', post=post, form=form, comments=comments)


@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        db.session.commit()
        liked = True
    return jsonify({'liked': liked, 'likes_count': post.likes_count})


@posts_bp.route('/<int:post_id>/save', methods=['POST'])
@login_required
def save_post(post_id):
    from app.models import Save
    post = Post.query.get_or_404(post_id)
    existing_save = Save.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if existing_save:
        db.session.delete(existing_save)
        db.session.commit()
        saved = False
    else:
        new_save = Save(user_id=current_user.id, post_id=post.id)
        db.session.add(new_save)
        db.session.commit()
        saved = True
    return jsonify({'saved': saved})


@posts_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        c = Comment(body=form.body.data, author=current_user, post=post)
        db.session.add(c)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'comment': {
                    'body': c.body,
                    'username': current_user.username,
                    'avatar': current_user.avatar,
                    'created_at': c.created_at.strftime('%d.%m.%Y %H:%M')
                }
            })
        flash('Izoh qo\'shildi!', 'success')
    return redirect(url_for('posts.detail', post_id=post.id))


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash("Bu postni o'chirish huquqingiz yo'q.", 'danger')
        return redirect(url_for('main.feed'))
    # Delete image file
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], post.image)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(post)
    db.session.commit()
    flash("Post o'chirildi.", 'success')
    return redirect(url_for('main.feed'))

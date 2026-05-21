from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Post, User, SupportRequest, AgroRecord
from app.forms import SearchForm, SupportForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/feed')
@login_required
def feed():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template('main/feed.html', posts=posts)


@main_bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=24, error_out=False
    )
    return render_template('main/explore.html', posts=posts)


@main_bp.route('/search')
@login_required
def search():
    q = request.args.get('q', '', type=str)
    users = []
    if q:
        users = User.query.filter(
            (User.username.ilike(f'%{q}%')) | (User.full_name.ilike(f'%{q}%'))
        ).limit(20).all()
    return render_template('main/search.html', users=users, query=q)


@main_bp.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    form = SupportForm()
    if form.validate_on_submit():
        request_obj = SupportRequest(
            subject=form.subject.data,
            message=form.message.data,
            user_id=current_user.id
        )
        db.session.add(request_obj)
        db.session.commit()
        flash('Xabaringiz yuborildi. Adminlarimiz tez orada javob berishadi.', 'success')
        return redirect(url_for('main.feed'))
    return render_template('main/contact.html', title='Bog\'lanish', form=form)


@main_bp.route('/agro-admin')
@login_required
def agro_admin():
    if not getattr(current_user, 'is_admin', False):
        flash('Sizda ushbu sahifaga kirish huquqi yo\'q.', 'danger')
        return redirect(url_for('main.feed'))
    
    total_harvest = db.session.query(func.sum(AgroRecord.harvested_qty)).scalar() or 0.0
    active_crops = AgroRecord.query.filter_by(is_harvested=False).count()
    records = AgroRecord.query.order_by(AgroRecord.created_at.desc()).limit(50).all()
    users_list = User.query.limit(10).all()
    
    return render_template('main/agro_admin.html', 
                          total_harvest=total_harvest, 
                          active_crops=active_crops, 
                          records=records,
                          users_list=users_list)


@main_bp.route('/update-subscription/<int:user_id>', methods=['POST'])
@login_required
def update_subscription(user_id):
    if not getattr(current_user, 'is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    sub_type = request.form.get('sub_type')
    user.subscription_type = sub_type # Assuming this field exists or adding it via migration if needed
    db.session.commit()
    flash(f'{user.username} obunasi {sub_type} ga o\'zgartirildi.', 'success')
    return redirect(url_for('main.agro_admin'))

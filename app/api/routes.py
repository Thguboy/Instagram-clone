from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import User, Post
from app.schemas import user_schema, users_schema, post_schema, posts_schema

api_bp = Blueprint('api', __name__)


@api_bp.route('/users/<username>')
@login_required
def get_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return jsonify(user_schema.dump(user))


@api_bp.route('/users/<username>/posts')
@login_required
def get_user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.created_at.desc()).all()
    return jsonify(posts_schema.dump(posts))


@api_bp.route('/feed')
@login_required
def get_feed():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=12, error_out=False
    )
    return jsonify({
        'posts': posts_schema.dump(posts.items),
        'has_next': posts.has_next,
        'page': page
    })


@api_bp.route('/explore')
@login_required
def get_explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=24, error_out=False
    )
    return jsonify({
        'posts': posts_schema.dump(posts.items),
        'has_next': posts.has_next,
        'page': page
    })


@api_bp.route('/search')
@login_required
def search_users():
    q = request.args.get('q', '', type=str)
    if not q:
        return jsonify([])
    users = User.query.filter(
        (User.username.ilike(f'%{q}%')) | (User.full_name.ilike(f'%{q}%'))
    ).limit(10).all()
    return jsonify(users_schema.dump(users))


@api_bp.route('/agro/plantings', methods=['POST'])
def sync_agro_planting():
    data = request.get_json()
    from app.models import AgroRecord
    from app import db
    
    record = AgroRecord(
        crop_name=data.get('crop_name'),
        planted_qty=data.get('planted_qty'),
        is_harvested=data.get('is_harvested', False),
        harvested_qty=data.get('harvested_qty', 0.0),
        user_id=None # Mocking user for now
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'id': record.id}), 201


@api_bp.route('/agro/stats')
def get_agro_stats():
    from app.models import AgroRecord
    from sqlalchemy import func
    
    total_harvest = db.session.query(func.sum(AgroRecord.harvested_qty)).scalar() or 0.0
    active_crops = AgroRecord.query.filter_by(is_harvested=False).count()
    
    return jsonify({
        'total_harvest_kg': total_harvest,
        'active_crop_count': active_crops,
        'total_farmers': 1 # Mock
    })

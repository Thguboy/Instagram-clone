from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# Follow association table
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(128), default='')
    bio = db.Column(db.String(500), default='')
    avatar = db.Column(db.String(256), default='default_avatar.png')
    website = db.Column(db.String(256), default='')
    is_private = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    saved_posts = db.relationship('Save', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    # Follow relationship
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers_list', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    @property
    def followers_count(self):
        return self.followers_list.count()

    @property
    def following_count(self):
        return self.followed.count()

    @property
    def posts_count(self):
        return self.posts.count()

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.created_at.desc())

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=False)
    caption = db.Column(db.String(2200), default='')
    location = db.Column(db.String(128), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    base_likes = db.Column(db.Integer, default=0)

    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    saves = db.relationship('Save', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def likes_count(self):
        return self.likes.count() + (self.base_likes or 0)

    @property
    def saves_count(self):
        return self.saves.count()

    def is_liked_by(self, user):
        if user.is_anonymous:
            return False
        return self.likes.filter_by(user_id=user.id).count() > 0

    def is_saved_by(self, user):
        if user.is_anonymous:
            return False
        return self.saves.filter_by(user_id=user.id).count() > 0

    def __repr__(self):
        return f'<Post {self.id}>'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)

    def __repr__(self):
        return f'<Like {self.id}>'


class Save(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)

    def __repr__(self):
        return f'<Save {self.id}>'


class SupportRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Ochiq')  # Ochiq, Ko'rilmoqda, Hal etildi
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('support_requests', lazy='dynamic'))

    def __repr__(self):
        return f'<SupportRequest {self.id} - {self.subject}>'


class AgroRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(64), nullable=False)
    planted_qty = db.Column(db.Float, default=0.0)
    is_harvested = db.Column(db.Boolean, default=False)
    harvested_qty = db.Column(db.Float, default=0.0)
    harvest_photo_path = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Allow null for demo simplicity

    def __repr__(self):
        return f'<AgroRecord {self.id} - {self.crop_name}>'

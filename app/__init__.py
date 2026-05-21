from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_wtf.csrf import CSRFProtect
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
ma = Marshmallow()
csrf = CSRFProtect()


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        flash('Sizda ushbu sahibaga kirish huquqi yo\'q.', 'danger')
        return redirect(url_for('auth.login'))


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        flash('Sizda ushbu sahifaga kirish huquqi yo\'q.', 'danger')
        return redirect(url_for('auth.login'))


class PostModelView(MyModelView):
    column_editable_list = ['caption', 'location', 'base_likes']
    column_searchable_list = ['caption', 'location']
    column_filters = ['created_at', 'user_id', 'base_likes']
    
    @action('boost_likes', 'Layklarni ko\'paytirish (Boost)', 'Siz tanlangan postlar layklarini ko\'paytirmoqchimisiz?')
    def action_boost_likes(self, ids):
        try:
            from app.models import Post
            query = Post.query.filter(Post.id.in_(ids))
            count = 0
            for post in query.all():
                post.base_likes = (post.base_likes or 0) + 100
                count += 1
            db.session.commit()
            flash(f'{count} ta postga 100 tadan layk qo\'shildi.', 'success')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(f'Xato yuz berdi: {str(ex)}', 'error')


admin = Admin(name='Insta Admin', template_mode='bootstrap4', index_view=MyAdminIndexView(), base_template='admin/my_base.html')


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    ma.init_app(app)
    csrf.init_app(app)
    admin.init_app(app)

    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register admin views
    from app.models import User, Post, Comment, Like, Save, SupportRequest
    admin.add_view(MyModelView(User, db.session, name='Foydalanuvchilar'))
    admin.add_view(PostModelView(Post, db.session, name='Postlar'))
    admin.add_view(MyModelView(Comment, db.session, name='Izohlar'))
    admin.add_view(MyModelView(Like, db.session, name='Yoqtirishlar'))
    admin.add_view(MyModelView(Save, db.session, name='Saqlanganlar'))
    admin.add_view(MyModelView(SupportRequest, db.session, name='Murojaatlar'))

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.posts.routes import posts_bp
    from app.users.routes import users_bp
    from app.api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp, url_prefix='/posts')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(api_bp, url_prefix='/api')

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Iltimos, avval tizimga kiring.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Create tables
    with app.app_context():
        db.create_all()

    return app

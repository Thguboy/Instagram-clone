from app import ma
from app.models import User, Post, Comment, Like


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password_hash',)
        load_instance = True

    followers_count = ma.Function(lambda obj: obj.followers_count)
    following_count = ma.Function(lambda obj: obj.following_count)
    posts_count = ma.Function(lambda obj: obj.posts_count)


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        include_fk = True
        load_instance = True

    author = ma.Nested(UserSchema, only=('id', 'username', 'avatar', 'full_name'))
    likes_count = ma.Function(lambda obj: obj.likes_count)


class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        include_fk = True
        load_instance = True

    author = ma.Nested(UserSchema, only=('id', 'username', 'avatar'))


class LikeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Like
        include_fk = True
        load_instance = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

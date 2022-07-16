from fileinput import filename
from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from webargs import fields
from webargs.flaskparser import use_kwargs
import os

from main.models.recipe import Recipe
from main.utils import save_image, clear_cache
from main.models.user import User
from main.schemas.user_schema import UserSchema
from main.schemas.recipe_schema import RecipePaginationSchema
from main.extensions import image_set, limiter

user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email',))
user_avatar_schema = UserSchema(only=('avatar_url',))
recipe_pagination_chema = RecipePaginationSchema()

class UserListResource(Resource):
    
    # Validate and create new user
    def post(self):
        json_data = request.get_json()
        try:
            data = user_schema.load(data=json_data)
        except ValidationError as err:
            return {'message':'Validation errors', 'errors': err}, HTTPStatus.BAD_REQUEST            
        
        if User.get_by_username(data.get('username')):
            return {'message': 'username already used'}, HTTPStatus.BAD_REQUEST
        if User.get_by_email(data.get('email')):
            return {'message':'email already used'}, HTTPStatus.BAD_REQUEST
        
        user = User(**data)
        user.save()
        
        return user_schema.dump(user), HTTPStatus.CREATED
    
    
class UserResource(Resource):
    
    # Get user by username, if authorized displaying email
    @jwt_required(optional=True)
    def get(self, username):
        user = User.get_by_username(username=username)
        
        if user is None:
            return {'message':'user not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        if current_user == user.id:
            data = user_schema.dump(user)
        else:
            data = user_public_schema.dump(user)
        return data, HTTPStatus.OK
    
    
class MeResource(Resource):
    
    # get info of authorized user(logging)
    @jwt_required()
    def get(self):
        user = User.get_by_id(id=get_jwt_identity())
        return user_schema.dump(user), HTTPStatus.OK


class UserRecipeListResource(Resource):
    
    decorators = [limiter.limit('3/minute;30/hour;300/day', methods=['GET'], error_message='Too Many Requests')]
    # Get user by username
    # visibility = 'public': get all published recipes from this user(no need to log in)
    # visibility = 'private': get all unpublished recipes from this user(need to log in)
    # visibility = 'all': get all published and unpublished recipes from this user(need to log in)
    @jwt_required(optional=True)
    @use_kwargs({'page': fields.Int(missing=1),
                 'per_page': fields.Int(missing=20),
                 'visibility': fields.Str(missing='public')}, location="query")
    def get(self, username, visibility, page, per_page):
        user = User.get_by_username(username=username)
        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        if current_user == user.id and visibility in ['all', 'private']:
            pass
        else:
            visibility = 'public'
        recipes = Recipe.get_all_by_user(user_id=user.id, page=page, per_page=per_page, visibility=visibility)
        return recipe_pagination_chema.dump(recipes), HTTPStatus.OK
    

class UserAvatarUploadResource(Resource):
    
    # upload avatar image for authorized user
    # if avatar image existed, replace with the new one
    @jwt_required()
    def put(self):
        file = request.files.get('avatar')
        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        
        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST
        
        user = User.get_by_id(id=get_jwt_identity())
        if user.avatar_image:
            avatar_path = image_set.path(folder='avatars', filename=user.avatar_image)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
        filename = save_image(image=file, folder='avatars')
        user.avatar_image = filename
        user.save()
        clear_cache('/recipes')
        return user_avatar_schema.dump(user), HTTPStatus.OK
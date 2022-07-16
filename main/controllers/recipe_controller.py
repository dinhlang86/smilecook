from pickle import GET
from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError, missing
import os
from webargs import fields
from webargs.flaskparser import use_kwargs

from main.models.recipe import Recipe
from main.schemas.recipe_schema import RecipeSchema, RecipePaginationSchema
from main.utils import save_image, clear_cache
from main.extensions import image_set, cache, limiter


recipe_schema = RecipeSchema()
recipe_cover_schema = RecipeSchema(only=('cover_url',))
recipe_pagination_schema = RecipePaginationSchema()


class RecipeListResource(Resource):
    
    decorators = [limiter.limit('2 per minute', methods=['GET'], error_message='Too Many Requests')]
    # Get all published recipes
    # query_string=True: allow passing in of arguments
    @use_kwargs({'page': fields.Int(missing=1),
                 'per_page': fields.Int(missing=20),
                 'q': fields.Str(missing=''),
                 'sort': fields.Str(missing='created_at'),
                 'order': fields.Str(missing='desc')}, location='query')
    @cache.cached(timeout=60, query_string=True)
    def get(self, q, page, per_page, sort, order):
        # Testing
        # print('Querying database...')
        # Accept sort by 'created_at', 'cook_time' and 'num_of_servings', default 'created_at'
        if sort not in ['created_at', 'cook_time', 'num_of_servings']:
            sort = 'created_at'
        # Accept order by asc or desc, default desc
        if order not in ['asc', 'desc']:
            order = 'desc'
        paginated_recipes = Recipe.get_all_published(q=q, page=page, per_page=per_page, sort=sort, order=order)
        return recipe_pagination_schema.dump(paginated_recipes), HTTPStatus.OK
    
    # Validate and create new recipe with authorized user
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()
        try:
            data= recipe_schema.load(data=json_data)
        except ValidationError as err:
            return {'message': 'Validation errors', 'errors': err}, HTTPStatus.BAD_REQUEST    
        
        recipe = Recipe(**data)
        recipe.user_id = current_user
        recipe.save()
        clear_cache('/recipes')
        return recipe_schema.dump(recipe), HTTPStatus.CREATED   
    
    
class RecipeResource(Resource):
    
    # Get specific recipe from authorized user
    @jwt_required(optional=True)
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message':'recipe not found'}, HTTPStatus.NOT_FOUND
        
        if not recipe.is_published:
            current_user = get_jwt_identity()
            if recipe.user_id != current_user:
                return {'message':'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        return recipe_schema.dump(recipe), HTTPStatus.OK
    
    # Update specific recipe from authorized user
    @jwt_required()
    def put(self, recipe_id):
        json_data = request.get_json()
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message':'recipe not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message':'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        try:
            data = recipe_schema.load(data=json_data)
        except ValidationError as err:
            return {'message': 'Validation errors', 'errors': err}, HTTPStatus.BAD_REQUEST   
        
        recipe.name = data['name']
        recipe.description = data['description']
        recipe.num_of_servings = data['num_of_servings']
        recipe.cook_time = data['cook_time']
        recipe.directions = data['directions']
        recipe.update()
        clear_cache('/recipes')
        return recipe_schema.dump(recipe), HTTPStatus.OK
    
    #Update some attributes for recipe
    @jwt_required()
    def patch(self, recipe_id):
        json_data = request.get_json()
        #'name' is a required attribute, using partial to specify that 'name' attribute is optional
        try:
            data = recipe_schema.load(data=json_data, partial=('name',))
        except ValidationError as err:
            return {'message': 'Validation errors', 'errors': err}, HTTPStatus.BAD_REQUEST   
        
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.directions = data.get('directions') or recipe.directions
        recipe.ingredients = data.get('ingredients') or recipe.ingredients
        recipe.save()
        clear_cache('/recipes')
        return recipe_schema.dump(recipe), HTTPStatus.OK
    
    # Delete recipe from authorized user
    @jwt_required()
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message':'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if (current_user != recipe.user_id):
            return {'message':'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.delete()
        clear_cache('/recipes')
        return {}, HTTPStatus.NO_CONTENT
    

class RecipePublishResource(Resource):
    
    # Update specific recipe to be published from authorized user
    @jwt_required()
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if not recipe:
            return {'message':'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if (current_user != recipe.user_id):
            return {'message':'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.is_published = True
        recipe.update()
        clear_cache('/recipes')
        return {}, HTTPStatus.NO_CONTENT
    
    # Update specific recipe to be unpublished from authorized user
    @jwt_required()
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if not recipe:
            return {'message':'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if (current_user != recipe.user_id):
            return {'message':'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.is_published = False
        recipe.update()
        clear_cache('/recipes')
        return {}, HTTPStatus.NO_CONTENT
        
        
class RecipeCoverUploadResource(Resource):
    
    # upload cover image for specific recipe from authorized user
    @jwt_required()
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        file = request.files.get('cover')
        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        
        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST
        
        if recipe.cover_image:
            cover_path = image_set.path(folder='covers', filename=recipe.cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)
        filename = save_image(image=file, folder='covers')
        recipe.cover_image = filename
        recipe.save()
        clear_cache('/recipes')
        return recipe_cover_schema.dump(recipe), HTTPStatus.OK
        
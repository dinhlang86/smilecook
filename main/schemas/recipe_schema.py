from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from flask import url_for

from main.schemas.user_schema import UserSchema
from main.schemas.pagination_schema import PaginationSchema


def validate_num_of_servings(n):
        if n < 1:
            raise ValidationError('Number of servings must be greater than 0')
        if n > 50:
            raise ValidationError('Number of servings must be less than 50')
        
class RecipeSchema(Schema):
    
    class Meta:
        ordered = True
        
    id = fields.Int(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(validate=[validate.Length(max=200)])
    directions = fields.String(validate=[validate.Length(max=1000)])
    ingredients = fields.String(validate=[validate.Length(max=1000)])
    num_of_servings = fields.Int(validate=validate_num_of_servings)
    cook_time = fields.Integer()
    cover_url = fields.Method(serialize='dump_cover_url')
    is_published = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('cook_time')
    def validate_cook_time(self, n):
        if n < 1:
            raise ValidationError('Cook time must be greater than 0')
        if n > 300:
            raise ValidationError('Cook time must be less than 300')
    
    # Display the author infomation related to the recipe
    ## This attribute is named 'author' in json response, but the original name is 'user'
    author = fields.Nested(UserSchema, attribute='user', dump_only=True, exclude=('email',))
    
    def dump_cover_url(self, recipe):
        if recipe.cover_image:
            return url_for('static', filename='images/covers/{}'.format(recipe.cover_image), _external=True)
        else:
            return url_for('static', filename='images/assets/default-cover.jpeg', _external=True)
        
        
class RecipePaginationSchema(PaginationSchema):
    data = fields.Nested(RecipeSchema, attribute='items', many=True)
    
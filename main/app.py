
from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from flask_uploads import configure_uploads

from main.config import Config
from main.extensions import db, jwt, image_set
from main.controllers.user_controller import (UserListResource, UserResource, MeResource, 
                                              UserRecipeListResource, UserAvatarUploadResource)
from main.controllers.recipe_controller import (RecipeListResource, RecipeResource, 
                                                RecipePublishResource, RecipeCoverUploadResource)
from main.controllers.token import TokenResource, RefreshTokenResource, RevokeResource, black_list

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    register_extensions(app)
    register_resources(app)
    config_images(app)
    return app
    
def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload: dict):
        jti = jwt_payload['jti']
        return jti in black_list

def config_images(app):
    configure_uploads(app, image_set)
    
def register_resources(app):
    api = Api(app)
    api.add_resource(RecipeListResource, '/recipes')
    api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish')
    api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
    api.add_resource(UserListResource, '/users')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(TokenResource, '/token')
    api.add_resource(MeResource, '/me')
    api.add_resource(RefreshTokenResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')
    api.add_resource(UserRecipeListResource, '/users/<string:username>/recipes')
    api.add_resource(UserAvatarUploadResource, '/users/avatar')
    api.add_resource(RecipeCoverUploadResource, '/recipes/<int:recipe_id>/cover')

if __name__ == '__main__':
    app = create_app()
    app.run()

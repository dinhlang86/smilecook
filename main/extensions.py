from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_uploads import UploadSet, IMAGES
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import func

db = SQLAlchemy()
jwt = JWTManager()
image_set = UploadSet('images', IMAGES)
cache = Cache()
# Return the IP address for current request to limit the rate per IP address
limiter = Limiter(key_func=get_remote_address)

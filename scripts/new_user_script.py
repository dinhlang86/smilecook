from main.models.user import User
from main.models.recipe import Recipe
from main.extensions import db
user = User(username='jack', email='jack@gmail.com', password='WkQa')
db.session.add(user)
db.session.commit()

user = User(username='Peter', email='peter@gmail.com', password='Peter123')
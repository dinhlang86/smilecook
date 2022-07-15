from main.models.user import User
from main.models.recipe import Recipe
from main.extensions import db
user = db.session.query(User).filter(User.email == 'peter@gmail.com').first()
pizza = Recipe(name='Cheese Pizza', description='This is a lovely cheese pizza recipe', num_of_servings=2, cook_time=30, 
               directions='This is how you make it', user_id= user.id)
db.session.add(pizza)
# user.recipes.append(pizza)
# pizza.user = user
db.session.commit()

pasta = Recipe(name='Tomato Pasta', description='This is a lovely tomato pasta recipe', num_of_servings=3, cook_time=20, 
               directions='This is how you make it', user_id=user.id)
db.session.add(pasta)
db.session.commit()

hamburger = Recipe(name='Beef Hamburger', description='This is a lovely beef hamburger recipe', num_of_servings=1, cook_time=10, 
               directions='This is how you make it', user_id=user.id)
db.session.add(hamburger)
db.session.commit()

sushi = Recipe(name='Vegie Sushi', description='This is a lovely vegie sushi recipe', num_of_servings=5, cook_time=35, 
               directions='This is how you make it', user_id=user.id)
db.session.add(sushi)
db.session.commit()
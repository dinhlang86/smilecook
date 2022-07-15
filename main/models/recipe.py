from sqlalchemy import desc


from  main.extensions import db

class Recipe(db.Model):
    
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    num_of_servings = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    directions = db.Column(db.String(1000))
    is_published = db.Column(db.Boolean(), default=False)
    cover_image = db.Column(db.String(100), default=None)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='recipes')
    
    @classmethod
    def get_all_published(cls, page, per_page):
        return cls.query.filter_by(is_published=True).order_by(desc(cls.created_at)).paginate(page=page, per_page=per_page)
    
    @classmethod
    def get_by_id(cls, recipe_id):
        return cls.query.filter_by(id=recipe_id).first()
    
    @classmethod
    def get_all_by_user(cls, user_id, visibility='public'):
        if visibility == 'public':
            return cls.query.filter_by(user_id=user_id, is_published=True).all()
        if visibility == 'private':
            return cls.query.filter_by(user_id=user_id, is_published=False).all()
        else:
            return cls.query.filter_by(user_id=user_id).all()
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
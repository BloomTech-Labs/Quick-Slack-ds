from quickslack.extensions import db


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    
    username = db.Column(db.String(24), unique=True, nullable=False)
    password = db.Column(db.String(24), nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}')"

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)
        pass

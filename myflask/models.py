from myflask import db

class Users(db.Model):
    id = id = db.Column(db.Integer,primary_key=True)
    user = db.Column(db.String(100),default='',unique=True,nullable=False)
    passwd = db.Column(db.String(60),nullable=False)
    handles = db.Column(db.String(1000),default='')

    def __repr__(self):
        return self.user

class Account(db.Model):
    email = db.Column(db.String(60),nullable=False,primary_key=True)
    passwd = db.Column(db.String(60), nullable=False)

from myflask import db

class Nice(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    url = db.Column(db.String(100), default='')
    text = db.Column(db.String(100), default='')

    def __repr__(self):
        return self.url

class Users(db.Model):
    id = id = db.Column(db.Integer,primary_key=True)
    user = db.Column(db.String(100),default='',unique=True,nullable=False)
    passwd = db.Column(db.String(50),nullable=False)
    handles = db.Column(db.String(1000),nullable=False,default='')

    def __repr__(self):
        return self.user

from myflask import db

class Nice(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    url = db.Column(db.String(100), default='')
    text = db.Column(db.String(100), default='')

    def __repr__(self):
        return self.url

class Twitter(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    handle_name = db.Column(db.String(100), default='',unique=True,nullable=False)

    def __repr__(self):
        return self.handle_name

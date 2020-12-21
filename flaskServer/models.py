# 建表写在models.py文件里面
from flaskdir.exts import db

class User(db.Model):
    id = db.Column(db.Integer)
    connect_way = db.Column(db.String(100))
    object_id = db.Column(db.Integer, db.ForeignKey('object.id'), primary_key=True, )
    borrowed_time = db.Column(db.Integer, primary_key=True)
    __tablename__ = 'user'

    def __init__(self,id,connect_way,object_id,borrowed_time):
        self.id = id
        self.connect_way = connect_way
        self.object_id = object_id
        self.borrowed_time = borrowed_time
        pass

class UnusedObject(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(100))
    now_user = db.Column(db.String(500))
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id'))
    quantity = db.Column(db.Integer)
    __tablename__ = 'object'

    def __init__(self,description,now_user,manager_id,quantity):
        self.description = description
        self.now_user = now_user
        self.manager_id = manager_id
        self.quantity = quantity
        pass

class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    connect_way = db.Column(db.String(100))
    __tablename__ = 'manager'

    def __init__(self,id,connect_way):
        self.id = id
        self.connect_way = connect_way
        pass

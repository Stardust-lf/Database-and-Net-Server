from flask import Flask,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from models import User,UnusedObject,Manager
import json

app = Flask(__name__,static_folder='./static')  # 创建一个Flask app对象
# 数据库链接的配置，此项必须，格式为（数据库+驱动://用户名:密码@数据库主机地址:端口/数据库名称）
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:20010110@localhost:3306/roomcontroller'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 跟踪对象的修改，在本例中用不到调高运行效率，所以设置为False
db = SQLAlchemy(app=app)  # 为哪个Flask app对象创建SQLAlchemy对象，赋值为db
#manager = Manager(app=app)  # 初始化manager模块

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/appNote')
def app_Note():
    return '''更新公告:,  ver1.6.8:, 1.修复了切换皮肤时底边栏图标仍显示原图标的bug, 2.添加了自定义闹钟响铃界面的功能, 3.由于画风不同删除了‘星空’系列皮肤(制作人员对此表示非常遗憾), 4.对四季系列皮肤进行了优化 现在它们看起来非常coooooool， 5.新版下载网址为http://119.45.36.212/download/app-debug.apk'''

@app.route('/sayHello')
def say_hello():
    return 'HHHHHHH!'

@app.route('/selectAllObject')
def select_AllObject():
    li = db.session.execute("select description,quantity from object").fetchall()
    if li==None :
        return "No such object"
    li2 = list()
    for x in li:
        dire = {"description":x[0],"quantity":x[1]}
        li2.append(dire)
        pass
    jsonArr = json.dumps(li2, ensure_ascii=False)
    return jsonArr

@app.route('/insert/User/<int:id>/<connect_way>/<int:object_id>/<int:borrowed_time>')
def insertUser(id,connect_way,object_id,borrowed_time):
    from models import db
    user = User(id,connect_way,object_id,borrowed_time)
    db.session.add(user)
    db.session.commit()
    return 'Insert user access'
@app.route('/insert/Object/<description>/<now_user>/<int:manager_id>/<int:quantity>')
def insertObject(description,now_user,manager_id,quantity):
    from models import db
    unuserObject = UnusedObject(description,now_user,manager_id,quantity)
    db.session.add(unuserObject)
    db.session.commit()
    return 'Insert object access'
@app.route('/insert/Manager/<int:id>/<conn_way>')
def insertManager(id,conn_way):
    from models import db
    manager = Manager(id,conn_way)
    db.session.add(manager)
    db.session.commit()
    return 'Insert manager access'
@app.route('/select/User/<int:object_id>/<int:borrowed_time>')
def selectUser(object_id,borrowed_time):
    user = User.query.get((object_id,borrowed_time))
    return {"id":user.id,"connect_way":user.connect_way,"object_id":user.object_id,"borrowed_time":user.borrowed_time}
@app.route('/select/Object/<int:id>')
def selectObject(id):
    unusedObject = UnusedObject.query.get(id)
    return {"id":unusedObject.id,"description":unusedObject.description,"now_user":unusedObject.now_user,"manager_id":unusedObject.manager_id,"quantity":unusedObject.quantity}
@app.route('/select/Object/Bydescription/<description>')
def selectObjectFromDescription(description):
    result = UnusedObject.query.filter(
        UnusedObject.description.like("%" + description + "%")
    ).all()
    li = list()
    for myObject in result:
        li.append({"code":myObject.id,"text":myObject.description,"type":myObject.quantity})
        pass

    if not len(li):
        return "no such object"
    jsonArr = json.dumps(li, ensure_ascii=False)
    return jsonArr
@app.route('/select/Manager/<int:id>')
def selectManager(id):
    manager = Manager.query.get(id)
    return {"id":manager.id,"connect_way":manager.connect_way}
@app.route('/delete/User/<int:object_id>/<int:borrowed_time>')
def deleteUser(object_id,borrowed_time):
    from models import db
    user = User.query.get((object_id,borrowed_time))
    db.session.delete(user)
    db.session.commit()
    return "delete succeed"
@app.route('/delete/Object/<int:id>')
def deleteObject(id):
    from models import db
    unusedObject = UnusedObject.query.get(id)
    db.session.delete(unusedObject)
    db.session.commit()
    return "delete succeed"

@app.route('/decreaseObject/<int:id>')
def decreaseObject(id):
    from models import db
    unusedObject = UnusedObject.query.get(id)
    if unusedObject.quantity:
        unusedObject.quantity -= 1
        num = unusedObject.quantity
        db.session.commit()
        return str(num)
    return '0'

@app.route('/increaseObject/<int:id>')
def increaseObject(id):
    from models import db
    unusedObject = UnusedObject.query.get(id)
    unusedObject.quantity += 1
    num = unusedObject.quantity
    db.session.commit()
    return str(num)

@app.route('/delete/Manager/<int:id>')
def deleteManager(id):
    from models import db
    manager = Manager.query.get(id)
    db.session.delete(manager)
    db.session.commit()
    return "delete succeed"

@app.route('/update/User/<int:object_id>/<int:borrowed_time>/<connect_way>')
def updateUserConnectWay(id,connect_way):
    from models import db
    user = User.query.get(id)
    user.connect_way = connect_way
    db.session.commit()
    return "update succeed"
@app.route('/update/Object/<int:object_id>/<description>')
def updateObjectDescription(id,description):
    from models import db
    unusedObject = UnusedObject.query.get(id)
    unusedObject.connect_way = description
    db.session.commit()
    return "update succeed"
@app.route('/update/Manager/<int:object_id>/<connect_way>')
def updateManagerConnectWay(id,connect_way):
    from models import db
    manager = Manager.query.get(id)
    manager.connect_way = connect_way
    db.session.commit()
    return "update succeed"
@app.route('/download/<filepath>', methods=['GET'])
def download2(filepath):
    print("filepath:",filepath)
    target_path = ""
    return send_from_directory(target_path,filepath,as_attachment=True)



if __name__ == '__main__':
   app.run()  # 运行服务器

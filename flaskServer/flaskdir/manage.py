from flask_script import Manager, Server
from app import app
from flask_migrate import Migrate, MigrateCommand
from flaskdir.exts import db
from first import models # 模型文件必须导入进来，否则运行报错

manager = Manager(app)
Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand) # 创建数据库映射命令
manager.add_command('start', Server(port=8000, use_debugger=True)) # 创建启动命令

if __name__ == '__main__':
    manager.run()
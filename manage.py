import unittest
import coverage
from flask_script import Manager
from project import create_app, db
from project.api.models import User

app = create_app()
manager = Manager(app)

COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/test/*'
    ]
)
COV.start()


@manager.command
def cov():
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print("Coverage Summary")
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


@manager.command
def recreate_db():
    """重新创建数据表 """
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def test():
    """ 运行测试"""
    tests = unittest.TestLoader().discover('project/tests', pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def seed_db():
    """ Seeds to database """
    db.session.add(User(username="test12", email='123456222@qq.com'))
    db.session.add(User(username="test22", email='1234567222@qq.com'))
    db.session.commit()


if __name__ == '__main__':
    manager.run()

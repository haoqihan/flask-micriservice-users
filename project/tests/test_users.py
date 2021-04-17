import json
from project.tests.base import BaseTestCase
from project.api.models import User
from project import db


class TestUserService(BaseTestCase):
    def test_users(self):
        """ 确保ping服务的正常"""
        response = self.client.get("/ping")
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """ 确保能够正确的添加一个用户的用户数据添加到数据库 """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(
                    dict(username='test', email="12345678@qq.com")
                ),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn("12345678@qq.com was added", data['message'])
            self.assertEqual("success", data['status'])

    def test_add_invalid_json(self):
        """ 如果JSON对象为空，确保抛出一个错误"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict()),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload", data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_invalid_json_key(self):
        """ 如果JSON对象中没有username或email，确保抛出一个错误"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(email="12345678@qq.com")),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload", data['message'])
            self.assertEqual('fail', data['status'])
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(username='test')),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload", data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_duplicate_user(self):
        """ 如果邮件已存在确保抛出一个错误"""

        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(
                    dict(username='test', email="12345678@qq.com")
                ),
                content_type="application/json"
            )
            response = self.client.post(
                '/users',
                data=json.dumps(
                    dict(username='test', email="12345678@qq.com")
                ),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Sorry, That email already exists.", data['message'])
            self.assertEqual("fail", data['status'])

    def test_get_user(self):
        """ 根据用户id获取用户信息"""
        user = User(username='test', email='123456@qq.com')
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get('/users/%d' % user.id)
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertEqual('test', data['data']['username'])
            self.assertEqual('123456@qq.com', data['data']['email'])
            self.assertEqual('success', data['status'])

    def test_get_user_no_id(self):
        """ 如果没有id的时候抛出异常"""
        with self.client:
            response = self.client.get('/users/xxx')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Param id error", data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_user_incorrect_id(self):
        """ 如果ID不存在的话抛出异常"""
        with self.client:
            response = self.client.get('/users/-1')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertEqual('fail', data['status'])

    def test_main_no_users(self):
        """ 没有用户 """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No users", response.data)

    def test_main_with_users(self):
        """ 有多个用户的场景"""
        db.session.add(User(username='tttt', email='11111@qq.com'))
        db.session.add(User(username='test1', email='111112@qq.com'))
        db.session.commit()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertNotIn(b'No users', response.data)
        self.assertIn(b'tttt', response.data)
        self.assertIn(b'test1', response.data)

    def test_main_add_user(self):
        """ 前端页面添加一个新用户"""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='test2', email='1111@qq.com'),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'No users', response.data)
            self.assertIn(b'test2', response.data)

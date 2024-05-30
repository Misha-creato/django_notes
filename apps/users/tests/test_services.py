import json
import os

from django.test import TestCase

from unittest.mock import patch

from users.models import CustomUser
from users.services import (
    register_user,
    login_user,
    confirm_email,
    change_password,
    password_reset_request,
    password_reset,
    get_user_by_hash,
)


CUR_DIR = os.path.dirname(__file__)


class ServicesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/services'
        cls.user = CustomUser.objects.create_user(
            email='example@example.com',
            password='password123',
            url_hash='fc0ecf9c-4c37-4bb2-8c22-938a1dc65da4',
        )

    @patch('users.services.send_confirmation_email')
    def test_register_user(self, mock_send_confirmation_email):
        path = f'{self.path}/register_user'
        fixtures = (
            (200, 'valid'),
            (400, 'exists_email'),
            (400, 'invalid_email'),
            (400, 'invalid_password'),
            (400, 'invalid'),
            (400, 'password_mismatch'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            response = self.client.post(
                '/',
                data=data,
            )

            request = response.wsgi_request

            status_code = register_user(
                request=request,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_login_user(self):
        path = f'{self.path}/login_user'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid_email'),
            (400, 'invalid'),
            (401, 'authentication_error'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            response = self.client.post(
                '/',
                data=data,
            )

            request = response.wsgi_request

            status_code = login_user(
                request=request,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_confirm_email(self):
        path = f'{self.path}/confirm_email'
        fixtures = (
            (200, 'valid'),
            (404, 'not_found'),
        )

        response = self.client.post(
            '/',
        )
        request = response.wsgi_request

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                url_hash = json.load(file)

            status_code = confirm_email(
                request=request,
                url_hash=url_hash,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_change_password(self):
        path = f'{self.path}/change_password'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid'),
            (400, 'invalid_old_password'),
            (400, 'password_mismatch'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            user = CustomUser.objects.first()

            self.client.force_login(
                user,
            )
            response = self.client.post(
                '/',
                data=data,
            )
            request = response.wsgi_request

            status_code = change_password(
                request=request,
            )

            self.assertEqual(status_code, code, msg=fixture)

    @patch('users.services.send_password_reset_email')
    def test_password_reset_request(self, mock_send_password_reset_email):
        path = f'{self.path}/password_reset_request'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid_email'),
            (400, 'invalid'),
            (404, 'not_found'),
        )

        mock_send_password_reset_email.return_value = 200

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            response = self.client.post(
                '/',
                data=data,
            )
            request = response.wsgi_request

            status_code = password_reset_request(
                request=request,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_password_reset(self):
        path = f'{self.path}/password_reset'
        fixtures = (
            (400, 'invalid'),
            (400, 'password_mismatch'),
            (404, 'not_found'),
            (200, 'valid'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            response = self.client.post(
                '/',
                data=data,
            )
            request = response.wsgi_request

            status_code = password_reset(
                request=request,
                url_hash=data['url_hash']
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_get_user_by_hash(self):
        path = f'{self.path}/get_user_by_hash'
        fixtures = (
            (200, 'valid'),
            (404, 'not_found'),
        )

        response = self.client.post(
            '/',
        )
        request = response.wsgi_request

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                url_hash = json.load(file)

            status_code, user = get_user_by_hash(
                request=request,
                url_hash=url_hash,
            )

            self.assertEqual(status_code, code, msg=fixture)

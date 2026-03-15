from rest_framework.test import APITestCase
from rest_framework import status
from .models import Student


class StudentRegistrationTest(APITestCase):

    def setUp(self):
        self.url = '/api/auth/register/'
        self.valid_data = {
            'name': 'Test Student',
            'email': 'test@example.com',
            'contact_no': '9876543210',
            'address': '123 Test Street, Bangalore',
            'school_college_name': 'Test College',
            'course_selection': 'B.Tech Computer Science',
            'password': 'StrongPass@123',
            'confirm_password': 'StrongPass@123',
            'terms_conditions_accepted': True,
        }

    def test_successful_registration(self):
        res = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', res.data)

    def test_duplicate_email(self):
        self.client.post(self.url, self.valid_data, format='json')
        res = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch(self):
        data = {**self.valid_data, 'confirm_password': 'WrongPassword'}
        res = self.client.post(self.url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_terms_not_accepted(self):
        data = {**self.valid_data, 'terms_conditions_accepted': False}
        res = self.client.post(self.url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_fields(self):
        res = self.client.post(self.url, {'email': 'test@example.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class StudentLoginTest(APITestCase):

    def setUp(self):
        self.url = '/api/auth/login/'
        self.student = Student.objects.create_user(
            email='login@example.com',
            password='StrongPass@123',
            name='Login Student',
            contact_no='9876543210',
            address='Test Address',
            school_college_name='Test College',
            course_selection='B.Tech',
            terms_conditions_accepted=True,
        )

    def test_successful_login(self):
        res = self.client.post(self.url, {
            'email': 'login@example.com',
            'password': 'StrongPass@123',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', res.data)

    def test_wrong_password(self):
        res = self.client.post(self.url, {
            'email': 'login@example.com',
            'password': 'WrongPass',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_email(self):
        res = self.client.post(self.url, {
            'email': 'nobody@example.com',
            'password': 'StrongPass@123',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class StudentProfileTest(APITestCase):

    def setUp(self):
        self.student = Student.objects.create_user(
            email='profile@example.com',
            password='StrongPass@123',
            name='Profile Student',
            contact_no='9876543210',
            address='Test Address',
            school_college_name='Test College',
            course_selection='B.Tech',
            terms_conditions_accepted=True,
        )
        login_res = self.client.post('/api/auth/login/', {
            'email': 'profile@example.com',
            'password': 'StrongPass@123',
        }, format='json')
        self.access_token = login_res.data['tokens']['access']

    def test_profile_with_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['student']['email'], 'profile@example.com')

    def test_profile_without_token(self):
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class StudentLogoutTest(APITestCase):

    def setUp(self):
        self.student = Student.objects.create_user(
            email='logout@example.com',
            password='StrongPass@123',
            name='Logout Student',
            contact_no='9876543210',
            address='Test Address',
            school_college_name='Test College',
            course_selection='B.Tech',
            terms_conditions_accepted=True,
        )
        login_res = self.client.post('/api/auth/login/', {
            'email': 'logout@example.com',
            'password': 'StrongPass@123',
        }, format='json')
        self.access_token  = login_res.data['tokens']['access']
        self.refresh_token = login_res.data['tokens']['refresh']

    def test_successful_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        res = self.client.post('/api/auth/logout/', {'refresh': self.refresh_token}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_logout_without_token(self):
        res = self.client.post('/api/auth/logout/', {'refresh': self.refresh_token}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Movie, Actor
from auth import retrieve_auth_token


def make_orderer():
    order = {}

    def ordered(f):
        order[f.__name__] = len(order)
        return f

    def compare(a, b):
        return [1, -1][order[a] < order[b]]

    return ordered, compare


ordered, compare = make_orderer()
unittest.defaultTestLoader.sortTestMethodsUsing = compare

actorids = []
movieids = []


class AgencyTestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = os.getenv('TEST_DATABASE_NAME', 'agency_test')
        self.database_path = os.getenv('TEST_DATABASE_URL', "postgresql://{}:{}@{}/{}".format(
            'postgres', 'wabtec', 'localhost:5432', self.database_name))
        setup_db(self.app, self.database_path)

        self.new_movies = [
            {
                'title': 'Mr. X',
                'director': 'Steven',
                'year': 2021
            },
            {
                'title': 'Superhero',
                'director': 'Howard',
                'year': 2020
            }
        ]

        self.new_actors = [
            {
                'name': 'Marilyn',
                'gender': 'female',
                'age': 38
            },
            {
                'name': 'Jackman',
                'gender': 'male',
                'age': 39
            }
        ]

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    '''
        Tests for Actors
    '''

    @ordered
    def test_retrieve_actors_director_404(self):
        bearer = retrieve_auth_token(2)
        self.assertTrue(bearer)
        res = self.client().get(
            '/actors', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    @ordered
    def test_retrieve_actors_unauthorized_401(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)

    @ordered
    def test_create_actor_assistant_forbidden_403(self):
        bearer = retrieve_auth_token(1)
        self.assertTrue(bearer)
        res = self.client().post(
            '/actors', json=self.new_actors[0], headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)

    @ordered
    def test_create_actor_director_200(self):
        bearer = retrieve_auth_token(2)
        self.assertTrue(bearer)
        index = 0
        res = self.client().post(
            '/actors', json=self.new_actors[index], headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['name'], self.new_actors[index]['name'])
        self.assertEqual(data['actor']['gender'],
                         self.new_actors[index]['gender'])
        self.assertEqual(data['actor']['age'], self.new_actors[index]['age'])

        actorids.append(data['actor']['id'])
        self.assertEqual(len(actorids), 1)

    @ordered
    def test_retrieve_actors_assistant_200(self):
        bearer = retrieve_auth_token(1)
        self.assertTrue(bearer)
        res = self.client().get(
            '/actors', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertEqual(len(data['actors']), 1)

    @ordered
    def test_create_actor_producer_405(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        res = self.client().post(
            '/actors/11', json=self.new_actors[1], headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not supported')

    @ordered
    def test_create_actor_producer_200(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        index = 1
        res = self.client().post(
            '/actors', json=self.new_actors[index], headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['name'], self.new_actors[index]['name'])
        self.assertEqual(data['actor']['gender'],
                         self.new_actors[index]['gender'])
        self.assertEqual(data['actor']['age'], self.new_actors[index]['age'])

        actorids.append(data['actor']['id'])
        self.assertEqual(len(actorids), 2)

    @ordered
    def test_retrieve_actors_director_200(self):
        bearer = retrieve_auth_token(2)
        self.assertTrue(bearer)
        res = self.client().get(
            '/actors', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertEqual(len(data['actors']), 2)

    @ordered
    def test_update_actor_director_200(self):
        bearer = retrieve_auth_token(2)
        self.assertTrue(bearer)
        body = {'age': 40}
        id = actorids[1]
        res = self.client().patch(
            f'/actors/{id}', json=body, headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['id'], id)
        self.assertEqual(data['actor']['name'], self.new_actors[1]['name'])
        self.assertEqual(data['actor']['gender'], self.new_actors[1]['gender'])
        self.assertEqual(data['actor']['age'], body['age'])

    @ordered
    def test_update_actor_producer_200(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        body = {'age': 36}
        id = actorids[0]
        res = self.client().patch(
            f'/actors/{id}', json=body, headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['id'], id)
        self.assertEqual(data['actor']['name'], self.new_actors[0]['name'])
        self.assertEqual(data['actor']['gender'], self.new_actors[0]['gender'])
        self.assertEqual(data['actor']['age'], body['age'])

    @ordered
    def test_update_actor_producer_404(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        body = {'age': 40}
        res = self.client().patch(
            '/actors/1111', json=body, headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    @ordered
    def test_update_actor_assistant_forbidden_403(self):
        bearer = retrieve_auth_token(1)
        self.assertTrue(bearer)
        body = {'age': 30}
        id = actorids[0]
        res = self.client().patch(
            f'/actors/{id}', json=body, headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)

    @ordered
    def test_delete_actor_assistant_forbidden_403(self):
        bearer = retrieve_auth_token(1)
        self.assertTrue(bearer)
        id = actorids[0]
        res = self.client().delete(
            f'/actors/{id}', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)

    @ordered
    def test_delete_actor_director_200(self):
        bearer = retrieve_auth_token(2)
        self.assertTrue(bearer)
        id = actorids[0]
        res = self.client().delete(
            f'/actors/{id}', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)

    @ordered
    def test_delete_actor_producer_422(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        id = actorids[0]
        res = self.client().delete(
            f'/actors/{id}', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    @ordered
    def test_delete_actor_producer_200(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        id = actorids[1]
        res = self.client().delete(
            f'/actors/{id}', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)

    @ordered
    def test_retrieve_actors_producer_404(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        res = self.client().get(
            '/actors', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    @ordered
    def test_retrieve_actors_producer_401(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        res = self.client().get(
            '/actors', headers={'Authorization': f'{bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)

    '''
        Tests for Movies
    '''

    @ordered
    def test_retrieve_movies_assistant_404(self):
        bearer = retrieve_auth_token(1)
        self.assertTrue(bearer)
        res = self.client().get(
            '/movies', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    @ordered
    def test_retrieve_movies_unauthorized_401(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)

    @ordered
    def test_create_movie_assistant_forbidden_403(self):
        bearer = retrieve_auth_token(1)
        self.assertTrue(bearer)
        res = self.client().post(
            '/movies', json=self.new_movies[0], headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)

    @ordered
    def test_create_movie_director_forbidden_403(self):
        bearer = retrieve_auth_token(2)
        self.assertTrue(bearer)
        res = self.client().post(
            '/movies', json=self.new_movies[0], headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)

    @ordered
    def test_create_movie_producer_400(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        res = self.client().post(
            '/movies', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    @ordered
    def test_create_movie_producer_200(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        index = 0
        res = self.client().post(
            '/movies', json=self.new_movies[index], headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie']['title'],
                         self.new_movies[index]['title'])
        self.assertEqual(data['movie']['director'],
                         self.new_movies[index]['director'])
        self.assertEqual(data['movie']['year'], self.new_movies[index]['year'])
        movieids.append(data['movie']['id'])

        index += 1
        res = self.client().post(
            '/movies', json=self.new_movies[index], headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie']['title'],
                         self.new_movies[index]['title'])
        self.assertEqual(data['movie']['director'],
                         self.new_movies[index]['director'])
        self.assertEqual(data['movie']['year'], self.new_movies[index]['year'])
        movieids.append(data['movie']['id'])

    @ordered
    def test_create_movie_producer_422(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        res = self.client().post(
            '/movies', json=self.new_movies[1], headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    @ordered
    def test_retrieve_movies_director_200(self):
        bearer = retrieve_auth_token(2)
        self.assertTrue(bearer)
        res = self.client().get(
            '/movies', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertEqual(len(data['movies']), 2)

    @ordered
    def test_update_movie_director_200(self):
        bearer = retrieve_auth_token(2)
        self.assertTrue(bearer)
        body = {'year': 2022}
        id = movieids[0]
        res = self.client().patch(
            f'/movies/{id}', json=body, headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie']['id'], id)
        self.assertEqual(data['movie']['title'],
                         self.new_movies[0]['title'])
        self.assertEqual(data['movie']['director'],
                         self.new_movies[0]['director'])
        self.assertEqual(data['movie']['year'], body['year'])

    @ordered
    def test_update_movie_producer_200(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        body = {'director': 'Cameron'}
        id = movieids[1]
        res = self.client().patch(
            f'/movies/{id}', json=body, headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie']['id'], id)
        self.assertEqual(data['movie']['title'],
                         self.new_movies[1]['title'])
        self.assertEqual(data['movie']['director'],
                         body['director'])
        self.assertEqual(data['movie']['year'], self.new_movies[1]['year'])

    @ordered
    def test_update_movie_producer_404(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        body = {'year': 2022}
        res = self.client().patch(
            '/movies/1111', json=body, headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    @ordered
    def test_update_movie_assistant_forbidden_403(self):
        bearer = retrieve_auth_token(1)
        self.assertTrue(bearer)
        body = {'year': 2021}
        id = movieids[1]
        res = self.client().patch(
            f'/movies/{id}', json=body, headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)

    @ordered
    def test_delete_movie_assistant_forbidden_403(self):
        bearer = retrieve_auth_token(1)
        self.assertTrue(bearer)
        id = movieids[0]
        res = self.client().delete(
            f'/movies/{id}', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)

    @ordered
    def test_delete_movie_director_forbidden_403(self):
        bearer = retrieve_auth_token(2)
        self.assertTrue(bearer)
        id = movieids[0]
        res = self.client().delete(
            f'/movies/{id}', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)

    @ordered
    def test_delete_movie_producer_200(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        id = movieids[0]
        res = self.client().delete(
            f'/movies/{id}', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)

        id = movieids[1]
        res = self.client().delete(
            f'/movies/{id}', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)

    @ordered
    def test_delete_movie_producer_422(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        id = movieids[0]
        res = self.client().delete(
            f'/movies/{id}', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    @ordered
    def test_retrieve_movies_producer_404(self):
        bearer = retrieve_auth_token(3)
        self.assertTrue(bearer)
        res = self.client().get(
            '/movies', headers={'Authorization': f'Bearer {bearer}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

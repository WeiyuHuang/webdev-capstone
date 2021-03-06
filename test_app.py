import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, Movie, Actor

""" Permission list
get:movies
get:actors
post:movies
delete:movies
patch:movies
"""


def insert_test_movie():
    data = {
        'title': 'Titanic',
        'release_date': '1997-12-19'
    }
    movie = Movie(**data)
    movie.insert()

    return data


def query_test_movie():
    query = Movie.query.filter_by(title="Titanic").first()
    return query


def delete_test_movie():
    query = Movie.query.filter_by(title="Titanic").first()
    if query is not None:
        query.deletes()


def insert_test_actor():
    data = {
        'name': 'Leonardo DiCaprio',
        'age': '45',
        'gender': 'Male'
    }
    actor = Actor(**data)
    actor.insert()

    return data


def query_test_actor():
    query = Actor.query.filter_by(name="Leonardo DiCaprio").first()
    return query


def delete_test_actor():
    query = Actor.query.filter_by(name="Leonardo DiCaprio").first()
    if query is not None:
        query.deletes()


class MoviesTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "movies_test"
        self.database_path = os.getenv("DATABASE_URL")
        self.test_movie = {
            'title': 'Titanic',
            'release_date': '1997-12-19'
        }
        # Casting Assistant (can view movies and actors)
        CA_TOKEN = os.getenv("CA_TOKEN")
        # Casting Director (can do everything)
        CD_TOKEN = os.getenv("CD_TOKEN")
        setup_db(self.app)
        self.director_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + CD_TOKEN,
        }
        self.assistant_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + CA_TOKEN,
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # Endpoint: POST /movie tests: RBAC success, 422 failure, RBAC failure 403

    """
    TEST ROLE BASED SUCCESS: Endpoint POST /movie
    A Casting Director can post a movie:
    """

    def test_post_movie_director(self):
        response = self.client().post(f"/movies", data=json.dumps(self.test_movie),
                                      content_type='application/json',
                                      headers=self.director_headers)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response, self.test_movie)
        delete_test_movie()

    """
    TEST FAIL: Endpoint POST /movie
    Not well formatted movie post return 422 unprocessable exception:
    """

    def test_post_movie_422(self):
        wrong_movie = {
            'titlesss': 'Inception 2',
            'release_date': '2024-04-04'
        }
        response = self.client().post(f"/movies", data=json.dumps(wrong_movie),
                                      content_type='application/json',
                                      headers=self.director_headers)
        self.assertEqual(response.status_code, 422)

    """
    TEST ROLE BASED FAIL: Endpoint POST /movie
    A Casting Assistant can't post a movie return 403 unathorized exception:
    """

    def test_post_movie_assistant(self):
        response = self.client().post(f"/movies", data=json.dumps(self.test_movie),
                                      content_type='application/json',
                                      headers=self.assistant_headers)
        self.assertEqual(response.status_code, 403)

    # Endpoint: DELETE /movie tests: RBAC success, 422 failure, RBAC failure 403

    """
    TEST ROLE BASED SUCCESS:  Endpoint DELETE /movies/<int:post_id>
    When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    def test_delete_movie(self):
        insert_test_movie()
        movie = query_test_movie()
        movie_id = movie.id

        # Make sure there is movie to delete
        self.assertIsNotNone(movie)

        self.client().delete(f"/movies/{movie_id}", content_type='application/json',
                             headers=self.director_headers)

        # Make sure removal is persistent
        deleted = Movie.query.get(movie_id)
        self.assertIsNone(deleted)

    """
    TEST FAILURE: Endpoint DELETE /movies/<int:post_id>, 404
    Method Not Allowed when requesting delete using wrong method.
    """

    def test_delete_movie_doesnt_exist(self):
        insert_test_movie()
        response = self.client().delete(f"/movies/10000",
                                        content_type='application/json',
                                        headers=self.director_headers)
        self.assertEqual(response.status_code, 404)
        delete_test_movie()

    """
    TEST ROLE BASED FAILURE:  Endpoint DELETE /movies/<int:post_id>, 403
    An assistant trying to delete a movie without permissions results in a 403.
    """

    def test_delete_movie_not_permitted(self):
        insert_test_movie()
        movie = query_test_movie()
        movie_id = movie.id

        # Check the post exists before deleting
        self.assertIsNotNone(movie)

        response = self.client().delete(f"/movies/{movie_id}",
                                        content_type='application/json',
                                        headers=self.assistant_headers)
        # Removal rejected
        self.assertEqual(response.status_code, 403)

        # Check the post exists after unauthorized delete attempt
        self.assertIsNotNone(movie)
        delete_test_movie()

    # Endpoint: GET /movie tests: RBAC success, 422 failure, RBAC failure 403

    """
    TEST ROLE BASED SUCCESS:  Endpoint GET /movie, 200
    An assistant can list the movies and return a JSON with the list of movies.
    """

    def test_get_movies(self):
        insert_test_movie()
        movie = query_test_movie()
        movie_id = movie.id
        response = self.client().get(f"/movies", content_type='application/json',
                                     headers=self.assistant_headers)
        self.assertEqual(response.status_code, 200)
        # Check if the id of the movie in the response is the same one as inserted
        json_response_data_movie_id = json.loads(response.data)['movies'][0]['id']
        self.assertEqual(json_response_data_movie_id, movie_id)
        delete_test_movie()

    '''
    TEST ROLE BASED FAILURE:  Endpoint GET /movie, 401
    Someone without assistant or director role JWT in the headers
    can't list the movies from the database returning a 401 authorization headers missing error.
    '''

    def test_get_movies_unauthorized(self):
        insert_test_movie()
        # no headers included
        response = self.client().get(f"/movies", content_type='application/json')
        self.assertEqual(response.status_code, 401)
        delete_test_movie()

    '''
    TEST FAILURE:  Endpoint GET /movie, 404
    There are no movies in the database returns 404 error.
    '''

    def test_get_movies_404(self):
        response = self.client().get(f"/movies", content_type='application/json',
                                     headers=self.assistant_headers)
        self.assertEqual(response.status_code, 404)

    # Endpoint: GET /actor tests: RBAC success, 422 failure, RBAC failure 403

    '''
    TEST ROLE BASED SUCCESS:  Endpoint GET /actor, 200
    An assistant can list the actors and return a JSON with the list of actors.
    '''

    def test_get_actors(self):
        insert_test_actor()
        actor = query_test_actor()
        actor_id = actor.id
        response = self.client().get(f"/actors", content_type='application/json',
                                     headers=self.assistant_headers)
        self.assertEqual(response.status_code, 200)
        # Check if the id of the actor in the response is the same one as inserted
        json_response_data_actor_id = json.loads(response.data)['actors'][0]['id']
        self.assertEqual(json_response_data_actor_id, actor_id)
        delete_test_actor()

    '''
    TEST ROLE BASED FAILURE:  Endpoint GET /actor, 401
    Someone without assistant or director role JWT in the headers
    can't list the actors from the database returning a 401 authorization headers missing error.
    '''

    def test_get_actors_401(self):
        insert_test_actor()
        # no headers included
        response = self.client().get(f"/actors", content_type='application/json')
        self.assertEqual(response.status_code, 401)
        delete_test_actor()

    '''
    TEST FAILURE:  Endpoint GET /actor, 404
    There are no actors in the database returns 404 error.
    '''

    def test_get_actors_404(self):
        delete_test_actor()
        response = self.client().get(f"/actors", content_type='application/json',
                                     headers=self.assistant_headers)
        self.assertEqual(response.status_code, 404)

    # Endpoint: PATCH /movie tests: RBAC success, 422 failure, RBAC failure 403

    '''
    TEST ROLE BASED SUCCESS:  Endpoint PATCH /movie, 200
    A director can update a movie with the PATCH/movie endpoint resulting in
    an udpated movie in the database and 200 response code.
    '''

    def test_patch_movie(self):
        insert_test_movie()
        new_movie = {
            'title': 'Titanic 2',
            'release_date': '2020-06-06'
        }
        data = json.dumps(new_movie)
        movie = query_test_movie()
        movie_id = movie.id
        response = self.client().patch(f"/movies/{movie_id}", content_type='application/json',
                                       data=data,
                                       headers=self.director_headers)
        self.assertEqual(response.status_code, 200)
        # Check if the id of the movie in the response is the same one as inserted
        json_response_data_movie_name = json.loads(response.data)['movies']['title']
        self.assertEqual(json_response_data_movie_name, "Titanic 2")
        delete_test_movie()

    '''
    TEST FAILURE:  Endpoint PATCH /movie, 404
    Patching a non-existing movie ID results in 404 error.
    '''

    def test_patch_movie_404(self):
        new_movie = {
            'title': "Titanic 2",
            'release_date': '2020-06-06'
        }
        data = json.dumps(new_movie)
        movie_id = 10000
        response = self.client().patch(f"/movies/{movie_id}", content_type='application/json',
                                       data=data,
                                       headers=self.director_headers)
        self.assertEqual(response.status_code, 404)
        delete_test_movie()

    '''
    TEST ROLE BASED FAILURE:  Endpoint PATCH /movie, 403
    An assistant trying to delete a movie without permissions results in a 403.
    '''

    def test_patch_movie_403(self):
        insert_test_movie()
        new_movie = {
            'title': "Titanic 2",
            'release_date': '2020-06-06'
        }
        data = json.dumps(new_movie)
        movie = query_test_movie()
        movie_id = movie.id
        response = self.client().patch(f"/movies/{movie_id}", content_type='application/json',
                                       data=data,
                                       headers=self.assistant_headers)
        self.assertEqual(response.status_code, 403)
        delete_test_movie()


# Make the tests conveniently executable


if __name__ == "__main__":
    unittest.main()

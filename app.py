import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import db_drop_and_create_all, setup_db, Movie, Actor
from auth import AuthError, requires_auth, retrieve_auth_token


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    # db_drop_and_create_all()

    # Routes/End-points follow

    @app.route('/token/<int:level>')
    def get_oauth_token(level):
        bearer_token = retrieve_auth_token(level)
        success = bearer_token != ""
        return jsonify({
            'success': success,
            'access_token': bearer_token
        })

    @app.route('/movies')
    @requires_auth('get:movies')
    def retrieve_movies(jwt):
        if jwt is not None:
            all_movies = Movie.query.order_by(Movie.id).all()
            movies = [movie.format() for movie in all_movies]

            if len(movies) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'movies': movies
            })

        else:
            abort(401)

    @app.route('/actors')
    @requires_auth('get:actors')
    def retrieve_actors(jwt):
        if jwt is not None:
            all_actors = Actor.query.order_by(Actor.id).all()
            actors = [actor.format() for actor in all_actors]

            if len(actors) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'actors': actors
            })

        else:
            abort(401)

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movie(jwt):
        if jwt is not None:
            body = request.get_json()
            if body is None:
                abort(400)

            new_title = body.get('title', None)
            new_director = body.get('director', None)
            new_year = body.get('year', 2020)

            try:
                new_movie = Movie(
                    title=new_title, director=new_director, year=new_year)
                new_movie.insert()

                return jsonify({
                    'success': True,
                    'movie': new_movie.format()
                })

            except:
                abort(422)

        else:
            abort(401)

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def create_actor(jwt):
        if jwt is not None:
            body = request.get_json()
            if body is None:
                abort(400)

            new_name = body.get('name', None)
            new_gender = body.get('gender', None)
            new_age = body.get('age', 0)

            try:
                new_actor = Actor(
                    name=new_name, gender=new_gender, age=new_age)
                new_actor.insert()

                return jsonify({
                    'success': True,
                    'actor': new_actor.format()
                })

            except:
                abort(422)

        else:
            abort(401)

    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(jwt, id):
        if jwt is not None:
            movie = Movie.query.filter(Movie.id == id).one_or_none()
            if movie is None:
                abort(404)

            body = request.get_json()
            if body is None:
                abort(400)

            new_title = body.get('title', None)
            new_director = body.get('director', None)
            new_year = body.get('year', None)

            if new_title is not None:
                movie.title = new_title
            if new_director is not None:
                movie.director = new_director
            if new_year is not None:
                movie.year = new_year

            try:
                movie.update()
                updated_movie = Movie.query.filter(
                    Movie.id == id).one_or_none()

                return jsonify({
                    'success': True,
                    'movie': updated_movie.format()
                })
            except:
                abort(422)

        else:
            abort(401)

    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(jwt, id):
        if jwt is not None:
            actor = Actor.query.filter(Actor.id == id).one_or_none()
            if actor is None:
                abort(404)

            body = request.get_json()
            if body is None:
                abort(400)

            new_name = body.get('name', None)
            new_gender = body.get('gender', None)
            new_age = body.get('age', None)

            if new_name is not None:
                actor.name = new_name
            if new_gender is not None:
                actor.gender = new_gender
            if new_age is not None:
                actor.age = new_age

            try:
                actor.update()
                updated_actor = Actor.query.filter(
                    Actor.id == id).one_or_none()

                return jsonify({
                    'success': True,
                    'actor': updated_actor.format()
                })
            except:
                abort(422)

        else:
            abort(401)

    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(jwt, id):
        if jwt is not None:
            movie = Movie.query.filter(Movie.id == id).one_or_none()
            if movie is None:
                abort(422)

            try:
                movie.delete()

                return jsonify({
                    'success': True,
                    'deleted': id
                })
            except:
                abort(422)

        else:
            abort(401)

    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(jwt, id):
        if jwt is not None:
            actor = Actor.query.filter(Actor.id == id).one_or_none()
            if actor is None:
                abort(422)

            try:
                actor.delete()

                return jsonify({
                    'success': True,
                    'deleted': id
                })
            except:
                abort(422)

        else:
            abort(401)

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "method not supported"
        }), 405

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad request"
        }), 400

    @app.errorhandler(AuthError)
    def auth_error(e):
        return jsonify(e.error), e.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)

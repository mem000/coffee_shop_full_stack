import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth




'''

'''

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    #initialize the datbase #THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    db_drop_and_create_all()

    CORS(app)   # enable CORS
    # specifying the Flask-CORS behavior
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})



    @app.route('/hello')
    def index():
        return jsonify({'greetings': 'Hello'})

    ## ROUTES
    '''
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks')
    def retrieve_drinks():
        drinks = Drink.query.order_by(Drink.id).all()
        #if len(drinks) == 0:
        #   abort(404)
        drinks_formatted = [drink.short() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': drinks_formatted
        })


    '''
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks-detail')
    @requires_auth('get:drinks-detail')
    def retrieve_drinks_detail(payload):
        print(payload)
        drinks = Drink.query.order_by(Drink.id).all()
        #if len(drinks) == 0:
        #   abort(404)
        drinks_formatted = [drink.long() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': drinks_formatted
        })


    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks', methods=['POST'])
    @requires_auth('post:drinks')
    def create_drink(payload):
        #print(payload)
        req = request.get_json()

        if req is None:
            abort(422)

        #Check if the request includes all the required data
        if ('title' and 'recipe') not in req:
            print('missing data')
            abort(422)
        
        new_title = req.get('title', None)
        new_recipe = req.get('recipe', None) #recipe: list of dictionaries that hold the ingredients
        #Check if the data has a value
        if ('title' or 'recipe') is None:
            print('Data needs value')
            abort(422)
        
        try:
            # Converts input list into # string and stores it in json_string
            new_recipe = json.dumps(new_recipe) 
            new_drink = Drink(title = new_title, recipe = new_recipe)
            new_drink.insert()

            return jsonify({
                'success': True,
                'drinks': [new_drink.long()]
            })
        except Exception as ex:
            print(ex)
            abort(422)

    '''
    @TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<int:drink_id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    def update_drink(payload, drink_id):
        print(payload)

        body = request.get_json()

        #Check if the request includes all the required data
        if ('title' not in body) and ('recipe' not in body):
            print('missing data')
            abort(422)

        try:
            drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
            if drink is None:
                abort(404)

            if ('title' in body) and ('recipe' in body): #update both 'title' and 'recipe'
                drink.title = body.get('title', None)
                drink.recipe = json.dumps(body.get('recipe', None))

            elif ('title') in body: #update both 'title' and leave 'recipe' with the last value
                drink.title = body.get('title', None)

            elif ('recipe') in body: #update both 'recipe' and leave 'title' with the last value
                drink.recipe = json.dumps(body.get('recipe', None))

            drink.update()

            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
            
        except:
            abort(400)


    '''
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<int:drink_id>', methods=['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drink(payload, drink_id):
        print(payload)

        try:
            drink = Drink.query.filter(
                Drink.id == drink_id).one_or_none()

            if drink is None:
                abort(404)

            drink.delete()
            

            return jsonify({
                'success': True,
                'deleted': drink_id
            })

        except:
            abort(422)

    

    ## Error Handling
    '''
    Example error handling for unprocessable entity
    '''
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessable"
        }), 422

    '''
    @TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    '''

    '''
    @TODO implement error handler for 404
        error handler should conform to general task above 
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    


    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above 
    '''
    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        resonse = jsonify(ex.error)
        resonse.status_code = ex.status_code
        return resonse

        
    return app

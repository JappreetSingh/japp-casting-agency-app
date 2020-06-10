The API provides following Endpoints to perform CRUD (Create Read Update Delete) operations on the database of the Casting Agency for model entities Actor and Movie:
GET '/actors'
GET '/movies'
POST '/actors'
POST '/movies'
PATCH '/actors/<id>'
PATCH '/movies/<id>'
DELETE '/actors/<id>'
DELETE '/movies/<id>'
GET '/token/<level>'

Corresponding to the model entities, the database has two tables 'actors' and 'movies' respectively.
The API provides role-based permissions. There are three roles defined:

Casting Assistant (level = 1):
    This role has view (read only) permissions on both tables, hence this role is permitted to perform the following operations only:
    GET '/actors'   
    GET '/movies'

Casting Director (level = 2):
    This role has complete permissions on 'actors', hence this role is permitted to perform all the following operations:
    GET '/actors'
    POST '/actors'
    PATCH '/actors/<id>'
    DELETE '/actors/<id>'

    This role has limited permissions on 'movies'; it can only read and modify existing movies but cannot add new movies or delete existing movies. Hence, this role is permitted to perform the following operations only:
    GET '/movies'
    PATCH '/movies/<id>'

Executive Producer (level = 3):
    This role has complete permissions on actors as well as movies; hence this role is permitted to perform ALL operations provided by the API.

GET '/token/<level>':
All the API endpoints require a Bearer type access-token with the appropriate permissions embedded within the token. The API provides this additional endpoint for convenience to get the JWT (JSON Web Token) of Bearer type corresponding to each role level.
- Request Arguments: 
    An integer from 1 to 3 representing the role or permission level.
- Returns on success:
    A Bearer token string for that role or permission level.
- Returns None if called with an invalid level (outside of range 1 - 3) or if an exception is encountered.
 

Error Codes returned by API:
400 - Bad Request:
    Example: If Body is missing in POST or PATCH operations.
404 - Resource Not Found:
    Example: If no resources are found as a result of GET operations, or the particular resource ID being patched/updated is not found.
405 - Method Not Supported:
    Example: If POST is called with a URL that points to a particular resource rather than the collection of resources, or a PATCH or DELETE is called on a collection rather than a specific resource.
422 - Unprocessable:
    Example: If delete operation cannot be performed because the resource being deleted is not found, or an exception is caught during the CRUD operation.

Authorization Errors:
401 - Unauthorized:
    Since all the API CRUD endpoints require a Bearer token, any request either without a JWT or with a non-bearer type token or an expired token results in this error.
403 - Forbidden:
    When an endpoint is accessed using a Bearer type token without the required permission (example, an assistant role trying to update an existing resource), this error code is returned. 

GET '/actors'
- Retrieves a list of actors
- Request Arguments: None
- Returns on success: 
    A list of actors, with each actor a dictionary with four keys: 
        id (with integer value as ID of the actor record)
        name (with string value as name of the actor)
        gender (with string value as gender of the actor)
        age (with integer value as age of the actor in years)
- Example Response:
    [{'id': 1, 'name': 'Marilyn', 'gender': 'female', age: 28}, {'id': 2, 'name': 'Jackman', 'gender': 'male', age: 39}....]


GET '/movies'
- Retrieves a list of movies
- Request Arguments: None
- Returns on success: 
    A list of movies, with each movie a dictionary with four keys: 
        id (with integer value as ID of the movie record)
        title (with string value as title of the movie)
        director (with string value as name of the director of the movie)
        year (with integer value as year of the movie release starting from 2020)
- Example Response:
    [{'id': 1, 'title': 'Mr. X', 'director': 'Steven', year: 2021}, {'id': 2, 'title': 'Superhero', 'director': 'Cameron', year: 2020}....]


POST '/actors'
- Creates and posts a new actor
- Request Arguments: 
    No query parameter; however a JSON body with key-value pairs is required specifying all attributes.
- Example Request Body: 
        {
            'name': 'Meryl',
            'gender': 'female',
            'age': 38
        }    
- Returns on success: 
    The newly posted actor with a new ID assigned
- Example Response:
    {'id': 3, 'name': 'Meryl', 'gender': 'female', age: 38}

POST '/movies'
- Creates and posts a new movie
- Request Arguments: 
    No query parameter; however a JSON body with key-value pairs is required specifying all attributes.
- Example Request Body: 
        {
            'title': 'Halloween',
            'director': 'Anderson',
            'year': 2021
        }    
- Returns on success: 
    The newly posted movie with a new ID assigned
- Example Response:
    {'id': 5, 'title': 'Halloween', 'director': 'Anderson', year: 2021}

PATCH '/actors/<id>'
- Peforms a partial update or patch on an existing actor resource
- Request Arguments:
    Integer argument id specifying the ID of the resource being updated.
    The JSON body contains one or more key-value pairs of the attributes to update.
- Example Request Body: (to update just the age of the actor with ID 'id')
        {
            'age': 20
        }   
- Returns on success: 
    The updated actor
- Example Response:
    {'id': 3, 'name': 'Meryl', 'gender': 'female', age: 20}

PATCH '/movies/<id>'
- Peforms a partial update or patch on an existing movie resource
- Request Arguments:
    Integer argument id specifying the ID of the resource being updated.
    The JSON body contains one or more key-value pairs of the attributes to update.
- Example Request Body: (to update just the Year of the movie with ID 'id')
        {
            'year': 2022
        }   
- Returns on success: 
    The updated movie
- Example Response:
    {'id': 5, 'title': 'Halloween', 'director': 'Anderson', year: 2022}

DELETE '/actors/<id>'
- Deletes an actor corresponding to the provided ID
- Request Arguments: 
    Query parameter "id" of type integer denoting the ID of the actor being deleted.
- Returns on success: 
    The ID of the deleted actor

DELETE '/movies/<id>'
- Deletes a movie corresponding to the provided ID
- Request Arguments: 
    Query parameter "id" of type integer denoting the ID of the movie being deleted.
- Returns on success: 
    The ID of the deleted movie
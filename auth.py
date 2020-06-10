import json
import os
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import http.client

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'fsnd-japp.auth0.com')
ALGORITHMS = os.getenv('ALGORITHMS', ['RS256'])
API_AUDIENCE = os.getenv('API_AUDIENCE', 'agency')
GRANT_TYPE = os.getenv('GRANT_TYPE', 'client_credentials')

'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


'''
    get_token_auth_header():
    Attempts to get the header from the request and 
        raises an AuthError if no header is present.
    Attempts to split bearer and the token and 
        raises an AuthError if the header is malformed.
    Returns the token part of the header.
'''


def get_token_auth_header():
    # check header is present in the request
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'no_authorization',
            'description': 'Authorization not included in header.'
        }, 401)

    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')  # split bearer and token

    # check if header is malformed
    if len(header_parts) != 2:
        raise AuthError({
            'code': 'malformed_header',
            'description': 'Malformed Authorization Header.'
        }, 401)
    elif header_parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'malformed_header',
            'description': 'Non-bearer Authorization Header.'
        }, 401)

    return header_parts[1]  # Token


'''
    check_permissions(permission, payload):
    @INPUTS
        permission: string permission ('method-verb:model-object')
        payload: decoded jwt payload

    Raises an AuthError if permissions are not included in the payload or
        if the requested permission string is not in the payload permissions array.
    Returns True otherwise.
'''


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)

    return True


'''
    verify_decode_jwt(token):
    @INPUTS
        token: a json web token (string)

    Validates that the token is an Auth0 token with key id (kid).
    Verifies the token using Auth0 /.well-known/jwks.json.
    Decodes the payload from the token, and validates the claims.
    Returns the decoded payload.
'''


def verify_decode_jwt(token):
    # Get the public key from Auth0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # Get the header data from the token
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    if "kid" not in unverified_header:  # check key id
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:  # choose key
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims, please check the audience.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    else:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to find the appropriate key.'
        }, 400)


'''
    @requires_auth(permission) decorator
    @INPUTS
        permission: string permission ('method-verb:model-object')

    Gets the token, decodes the jwt, and checks the requested permission.
    Returns the decorator which passes the decoded payload to the decorated method.
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()  # Get Token
                payload = verify_decode_jwt(token)  # Decode JWT
                # validate claims and check requested permission
                check_permissions(permission, payload)
            except AuthError:
                raise
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator


'''
    @retrieve_auth_token(level)
    @INPUTS
        level: integer
        Valid values: 1 (for assistant role), 2 (for director role), 3 (for producer role)

    Gets the bearer token.
    Returns the token if level is valid and token_type is Bearer, else returns None.
'''


def retrieve_auth_token(level=0):
    if level > 3 or level == 0:
        return None

    try:
        client_id = os.getenv(f'CLIENT_ID{level}')
        client_secret = os.getenv(f'CLIENT_SECRET{level}')

        conn = http.client.HTTPSConnection(AUTH0_DOMAIN)

        payload = {"client_id": client_id, "client_secret": client_secret,
                   "audience": API_AUDIENCE, "grant_type": GRANT_TYPE}

        headers = {"content-type": "application/json"}

        conn.request("POST", "/oauth/token", json.dumps(payload), headers)

        res = conn.getresponse()
        data = res.read()
        conn.close()

        decoded_data = json.loads(data.decode("utf-8"))
        token_type = decoded_data['token_type']
        bearer_token = decoded_data['access_token'] if token_type == "Bearer" else None

        return bearer_token

    except:
        return None

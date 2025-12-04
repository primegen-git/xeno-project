import os
import sys
from typing import Dict
import jwt
from dotenv import load_dotenv


load_dotenv()


JWT_SECRET = os.getenv("JWT_SECRET", None)

if JWT_SECRET is None:
    print("jwt secret does not exist")
    sys.exit(1)


JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", None)

if JWT_ALGORITHM is None:
    print("jwt algorithm does not exist")
    sys.exit(1)


def create_jwt_token(payload: Dict):
    encoded_jwt = jwt.encode(payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

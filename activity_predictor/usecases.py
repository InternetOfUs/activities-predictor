"""module with the business logic"""


import datetime
from os import environ
from pprint import pprint

import requests


class ProdSecretNotFound(Exception):
    pass


class RequestError(Exception):
    pass


class ResponseParsingError(Exception):
    pass


def _get_users():
    """
    Retrieve a list of user identifiers from the profile manager.

    This function sends a GET request to the URL with the provided API key in the headers.
    It then parses the JSON response and extracts the user IDs.

    Raises:
        ProdSecretNotFound: If the PRODSECRET environment variable is not found in the .env file.
        RequestError: If there is an error while making the request to the URL.
        ResponseParsingError: If there is an error while parsing the response.

    Returns:
        list: A list of user IDs if successful, or None if an error occurs.
    """
    try:
        prod_secret = environ.get("PRODSECRET")
        if prod_secret is None:
            raise ProdSecretNotFound("PRODSECRET not found in .env")

        url = "https://internetofus.u-hopper.com/prod/profile_manager/userIdentifiers?offset=0&limit=10000"
        headers = {
            "x-wenet-component-apikey": prod_secret,
            "Accept": "application/json",
        }

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RequestError(f"An error occurred while making the request: {e}")

        try:
            res_json = res.json()
            users = res_json["userIds"]
            return users
        except (KeyError, ValueError) as e:
            raise ResponseParsingError(
                f"An error occurred while parsing the response: {e}"
            )

    except (ProdSecretNotFound, RequestError, ResponseParsingError) as e:
        print(e)
        return None


def _get_user_data(userid, property="locationeventpertime"):
    """
    Retrieve user data for a specific user and property.

    This function sends a GET request to the URL with the provided API key in the headers.
    It then parses the JSON response and returns the user data.

    Args:
        userid (str): The user ID for which to retrieve data.
        property (str, optional): The property to retrieve data for. Defaults to "locationeventpertime".

    Raises:
        ProdSecretNotFound: If the PRODSECRET environment variable is not found in the .env file.
        RequestError: If there is an error while making the request to the URL.
        ResponseParsingError: If there is an error while parsing the response.

    Returns:
        dict: A dictionary containing the user data if successful, or None if an error occurs.
    """
    try:
        prod_secret = environ.get("PRODSECRET")
        if prod_secret is None:
            raise ProdSecretNotFound("PRODSECRET not found in .env")

        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(hours=2)
        today = today.strftime("%Y%m%d%H%M%S") + "000"
        yesterday = yesterday.strftime("%Y%m%d%H%M%S") + "000"

        url = f"https://internetofus.u-hopper.com/prod/streambase/data?from={yesterday}&to={today}&properties={property}&userId={userid}"
        headers = {
            "x-wenet-component-apikey": prod_secret,
            "Accept": "application/json",
        }

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RequestError(f"An error occurred while making the request: {e}")

        try:
            res_json = res.json()
            return res_json
        except ValueError as e:
            raise ResponseParsingError(
                f"An error occurred while parsing the response: {e}"
            )

    except (ProdSecretNotFound, RequestError, ResponseParsingError) as e:
        print(e)
        return None


def process():
    users = _get_users()
    users = users[-10:]
    pprint(users)
    for user in users:
        data = _get_user_data(user)
        pprint(data)

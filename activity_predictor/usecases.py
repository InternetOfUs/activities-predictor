"""module with the business logic"""


import datetime
import json
from os import environ
from pathlib import Path
from pprint import pprint
from uuid import uuid4

import requests

_env_type = {"prod": "PRODSECRET", "beta": "BETASECRET", "dev": "DEVSECRET"}


class SecretNotFound(Exception):
    pass


class RequestError(Exception):
    pass


class ResponseParsingError(Exception):
    pass


def predict_activity(
    data, models_path: Path = Path("/models"), sensor_type=6, country="all"
):
    from wenet.activity_detection import ActivityDetection

    try:
        dt = data[-1]["data"]["locationeventpertime"][-1]["ts"]
        current_timestamp = datetime.datetime.fromtimestamp(dt / 1000)
    except Exception as e:
        print(e)
        return None
    try:
        data_file = Path(f"{uuid4()}.json")
        with open(data_file, "w") as f:
            json.dump(data, f)
        embed_model = (
            models_path
            / f"auto-encoder-cat-datetime/wenet-all-countries-ae-method2-embed22-feats{sensor_type}-m-0/model_0.pkl"
        )
        ad = ActivityDetection(embed_model, models_path / "random-forest")

        pred = ad.predict_from_json(data_file, current_timestamp, country)
        return pred[0]
    finally:
        data_file.unlink()


def _get_users(env="dev"):
    """
    Retrieve a list of user identifiers from the profile manager.

    This function sends a GET request to the URL with the provided API key in the headers.
    It then parses the JSON response and extracts the user IDs.

    Raises:
        SecretNotFound: If the PRODSECRET environment variable is not found in the .env file.
        RequestError: If there is an error while making the request to the URL.
        ResponseParsingError: If there is an error while parsing the response.

    Returns:
        list: A list of user IDs if successful, or None if an error occurs.
    """
    try:
        secret = environ.get(_env_type[env])
        if secret is None:
            raise SecretNotFound(f"{_env_type[env]} not found in .env")

        if env == "prod":
            url = f"https://internetofus.u-hopper.com/{env}/profile_manager/userIdentifiers?offset=0&limit=10000"
        else:
            url = f"https://wenet.u-hopper.com/{env}/profile_manager/userIdentifiers?offset=0&limit=10000"
        headers = {
            "x-wenet-component-apikey": secret,
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

    except (SecretNotFound, RequestError, ResponseParsingError) as e:
        print(e)
        return None


def _get_user_data(userid, property="locationeventpertime", env="dev"):
    """
    Retrieve user data for a specific user and property.

    This function sends a GET request to the URL with the provided API key in the headers.
    It then parses the JSON response and returns the user data.

    Args:
        userid (str): The user ID for which to retrieve data.
        property (str, optional): The property to retrieve data for. Defaults to "locationeventpertime".

    Raises:
        SecretNotFound: If the PRODSECRET environment variable is not found in the .env file.
        RequestError: If there is an error while making the request to the URL.
        ResponseParsingError: If there is an error while parsing the response.

    Returns:
        dict: A dictionary containing the user data if successful, or None if an error occurs.
    """
    try:
        secret = environ.get(_env_type[env])
        if secret is None:
            raise SecretNotFound(f"{_env_type[env]} not found in .env")

        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(hours=2)
        today = today.strftime("%Y%m%d%H%M%S") + "000"
        yesterday = yesterday.strftime("%Y%m%d%H%M%S") + "000"
        if env == "prod":
            url = f"https://internetofus.u-hopper.com/{env}/streambase/data?from={yesterday}&to={today}&properties={property}&userId={userid}"
        else:
            url = f"https://wenet.u-hopper.com/{env}/streambase/data?from={yesterday}&to={today}&properties={property}&userId={userid}"
        headers = {
            "x-wenet-component-apikey": secret,
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

    except (SecretNotFound, RequestError, ResponseParsingError) as e:
        print(e)
        return None


def _update_profile(userid, activity, env="dev", confidence=0.8):
    if userid is None or userid == "":
        print("warning, empty userid")
        return
    try:
        secret = environ.get(_env_type[env])
        if secret is None:
            raise SecretNotFound(f"{_env_type[env]} not found in .env")

        if env == "prod":
            url = f"https://internetofus.u-hopper.com/{env}/profile_manager/profiles/{userid}"
        else:
            url = f"https://wenet.u-hopper.com/{env}/profile_manager/profiles/{userid}"
        headers = {
            "x-wenet-component-apikey": secret,
            "Accept": "application/json",
        }

        try:
            ts = int(datetime.datetime.now().timestamp())
            res = requests.patch(
                url,
                headers=headers,
                json={
                    "latestKnownActivity": {
                        "timestamp": ts,
                        "activity": activity,
                        "confidence": confidence,
                    }
                },
            )
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RequestError(f"An error occurred while making the request: {e}")

    except (SecretNotFound, RequestError) as e:
        print(e)
        return None


def process(nbmax=None, env="dev", models_path=Path("/models")):
    """
    Process and print user data for a specified number of users.

    This function retrieves a list of users using the _get_users() function, and then fetches
    user data for each user using the _get_user_data() function. The retrieved user data is
    printed using the pprint function.

    Args:
        nbmax (int, optional): The maximum number of users to process. If not provided, all users
                               will be processed. If provided, only the last 'nbmax' users will be
                               processed.

    Returns:
        None: This function returns None if an error occurs, or if it completes successfully.
    """
    print("Start to ask for users...")
    users = _get_users(env=env)
    if users is None:
        return None
    if nbmax is not None:
        users = users[-nbmax:]
    pprint(users)
    for user in users:
        data = _get_user_data(user, env=env)
        activity = predict_activity(data=data, models_path=models_path)
        print(f"predicted {activity} for user {user}")
        if activity is not None and activity != "Nothing":
            _update_profile(user, activity, env=env)

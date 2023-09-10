from flask import session, redirect, url_for
from flask_login import current_user, login_user
from authlib.integrations.flask_client import OAuth
import requests
import datetime
import os
from . import models
import mongoengine as me
from dotenv import load_dotenv

load_dotenv()

def fetch_token(name):
    token = models.OAuth2Token.objects(
        name=name, user=current_user._get_current_object()
    ).first()
    return token.to_dict()


def update_token(name, token):
    item = models.OAuth2Token(
        name=name, user=current_user._get_current_object()
    ).first()
    item.token_type = token.get("token_type", "Bearer")
    item.access_token = token.get("access_token")
    item.refresh_token = token.get("refresh_token")
    item.expires = datetime.datetime.utcfromtimestamp(token.get("expires_at"))

    item.save()
    return item


oauth2_client = OAuth()

def handle_authorize(remote, token, user_info):
    if not user_info:
        return redirect(url_for("site.login"))

    user = models.User.objects(
        me.Q(username=user_info.get("username")) | me.Q(email=user_info.get("email"))
    ).first()
    if not user:
        user = models.User(
            username=user_info.get("username"),
            email=user_info.get("email"),
            first_name=user_info.get("first_name", ""),
            last_name=user_info.get("last_name", ""),
            status="active",
        )
        user.resources[remote.name] = user_info
        email = user_info.get("email")
        if email[: email.find("@")].isdigit():
            user.role = "user"
        user.save()

    login_user(user)

    if token:
        oauth2token = models.OAuth2Token(
            name=remote.name,
            user=user,
            access_token=token.get("access_token"),
            token_type=token.get("token_type"),
            refresh_token=token.get("refresh_token", None),
            expires=datetime.datetime.utcfromtimestamp(token.get("expires_in")),
        )
        oauth2token.save()
    next_uri = session.get("next", None)
    if next_uri:
        session.pop("next")
        return redirect(next_uri)
    return redirect(url_for("site.index"))


def init_oauth(server):
    oauth2_client.init_app(app=server, fetch_token=fetch_token, update_token=update_token)
    oauth2_client.register(
        name='psu_passport',
        client_id = os.getenv("PSU_PASSPORT_CLIENT_ID"),
        client_secret= os.getenv("PSU_PASSPORT_CLIENT_SECRET"),
        access_token_url= os.getenv("ACCESS_TOKEN_URL"),
        authorize_url = os.getenv("AUTHORIZE_URL"),
        userinfo_endpoint= os.getenv("USER_INFO"),
        client_kwargs={'scope': 'openid email profile'},
        server_metadata_url=os.getenv("CONF_URL"),
        # jwks = os.getenv("JWKS"),
        end_session=os.getenv("END_SESSION"),
    )
    
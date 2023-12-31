import datetime

import mongoengine as me

from . import users


class OAuth2Token(me.Document):
    user = me.ReferenceField(users.User, dbref=True)
    name = me.StringField(required=True)

    token_type = me.StringField()
    access_token = me.StringField(required=True)
    refresh_token = me.StringField()
    expires = me.DateTimeField(required=True,
                            default=datetime.datetime.now)

    meta = {'collection': 'oauth2_tokens'}

    @property
    def expires_at(self):
        return self.expires.timestamp()

    def to_dict(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )
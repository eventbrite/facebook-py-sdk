from facebook_sdk.exceptions import FacebookResponseException
from facebook_sdk.facebook import Facebook

facebook = Facebook(
    app_id='{app_id}',
    app_secret='{app_secret}',
)

facebook.set_default_access_token(access_token='{access_token}')

try:
    response = facebook.post(
        endpoint='/me/feed',
        params={
            'message': 'User provided message',
            'link': 'http://www.example.com',
        },
    )
except FacebookResponseException as e:
    print e.message
else:
    print 'Posted with id: %(id)s' % {'id': response.json_body.get('id')}
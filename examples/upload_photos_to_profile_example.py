from facebook_sdk.exceptions import FacebookResponseException
from facebook_sdk.facebook import Facebook

facebook = Facebook(
    app_id='{app_id}',
    app_secret='{app_secret}',
)

facebook.set_default_access_token(access_token='{access_token}')

try:
    response = facebook.post(
        endpoint='/me/photos',
        params={
            'message': 'My awesome photo upload example.',
            'source': facebook.file_to_upload('file/to/upload.jpg'),
        },
    )
except FacebookResponseException as e:
    print e.message
else:
    print response.json_body
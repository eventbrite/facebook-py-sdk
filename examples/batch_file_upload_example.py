from facebook_sdk.exceptions import FacebookResponseException
from facebook_sdk.facebook import Facebook

facebook = Facebook(
    app_id='{app_id}',
    app_secret='{app_secret}',
)

facebook.set_default_access_token(access_token='{access_token}')

batch = {
    'photo-one': facebook.request(
        endpoint='/me/photos',
        params={
            'message': 'Foo photo.',
            'source': facebook.file_to_upload('path/to/foo.jpg'),
        },
    ),
    'photo-two': facebook.request(
        endpoint='/me/photos',
        params={
            'message': 'Bar photo.',
            'source': facebook.file_to_upload('path/to/bar.jpg'),
        },
    ),
    'photo-three': facebook.request(
        endpoint='/me/photos',
        params={
            'message': 'Other photo.',
            'source': facebook.file_to_upload('path/to/other.jpg'),
        },
    )
}

try:
    responses = facebook.send_batch_request(requests=batch)
except FacebookResponseException as e:
    print e.message

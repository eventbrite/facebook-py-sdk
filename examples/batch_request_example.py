from facebook_sdk.exceptions import FacebookResponseException
from facebook_sdk.facebook import Facebook

facebook = Facebook(
    app_id='{app_id}',
    app_secret='{app_secret}',
)

facebook.set_default_access_token(access_token='{access_token}')

# Get the name of the logged in user
user_name_request= facebook.request(method='GET', endpoint='/me?fields=id,name')

# Get user likes
user_likes_request = facebook.request(method='GET', endpoint='/me/likes?fields=id,name&amp;limit=1')

# Get user events
user_event_request = facebook.request(method='GET', endpoint='/me/events?fields=id,name&amp;limit=2')

message = 'My name is {result=user-profile:$.name}.\n\n' \
          'I like this page: {result=user-likes:$.data.0.name}.\n\n' \
          'My next 2 events are {result=user-events:$.data.*.name}.'

post_to_feed_request = facebook.request(
    method='POST',
    endpoint='/me/feed',
    params={
        'message': message
    },
)

user_photos_request = facebook.request(method='POST', endpoint='/me/photos?fields=id,source,name&amp;limit=2')

batch = {
    'user-profile': user_name_request,
    'user-likes': user_likes_request,
    'user-events': user_event_request,
    'post-to-feed': post_to_feed_request,
    'user-photos': user_photos_request,
}

try:
    responses = facebook.send_batch_request(requests=batch)
except FacebookResponseException as e:
    print e.message
else:
    for response in responses:
        print response.json_body
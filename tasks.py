from __future__ import (
    absolute_import,
    unicode_literals,
)

from invoke_release.tasks import *  # noqa: F403


configure_release_parameters(  # noqa: F405
    module_name='facebook_sdk',
    display_name='FacebookSDK',
    use_pull_request=True,
    use_tag=False,
)

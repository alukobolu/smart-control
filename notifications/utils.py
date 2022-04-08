from accounts.models import UserAccount
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError



# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(token, title, body, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=body,
                        title= title,
                        sound="default",
                        data=extra))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        # rollbar.report_exc_info(
        #     extra_data={
        #         'token': token,
        #         'message': title,
        #         'extra': extra,
        #         'errors': exc.errors,
        #         'response_data': exc.response_data,
        #     })
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        # rollbar.report_exc_info(
        #     extra_data={'token': token, 'message': message, 'extra': extra})
        raise self.retry(exc=exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        from notifications.models import PushToken
        PushToken.objects.filter(token=token).update(active=False)
    except PushTicketError as exc:
        # Encountered some other per-notification error.
        # rollbar.report_exc_info(
        #     extra_data={
        #         'token': token,
        #         'message': title,
        #         'extra': extra,
        #         'push_response': exc.push_response._asdict(),
        #     })
        raise self.retry(exc=exc)


# send notification helper function
def send_notification(user, title, message) :

    # extracting expo id token
    user_account = UserAccount.objects.get(user = user)
    token = user_account.expo_push_token

    send_push_message(token, title, message)
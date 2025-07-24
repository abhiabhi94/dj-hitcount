from django.apps import apps

try:
    from django.utils.regex_helper import _lazy_re_compile
except ImportError:
    from django.core.validators import _lazy_re_compile

from hitcount.conf import settings

# this is not intended to be an all-knowing IP address regex
IP_RE = _lazy_re_compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")


def get_ip(request):
    """
    Retrieves the remote IP address from the request data.  If the user is
    behind a proxy, they may have a comma-separated list of IP addresses, so
    we need to account for that.  In such a case, only the first IP in the
    list will be retrieved.  Also, some hosts that use a proxy will put the
    REMOTE_ADDR into HTTP_X_FORWARDED_FOR.  This will handle pulling back the
    IP from the proper place.

    **NOTE** This function was taken from django-tracking (MIT LICENSE)
             http://code.google.com/p/django-tracking/

    It has now been modified a bit.
    """
    # if neither header contain a value, just use local loopback
    probable_ip_address = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "127.0.0.1"))
    if probable_ip_address:
        # make sure we have one and only one IP
        match = IP_RE.match(probable_ip_address)
        if match:
            ip_address = match.group(0)
        else:
            # no IP, probably from some dirty proxy or other device
            # throw in some bogus IP
            ip_address = "10.0.0.1"
        return ip_address

    return probable_ip_address


def _get_model_from_string(model_path):
    app_name, model_name = model_path.rsplit(".", 1)
    return apps.get_model(app_name, model_name)


def get_hitcount_model():
    return _get_model_from_string(settings.HITCOUNT_HITCOUNT_MODEL)

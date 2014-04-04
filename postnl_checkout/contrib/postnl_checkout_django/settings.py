from .utils import SettingsBase


class PostNLCheckoutSettings(SettingsBase):
    """ Settings for PostNL checkout. """
    settings_prefix = 'POSTNL_CHECKOUT'

    DEFAULT_TIMEOUT = None
    DEFAULT_ENVIRONMENT = 'sandbox'

    DEFAULT_REDIRECT_URL = 'wishlist'

postnl_checkout_settings = PostNLCheckoutSettings()

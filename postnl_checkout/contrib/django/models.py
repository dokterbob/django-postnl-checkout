from django.db import models

from postnl_checkout.client import PostNLCheckoutClient

from .utils import SudsDjangoCache
from .settings import postnl_checkout_settings as settings


class Order(models.Model):
    """ Django model representing the result of the ReadOrder call. """

    def __init__(self, *args, **kwargs):
        """ Make a client available. """
        super(Order, self).__init__(self, *args, **kwargs)

        suds_cache = SudsDjangoCache()

        self.client = PostNLCheckoutClient(
            username=settings.USERNAME,
            password=settings.PASSWORD,
            webshop_id=settings.WEBSHOP_ID,
            environment=settings.ENVIRONMENT,
            timouet=settings.TIMEOUT,
            cache=suds_cache
        )

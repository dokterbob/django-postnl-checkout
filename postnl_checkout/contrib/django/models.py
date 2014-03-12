from django.db import models

from jsonfield import JSONField

from postnl_checkout.client import PostNLCheckoutClient

from .utils import SudsDjangoCache
from .settings import postnl_checkout_settings as settings


class Order(models.Model):
    """ Django model representing the result of the ReadOrder call. """

    # Primary identifier
    order_token = models.CharField(max_length=255, primary=True)

    # Other indexe fields
    order_ext_ref = models.CharField(db_index=True, max_length=255)
    order_date = models.DateField(db_index=True)
    customer_ext_ref = models.CharField(db_index=True, max_length=255)

    # Raw data
    prepare_order_request = JSONField()
    prepare_order_response = JSONField()

    read_order_request = JSONField()
    read_order_response = JSONField()

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

    @classmethod
    def prepare_order(cls, params):
        """ Call PrepareOrder and create Order using resulting token. """

        # Assert required attributes
        assert 'Order' in params

        order_data = params['Order']

        assert 'ExtRef' in order_data
        assert 'OrderDatum' in order_data
        assert 'VerzendDatum' in order_data

        # Prepare order
        response = self.client.prepare_order(params)

        # Store data
        order = cls(
            order_ext_ref=order_data['ExtRef'],
            order_date=order_data['OrderDatum']
            prepare_order_request=params,
            prepare_order_response=response
        )

        # Validate and save
        order.clean()
        order.save()

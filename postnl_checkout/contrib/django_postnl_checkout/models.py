from django.db import models

from jsonfield import JSONField

from postnl_checkout.exceptions import PostNLResponseException

from .utils import get_client, sudsobject_to_dict

# Instantiate a client
postnl_client = get_client()


class Order(models.Model):
    """ Django model representing the result of the ReadOrder call. """

    # Primary identifier
    order_token = models.CharField(max_length=255, primary_key=True)

    # Other indexe fields
    order_ext_ref = models.CharField(db_index=True, max_length=255)
    order_date = models.DateField(db_index=True)
    customer_ext_ref = models.CharField(db_index=True, max_length=255)

    # Raw data
    prepare_order_request = JSONField()
    prepare_order_response = JSONField()

    read_order_response = JSONField()

    update_order_request = JSONField()

    @classmethod
    def prepare_order(cls, **kwargs):
        """ Call PrepareOrder and create Order using resulting token. """

        # Assert required attributes
        assert 'Order' in kwargs

        order_data = kwargs['Order']

        assert 'ExtRef' in order_data
        assert 'OrderDatum' in order_data
        assert 'VerzendDatum' in order_data

        # Call API
        response = postnl_client.prepare_order(**kwargs)
        response_dict = sudsobject_to_dict(response)

        assert 'Checkout' in response_dict
        assert 'OrderToken' in response_dict['Checkout']
        order_token = response_dict['Checkout']['OrderToken']

        # Store data
        order = cls(
            order_token=order_token,
            order_ext_ref=order_data['ExtRef'],
            order_date=postnl_client.parse_datetime(order_data['OrderDatum']),
            prepare_order_request=kwargs,
            prepare_order_response=response_dict
        )

        # Validate and save
        order.clean()
        order.save()

        return order

    def read_order(self):
        """ Call ReadOrder and store results. """
        assert self.order_token

        # Prepare arguments
        kwargs = {
            'Checkout': {
                'OrderToken': self.order_token
            }
        }

        # Call API
        response = postnl_client.read_order(**kwargs)
        response_dict = sudsobject_to_dict(response)

        # Store response
        self.read_order_response = response_dict
        self.clean()
        self.save()

        # Return updated instance
        return self

    def confirm_order(self, **kwargs):
        """ Call ConfirmOrder and confirm results. """

        # Prepare arguments
        assert not 'Checkout' in kwargs

        kwargs['Checkout'] = {
            'OrderToken': self.order_token
        }

        # Call API
        result = postnl_client.confirm_order(**kwargs)

        # Make sure the result is sensible
        if result['Order']['ExtRef'] != self.order_ext_ref:
            raise Exception('Order reference does not correspond.')

    def update_order(self, **kwargs):
        """ Call UpdateOrder, store request and confirm results. """

        # Prepare arguments
        assert not 'Checkout' in kwargs

        kwargs['Checkout'] = {
            'OrderToken': self.order_token
        }

        # Call API
        response = postnl_client.update_order(**kwargs)

        assert response in (True, False)

        if not response:
            raise PostNLResponseException('Could not update order.')

        # Store request
        self.update_order_request = kwargs
        self.clean()
        self.save()

        # Return updated instance
        return self

    def ping_status(self):
        """ Wrap PingStatus for ease of accesibility. """

        return postnl_client.ping_status()

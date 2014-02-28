import unittest

from ..client import PostNLCheckoutClient


class ClientTests(unittest.TestCase):
    def test_init(self):
        """ Test instantiating the client """

        client = PostNLCheckoutClient(
            username='test_user',
            password='test_password',
            webshop_id='test_shop',
            environment='sandbox'
        )

        # Get suds client
        self.assertTrue(hasattr(client, 'client'))
        suds_client = client.client

        # Make sure we have a service
        self.assertTrue(hasattr(suds_client, 'service'))
        service = suds_client.service

        # Make sure necessary methods are available
        self.assertTrue(hasattr(service, 'ReadOrder'))
        self.assertTrue(hasattr(service, 'ConfirmOrder'))
        self.assertTrue(hasattr(service, 'UpdateOrder'))
        self.assertTrue(hasattr(service, 'PingStatus'))

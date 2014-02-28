import unittest

from httmock import HTTMock

from ..client import PostNLCheckoutClient


class ClientTests(unittest.TestCase):
    def setUp(self):
        """ Instantiate client for tests. """

        self.client = PostNLCheckoutClient(
            username='test_user',
            password='test_password',
            webshop_id='test_shop',
            environment='sandbox'
        )

    def test_client(self):
        """ Test instantiated client """

        # Get suds client
        self.assertTrue(hasattr(self.client, 'suds_client'))

        # Make sure we have a service
        self.assertTrue(hasattr(self.client, 'service'))
        service = self.client.service

        # Make sure necessary methods are available
        self.assertTrue(hasattr(service, 'ReadOrder'))
        self.assertTrue(hasattr(service, 'ConfirmOrder'))
        self.assertTrue(hasattr(service, 'UpdateOrder'))
        self.assertTrue(hasattr(service, 'PingStatus'))

    def test_ping_status(self):
        """ ping_status returns True or False """

        ok_response = lambda url, request: """
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"> <s:Body>
            <PingStatusResponse xmlns="http://postnl.nl/cif/services/WebshopCheckoutWebService/" zmlns:a="http://schemas.datacontract.org/2004/07/Tpp.Cif.Services.Domain.WebshopCheckoutWebService" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <a:Status>OK</a:Status> </PingStatusResponse>
            </s:Body>
            </s:Envelope>
        """

        nok_response = lambda url, request: """
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"> <s:Body>
            <PingStatusResponse xmlns="http://postnl.nl/cif/services/WebshopCheckoutWebService/" zmlns:a="http://schemas.datacontract.org/2004/07/Tpp.Cif.Services.Domain.WebshopCheckoutWebService" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <a:Status>NOK</a:Status> </PingStatusResponse>
            </s:Body>
            </s:Envelope>
        """

        with HTTMock(ok_response):
            self.assertEquals(self.client.ping_status(), True)

        with HTTMock(nok_response):
            self.assertEquals(self.client.ping_status(), False)

import os

from django.test import TestCase

from httmock import HTTMock

from ..client import PostNLCheckoutClient


class ClientTests(TestCase):
    def setUp(self):
        """ Instantiate client for tests. """

        def response(url, request):
            if '.xsd' in url.path:
                # Request of XSD file from WSDL
                filename = url.path.rsplit('/', 1)[1]

                return self.read_file('wsdl/' + filename)

            # Request for WSDL file
            self.assertEquals(
                url.geturl(),
                PostNLCheckoutClient.SANDBOX_ENDPOINT_URL
            )

            return self.read_file('wsdl/WebshopCheckoutWebService_1.wsdl')

        with HTTMock(response):
            self.client = PostNLCheckoutClient(
                username='klant1',
                # Note: sha1 hashed password:
                # dd7b7b74ea160e049dd128478e074ce47254bde8
                password='xx',
                webshop_id='a0713e4083a049a996c302f48bb3f535',
                environment='sandbox'
            )

    def read_file(self, filename):
        """ Read file from data directory and return contents. """

        assert filename

        data_directory = os.path.join(os.path.dirname(__file__), 'data')

        f = open(os.path.join(data_directory, filename))

        return f.read()

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

    def test_add_webshop(self):
        """ Test _add_webshop """

        raise NotImplementedError()

    def test_prepare_order(self):
        """ Test prepare_order """

        raise NotImplementedError()

    def test_read_order(self):
        """ Test read_order """

        def response(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('read_order_request.xml')
            )

            return self.read_file('read_order_response.xml')

        kwargs = {
            'Checkout': {
                'OrderToken': '0cfb4be2-47cf-4eac-865c-d66657953d5c'
            }
        }

        # Execute API call
        with HTTMock(response):
            result = self.client.read_order(**kwargs)

        # Assert presence of top level elements
        self.assertIn('BetaalMethode', result)
        self.assertIn('Bezorging', result)
        self.assertIn('CommunicatieOpties', result)
        self.assertIn('Consument', result)
        self.assertIn('Facturatie', result)
        self.assertIn('Opties', result)
        self.assertIn('Order', result)
        self.assertIn('Voorkeuren', result)
        self.assertIn('Webshop', result)

    def test_confirm_order(self):
        """ Test confirm_order """

        raise NotImplementedError()

    def test_update_order(self):
        """ Test update_order """

        raise NotImplementedError()

    def test_ping_status(self):
        """ ping_status returns True or False """

        def ok_response(url, request):
            # Assert
            self.assertXMLEqual(
                request.body,
                self.read_file('ping_status_request.xml')
            )
            return self.read_file('ping_status_response_ok.xml')

        def nok_response(url, request):
            return self.read_file('ping_status_response_nok.xml')

        with HTTMock(ok_response):
            self.assertEquals(self.client.ping_status(), True)

        with HTTMock(nok_response):
            self.assertEquals(self.client.ping_status(), False)

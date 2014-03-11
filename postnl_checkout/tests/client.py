import os
import datetime

from django.test import TestCase

from httmock import HTTMock

from ..client import PostNLCheckoutClient


class ClientTests(TestCase):
    # IntRef used for testing
    intref = 'a0713e4083a049a996c302f48bb3f535'

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

    def assertWebshop(self, result):
        """ Assert webshop and id in result. """

        self.assertIn('Webshop', result)
        self.assertIn('IntRef', result.Webshop)
        self.assertEquals(result.Webshop.IntRef, self.intref)

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

        kwargs = {
            'kaas': 'lekker'
        }

        self.client._add_webshop(kwargs)

        # Kwargs should be updated with IntRef
        self.assertEquals({
            'kaas': 'lekker',
            'Webshop': {'IntRef': self.intref}
        }, kwargs)

    def test_parse_datetime(self):
        """ TEst parsing datetimes """
        output = self.client.parse_datetime('15-06-1977 00:00:00')

        self.assertEquals(
            output,
            datetime.datetime(
                year=1977, month=6, day=15,
                hour=0, minute=0, second=0
            )
        )

    def test_format_datetime(self):
        """ TEst parsing datetimes """
        output = self.client.format_datetime(
            datetime.datetime(
                year=1977, month=6, day=15,
                hour=0, minute=0, second=0
            )
        )

        self.assertEquals(
            output,
            '15-06-1977 00:00:00'
        )

    def test_prepare_order(self):
        """ Test PrepareOrder """

        def response(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('prepare_order_request.xml')
            )

            return self.read_file('prepare_order_response.xml')

        kwargs = {
            'AangebodenBetaalMethoden': {
                'PrepareOrderBetaalMethode': {
                    'Code': 'IDEAL',
                    'Prijs': '5.00'
                }
            },
            'AangebodenCommunicatieOpties': {
                'PrepareOrderCommunicatieOptie': {
                    'Code': 'NEWS'
                }
            },
            # FIXME: the following is not submitted by SUDS
            # Most probably because it is not properly defined in the WSDL
            # Contact PostNL about this.
            # 'AangebodenOpties': {
            #     'PrepareOrderOptie': {
            #         'Code': 'WRAP',
            #         'Prijs': '2.50'
            #     }
            # },
            # 'AfleverOpties': {
            #     'AfleverOptie': {
            #         'Code': 'PG',
            #         'Kosten': '0.00',
            #         'Toegestaan': True
            #     }
            # },
            'Consument': {
                'ExtRef': 'test@e-id.nl'
            },
            'Contact': {
                'Url': 'http://www.kadowereld.nl/url/contact'
            },
            'Order': {
                'ExtRef': '1105_900',
                'OrderDatum': self.client.format_datetime(
                    datetime.datetime(
                        year=2011, month=7, day=21,
                        hour=20, minute=11, second=0
                    )
                ),
                'Subtotaal': '125.00',
                'VerzendDatum': self.client.format_datetime(
                    datetime.datetime(
                        year=2011, month=7, day=22,
                        hour=20, minute=11, second=0
                    )
                ),
                'VerzendKosten': '12.50'
            },
            'Retour': {
                'BeschrijvingUrl': 'http://www.kadowereld.nl/url/beschrijving',
                'PolicyUrl': 'http://www.kadowereld.nl/url/policy',
                'RetourTermijn': 28,
                'StartProcesUrl': 'http://www.kadowereld.nl/url/startproces'
            },
            'Service': {
                'Url': 'http://www.kadowereld.nl/url/service'
            }
        }

        # Execute API call
        with HTTMock(response):
            result = self.client.prepare_order(**kwargs)

        # Assert checkout
        self.assertIn('Checkout', result)

        checkout = result.Checkout
        self.assertIn('OrderToken', checkout)
        self.assertEquals(
            checkout.OrderToken, '0cfb4be2-47cf-4eac-865c-d66657953d5c'
        )

        self.assertWebshop(result)

    def test_read_order(self):
        """ Test ReadOrder """

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

        self.assertWebshop(result)

        # Dive into voorkeuren
        voorkeuren = result['Voorkeuren']
        self.assertIn('Bezorging', voorkeuren)

        # Attempt parsing datetime
        self.assertEquals(
            self.client.parse_datetime(voorkeuren['Bezorging']['Datum']),
            datetime.datetime(
                year=2012, month=4, day=26,
                hour=0, minute=0, second=0
            )
        )

        # FIXME: According to the specs, a ProductType field exists.
        # However, this is not in the XSD and hence causes a validation error.
        # For now, this has been removed from the mock response for now.
        # Eventually, PostNL should be contacted about this.

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

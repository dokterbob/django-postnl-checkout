import datetime

from django.test import TestCase

from httmock import HTTMock

from django_dynamic_fixture import G, N

from postnl_checkout.tests.base import PostNLTestMixin

from ..models import Order, postnl_client


class OrderTests(PostNLTestMixin, TestCase):
    """ Tests for Order model. """

    def setUp(self):
        super(OrderTests, self).setUp()

        self.order_datum = datetime.datetime(
            year=2011, month=7, day=21,
            hour=20, minute=11, second=0
        )

        self.verzend_datum = datetime.datetime(
            year=2011, month=7, day=22,
            hour=20, minute=11, second=0
        )

    def test_save(self):
        """ Test saving an Order model. """
        instance = N(Order)
        instance.clean()
        instance.save()

    def test_prepare_order(self):
        """ Test prepare_order class method. """

        # Setup mock response
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
                'OrderDatum': postnl_client.format_datetime(self.order_datum),
                'Subtotaal': '125.00',
                'VerzendDatum': postnl_client.format_datetime(
                    self.verzend_datum
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
            instance = Order.prepare_order(**kwargs)

        # Assert model field values
        self.assertTrue(instance.pk)

        self.assertEquals(
            instance.order_token, '0cfb4be2-47cf-4eac-865c-d66657953d5c'
        )
        self.assertEquals(
            instance.order_ext_ref, '1105_900'
        )
        self.assertEquals(
            instance.order_date, self.order_datum
        )

        # Assert JSON values
        self.assertEquals(instance.prepare_order_request, kwargs)
        self.assertEquals(instance.prepare_order_response, {
            'Checkout': {
                'OrderToken': '0cfb4be2-47cf-4eac-865c-d66657953d5c',
                'Url': (
                    'http://tpppm-test.e-id.nl/Orders/OrderCheckout'
                    '?token=0cfb4be2-47cf-4eac-865c-d66657953d5c'
                )
            },
            'Webshop': {
                'IntRef': 'a0713e4083a049a996c302f48bb3f535'
            }
        })

    def test_read_order(self):
        """ Test read_order method. """

        # Setup mock response
        def response(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('read_order_request.xml')
            )

            return self.read_file('read_order_response.xml')

        instance = G(
            Order,
            order_token='0cfb4be2-47cf-4eac-865c-d66657953d5c'
        )

        # Read order data
        with HTTMock(response):
            new_instance = instance.read_order()

        response_data = new_instance.read_order_response

        self.assertTrue(response_data)

        self.assertEquals(response_data, {
            'Voorkeuren': {
                'Bezorging': {
                    'Tijdvak': {
                        'Start': '10:30',
                        'Eind': '08:30'
                    },
                    'Datum': '26-4-2012 00:00:00'
                }
            },
            'Consument': {
                'GeboorteDatum': '15-06-1977 00:00:00',
                'ExtRef': 'jjansen',
                'TelefoonNummer': '06-12345678',
                'Email': 'j.jansen@e-id.nl'
            },
            'Facturatie': {
                'Adres': {
                    'Huisnummer': '1',
                    'Initialen': 'J',
                    'Geslacht': 'Meneer',
                    'Deurcode': None,
                    'Gebruik': 'P',
                    'Gebouw': None,
                    'Verdieping': None,
                    'Achternaam': 'Jansen',
                    'Afdeling': None,
                    'Regio': None,
                    'Land': 'NL',
                    'Wijk': None,
                    'Postcode': '4131LV',
                    'Straat':
                    'Lage Biezenweg',
                    'Bedrijf': None,
                    'Plaats': 'Vianen',
                    'Tussenvoegsel': None,
                    'Voornaam': 'Jan',
                    'HuisnummerExt': None
                }
            },
            'Webshop': {
                'IntRef': 'a0713e4083a049a996c302f48bb3f535'
            },
            'CommunicatieOpties': {
                'ReadOrderResponseCommunicatieOptie': [
                    {
                        'Text': 'Do not deliver to neighbours',
                        'Code': 'REMARK'
                    }
                ]
            },
            'Bezorging': {
                'ServicePunt': {
                    'Huisnummer': None,
                    'Initialen': None,
                    'Geslacht': None,
                    'Deurcode': None,
                    'Gebruik': None,
                    'Gebouw': None,
                    'Verdieping': None,
                    'Achternaam': None,
                    'Afdeling': None,
                    'Regio': None,
                    'Land': None,
                    'Wijk': None,
                    'Postcode': None,
                    'Straat': None,
                    'Bedrijf': None,
                    'Plaats': None,
                    'Tussenvoegsel': None,
                    'Voornaam': None,
                    'HuisnummerExt': None
                },
                'Geadresseerde': {
                    'Huisnummer': '1',
                    'Initialen': 'J',
                    'Geslacht': 'Meneer',
                    'Deurcode': None,
                    'Gebruik': 'Z',
                    'Gebouw': None,
                    'Verdieping': None,
                    'Achternaam': 'Janssen',
                    'Afdeling': None,
                    'Regio': None,
                    'Land': 'NL',
                    'Wijk': None,
                    'Postcode': '4131LV',
                    'Straat': 'Lage Biezenweg ',
                    'Bedrijf': 'E-ID',
                    'Plaats': 'Vianen',
                    'Tussenvoegsel': None,
                    'Voornaam': 'Jan',
                    'HuisnummerExt': None
                }
            },
            'Opties': {
                'ReadOrderResponseOpties': [
                    {
                        'Text': 'Congratulat ions with your new foobar!',
                        'Code': 'CARD',
                        'Prijs': '2.00'
                    }
                ]
            },
            'Order': {
                'ExtRef': '15200_001'
            },
            'BetaalMethode': {
                'Optie': '0021',
                'Code': 'IDEAL',
                'Prijs': '0.00'
            }
        })

    def test_confirm_order(self):
        """ Test confirm_order """

        def response(url, request):
            self.assertXMLEqual(
                request.body, self.read_file('confirm_order_request.xml')
            )

            return self.read_file('confirm_order_response.xml')

        kwargs = {
            'Order': {
                'PaymentTotal': '183.25'
            }
        }

        instance = G(
            Order,
            order_token='0cfb4be2-47cf-4eac-865c-d66657953d5c',
            order_ext_ref='1105_900'
        )

        # Execute API call
        with HTTMock(response):
            instance.confirm_order(**kwargs)

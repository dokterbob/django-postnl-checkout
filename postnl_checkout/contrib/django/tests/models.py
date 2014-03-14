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

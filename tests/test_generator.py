#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
from datetime import datetime, timedelta
from unittest import TestCase

from faker import Faker

# from nise.generators.generator import AbstractGenerator
from nise.generators.aws import (AWS_COLUMNS,
                                 AWSGenerator,
                                 DataTransferGenerator,
                                 EBSGenerator,
                                 EC2Generator,
                                 RDSGenerator,
                                 Route53Generator,
                                 S3Generator,
                                 VPCGenerator)


class TestGenerator(AWSGenerator):

    def _update_data(self, row, start, end):
        return None

    def generate_data(self):
        return []


class AbstractGeneratorTestCase(TestCase):
    """
    TestCase class for Abstract Generator
    """

    def setUp(self):
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.payer_account = self.fake.ean(length=13)
        self.usage_accounts = (self.payer_account,
                               self.fake.ean(length=13),
                               self.fake.ean(length=13),
                               self.fake.ean(length=13),
                               self.fake.ean(length=13))

    def test_set_hours_invalid_start(self):
        """Test that the start date must be a date object."""
        with self.assertRaises(ValueError):
            TestGenerator('invalid', self.now,
                          self.payer_account, self.usage_accounts)

    def test_set_hours_invalid_end(self):
        """Test that the end date must be a date object."""
        with self.assertRaises(ValueError):
            TestGenerator(self.now, 'invalid',
                          self.payer_account, self.usage_accounts)

    def test_set_hours_none_start(self):
        """Test that the start date is not None."""
        with self.assertRaises(ValueError):
            TestGenerator(None, self.now,
                          self.payer_account, self.usage_accounts)

    def test_set_hours_none_end(self):
        """Test that the end date is not None."""
        with self.assertRaises(ValueError):
            TestGenerator(self.now, None,
                          self.payer_account, self.usage_accounts)

    def test_set_hours_compared_dates(self):
        """Test that the start date must be less than the end date."""
        hour_ago = self.now - self.one_hour
        with self.assertRaises(ValueError):
            TestGenerator(self. now, hour_ago,
                          self.payer_account, self.usage_accounts)

    def test_set_hours(self):
        """Test that a valid list of hours are returned."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        expected = [{'start': two_hours_ago,
                     'end': two_hours_ago + self.one_hour},
                     {'start': two_hours_ago + self.one_hour,
                     'end': two_hours_ago + self.one_hour + self.one_hour}]
        self.assertEqual(generator.hours, expected)

    def test_timestamp_none(self):
        """Test that the timestamp method fails with None."""
        with self.assertRaises(ValueError):
            TestGenerator.timestamp(None)

    def test_timestamp_invalid(self):
        """Test that the timestamp method fails with an not a date."""
        with self.assertRaises(ValueError):
            TestGenerator.timestamp('invalid')

    def test_init_data_row(self):
        """Test the init data row method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        a_row = generator._init_data_row(two_hours_ago, self.now)
        self.assertIsInstance(a_row, dict)
        for col in AWS_COLUMNS:
            self.assertIsNotNone(a_row.get(col))

    def test_init_data_row_start_none(self):
        """Test the init data row method none start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        with self.assertRaises(ValueError):
            generator._init_data_row(None, self.now)

    def test_init_data_row_end_none(self):
        """Test the init data row method none end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        with self.assertRaises(ValueError):
            generator._init_data_row(two_hours_ago, None)

    def test_init_data_row_start_invalid(self):
        """Test the init data row method invalid start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        with self.assertRaises(ValueError):
            generator._init_data_row('invalid', self.now)

    def test_init_data_row_end_invalid(self):
        """Test the init data row method invalid end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        with self.assertRaises(ValueError):
            generator._init_data_row(two_hours_ago, 'invalid')

    def test_get_location(self):
        """Test the _get_location method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        location = generator._get_location()

        self.assertIsInstance(location, tuple)

        attributes = {}
        attributes['region'] = 'us-west-1a'
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts, attributes)
        location = generator._get_location()
        self.assertIn('us-west-1', location)


class AWSGeneratorTestCase(TestCase):
    """Test Base for specific generator classes."""

    def setUp(self):
        """Set up each test."""
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.payer_account = self.fake.ean(length=13)
        self.usage_accounts = (self.payer_account,
                                self.fake.ean(length=13),
                                self.fake.ean(length=13),
                                self.fake.ean(length=13),
                                self.fake.ean(length=13))

        self.product_sku = '12345'
        self.tags = {'key': 'value'}
        self.instance_type = {
            'inst_type': '1',
            'vcpu': '1',
            'memory': '1',
            'storage': '1',
            'family': '1',
            'cost': '1',
            'rate': '1'
        }
        self.product_code = 'AmazonEC2'
        self.product_name = 'Amazon Elastic Compute Cloud'
        self.product_family = 'DNS Query'
        self.resource_id = '12345'
        self.amount = 1
        self.rate = 0.1
        self.attributes= {
            'product_sku': self.product_sku,
            'tags': self.tags,
            'instance_type': self.instance_type,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'resource_id': self.resource_id,
            'amount': self.amount,
            'rate': self.rate,
            'product_family': self.product_family
        }
        self.two_hours_ago = (self.now - self.one_hour) - self.one_hour


class TestRDSGenerator(AWSGeneratorTestCase):
    """Tests for the RDS Generator type."""

    # def setUp(self):
    #     """Set up each test."""
    #     super().setUp()


    def test_init_with_attributes(self):
        """Test the unique init options for RDS."""

        generator = RDSGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        self.assertEqual(generator._product_sku, self.product_sku)
        self.assertEqual(generator._tags, self.tags)
        self.assertEqual(generator._instance_type[:-1], tuple(self.instance_type.values()))

    def test_update_data(self):
        """Test RDS specific update data method."""
        generator = RDSGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now)

        self.assertEqual(row['lineItem/ProductCode'], 'AmazonRDS')
        self.assertEqual(row['lineItem/Operation'], 'CreateDBInstance')
        self.assertEqual(row['product/ProductName'], 'Amazon Relational Database Service')

    def test_generate_data(self):
        """Test that the RDS generate_data method works."""
        generator = RDSGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestDataTransferGenerator(AWSGeneratorTestCase):
    """Tests for the Data Transfer Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        generator = DataTransferGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        self.assertEqual(generator._product_code, self.product_code)
        self.assertEqual(generator._tags, self.tags)
        self.assertEqual(generator._resource_id, self.resource_id)
        self.assertEqual(generator._amount, self.amount)
        self.assertEqual(generator._rate, self.rate)

    def test_update_data(self):
        """Test Data Transfer specific update data method."""
        generator = DataTransferGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now)

        self.assertEqual(row['product/servicecode'], 'AWSDataTransfer')
        self.assertEqual(row['product/productFamily'], 'Data Transfer')

    def test_generate_data(self):
        """Test that the Data Transfer generate_data method works."""
        generator = DataTransferGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestEBSGenerator(AWSGeneratorTestCase):
    """Tests for the EBS Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        generator = EBSGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        self.assertEqual(generator._product_sku, self.product_sku)
        self.assertEqual(generator._tags, self.tags)
        self.assertEqual(generator._resource_id, 'vol-' + self.resource_id)
        self.assertEqual(generator._amount, self.amount)
        self.assertEqual(generator._rate, self.rate)

    def test_update_data(self):
        """Test EBS specific update data method."""
        generator = EBSGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now)

        self.assertEqual(row['product/servicecode'], 'AmazonEC2')
        self.assertEqual(row['product/productFamily'], 'Storage')
        self.assertEqual(row['lineItem/Operation'], 'CreateVolume')

    def test_generate_data(self):
        """Test that the EBS generate_data method works."""
        generator = EBSGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestEC2Generator(AWSGeneratorTestCase):
    """Tests for the EBS Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        generator = EC2Generator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        self.assertEqual(generator._product_sku, self.product_sku)
        self.assertEqual(generator._tags, self.tags)
        self.assertEqual(generator._resource_id, 'i-' + self.resource_id)
        self.assertEqual(generator._instance_type[:-1], tuple(self.instance_type.values()))

    def test_update_data(self):
        """Test EBS specific update data method."""
        generator = EC2Generator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now)

        self.assertEqual(row['product/servicecode'], 'AmazonEC2')
        self.assertEqual(row['product/productFamily'], 'Compute Instance')
        self.assertEqual(row['lineItem/Operation'], 'RunInstances')

    def test_generate_data(self):
        """Test that the EBS generate_data method works."""
        generator = EC2Generator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestRoute53Generator(AWSGeneratorTestCase):
    """Tests for the Route53 Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        generator = Route53Generator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        self.assertEqual(generator._product_sku, self.product_sku)
        self.assertEqual(generator._tags, self.tags)
        self.assertEqual(generator._product_family, self.product_family)


    def test_update_data(self):
        """Test Route53 specific update data method."""
        generator = Route53Generator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now)

        self.assertEqual(row['product/servicecode'], 'AmazonRoute53')
        self.assertEqual(row['product/productFamily'], self.product_family)
        self.assertEqual(row['lineItem/ProductCode'], 'AmazonRoute53')

    def test_generate_data(self):
        """Test that the Route53 generate_data method works."""
        generator = Route53Generator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestS3Generator(AWSGeneratorTestCase):
    """Tests for the S3 Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        generator = S3Generator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        self.assertEqual(generator._product_sku, self.product_sku)
        self.assertEqual(generator._tags, self.tags)
        self.assertEqual(generator._amount, self.amount)
        self.assertEqual(generator._rate, self.rate)


    def test_update_data(self):
        """Test S3 specific update data method."""
        generator = S3Generator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now)

        self.assertEqual(row['product/servicecode'], 'AmazonS3')
        self.assertEqual(row['lineItem/Operation'], 'GetObject')
        self.assertEqual(row['lineItem/ProductCode'], 'AmazonS3')

    def test_generate_data(self):
        """Test that the S3 generate_data method works."""
        generator = S3Generator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        data = generator.generate_data()
        self.assertNotEqual(data, [])


class TestVPCGenerator(AWSGeneratorTestCase):
    """Tests for the VPC Generator type."""

    def test_init_with_attributes(self):
        """Test the unique init options for Data Transfer."""

        generator = VPCGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        self.assertEqual(generator._product_sku, self.product_sku)
        self.assertEqual(generator._tags, self.tags)
        self.assertEqual(generator._resource_id, 'vpn-' + self.resource_id)


    def test_update_data(self):
        """Test VPC specific update data method."""
        generator = VPCGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        start_row = {}
        row = generator._update_data(start_row, self.two_hours_ago, self.now)

        self.assertEqual(row['product/servicecode'], 'AmazonVPC')
        self.assertEqual(row['lineItem/Operation'], 'CreateVpnConnection')
        self.assertEqual(row['lineItem/ProductCode'], 'AmazonVPC')

    def test_generate_data(self):
        """Test that the VPC generate_data method works."""
        generator = VPCGenerator(self.two_hours_ago, self.now,
                                 self.payer_account, self.usage_accounts,
                                 self.attributes)
        data = generator.generate_data()
        self.assertNotEqual(data, [])

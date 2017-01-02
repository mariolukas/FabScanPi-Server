import unittest
from urllib2 import URLError

from mock import patch

from fabscan.util.FSUpdate import get_latest_version_tag, upgrade_is_available


class FSUpdateTestCase(unittest.TestCase):

	@patch('urllib2.urlopen', return_value=open('Packages.example', 'r'))
	def test_get_latest_version_successfull(self, urlopen_mock):
		result = get_latest_version_tag()
		self.assertEqual(result, "0.3.1")

	@patch('urllib2.urlopen', side_effect=URLError("Connection error"))
	def test_get_latest_version_exception(self, urlopen_mock):
		result = get_latest_version_tag()
		self.assertEqual(result, "0.0.0")

	@patch('urllib2.urlopen', return_value=open('Packages.example', 'r'))
	def test_upgrade_is_available_upgrade_available(self, urlopen_mock):
		upgrade_available, upgrade_version = upgrade_is_available("0.1.2")
		self.assertTrue(upgrade_available)
		self.assertEqual(upgrade_version, "0.3.1")

	@patch('urllib2.urlopen', return_value=open('Packages.example', 'r'))
	def test_upgrade_is_available_upgrade_not_available(self, urlopen_mock):
		upgrade_available, upgrade_version = upgrade_is_available("0.3.1")
		self.assertFalse(upgrade_available)
		self.assertEqual(upgrade_version, "0.3.1")


if __name__ == '__main__':
	unittest.main()

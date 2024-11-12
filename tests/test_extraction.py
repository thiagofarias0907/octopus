import unittest
from unittest import mock
import os
from unittest.mock import patch, Mock, seal

from extraction import OctopusPlanParser, DetailedOfferParser, PlanOffer
from extraction.exceptions import InvalidContentException, ParsingFailureException, DownloadException

page_one_content = ""
page_two_content = ""

test_dir = os.path.dirname(__file__)
with open(os.path.join(test_dir,'pages/page1.htm'), 'r', encoding='utf-8') as file:
    page_one_content = file.read()

with open(os.path.join(test_dir,'pages/page2.htm'), 'r', encoding='utf-8') as file:
    page_two_content = file.read()


class TestExtraction(unittest.TestCase):

    def test_should_raise_invalid_content_exception(self):
        invalid_content = [None, "", "<html><body></body></html>"]

        for content in invalid_content:
            with self.assertRaises(InvalidContentException):
                OctopusPlanParser(content, "test")

    def test_should_raise_parsing_exception(self):
        content_parsing_offers_failure = "Le nostre tariffe luce"

        with self.assertRaises(ParsingFailureException):
            OctopusPlanParser(content_parsing_offers_failure, "test").get_offers()

        content_parsing_button_failure = "Le nostre tariffe luce"
        with self.assertRaises(ParsingFailureException):
            OctopusPlanParser(content_parsing_button_failure, "test").get_next_page_button_url()

    def test_should_return_three_plan_offer_from_first_page(self):
        plan_offers = OctopusPlanParser(page_one_content, "test").get_offers()

        self.assertIsNotNone(plan_offers)
        self.assertEqual(3, len(plan_offers))

    def test_should_have_expected_first_page_data_for_each_plan_offer(self):
        plan_offers = OctopusPlanParser(page_one_content, "test").get_offers()

        plan_offer = plan_offers[0]
        self.assertIsNotNone(plan_offer.name, "name cannot be None")
        self.assertIsNotNone(plan_offer.commercial_cost, "cost cannot be None")
        self.assertIsNotNone(plan_offer.file_url, "file source url cannot be None")
        self.assertEqual("Octopus Fissa 12M", plan_offer.name)
        self.assertEqual(96.0, plan_offer.commercial_cost)
        self.assertRegex(plan_offer.file_url, "^http.*conditions/[Oo]cto.*[Ff]issa.*\\.pdf.*")

        plan_offer = plan_offers[1]
        self.assertIsNotNone(plan_offer.name, "name cannot be None")
        self.assertIsNotNone(plan_offer.commercial_cost, "cost cannot be None")
        self.assertIsNotNone(plan_offer.file_url, "file source url cannot be None")
        self.assertEqual("Octopus Flex", plan_offer.name)
        self.assertEqual(96.0, plan_offer.commercial_cost)
        self.assertRegex(plan_offer.file_url, "^http.*conditions/[Oo]cto.*[Ff]lex.*\\.pdf.*")

        plan_offer = plan_offers[2]
        self.assertIsNotNone(plan_offer.name, "name cannot be None")
        self.assertIsNotNone(plan_offer.commercial_cost, "cost cannot be None")
        self.assertIsNotNone(plan_offer.file_url, "file source url cannot be None")
        self.assertEqual("Octopus Flex Mono", plan_offer.name)
        self.assertEqual(96.0, plan_offer.commercial_cost)
        self.assertRegex(plan_offer.file_url, "^http.*conditions/[Oo]cto.*[Ff]lex(\\s+|%20)[Mm]ono.*\\.pdf.*")

    def test_should_be_true_if_there_is_at_least_one_offer_under_100(self):
        plan_offers= [PlanOffer(commercial_cost=100),PlanOffer(commercial_cost=99)]
        self.assertTrue(OctopusPlanParser(page_one_content, "test").should_download_all_pdfs(plan_offers))

        plan_offers= [PlanOffer(commercial_cost=55),PlanOffer(commercial_cost=101.5)]
        self.assertTrue(OctopusPlanParser(page_one_content, "test").should_download_all_pdfs(plan_offers))

    def test_should_be_false_if_offers_are_above_100(self):
        plan_offers= [PlanOffer(commercial_cost=100.5),PlanOffer(commercial_cost=101)]
        self.assertFalse(OctopusPlanParser(page_one_content, "test").should_download_all_pdfs(plan_offers))

        plan_offers= [PlanOffer(commercial_cost=100)]
        self.assertFalse(OctopusPlanParser(page_one_content, "test").should_download_all_pdfs(plan_offers))

    def test_should_return_button_url(self):
        self.assertEqual("/offerta/tariffe", OctopusPlanParser(page_one_content, "test").get_next_page_button_url())

    def test_should_return_expected_file_name(self):
        plan_offer_mock = PlanOffer(name="Test File Name 12", commercial_cost=123.0, file_url="https://test")
        regex_pattern = os.getcwd().replace('\\','/')+"/data/test_file_name_12_\\d{4}-\\d{2}-\\d{2}\\.pdf"
        self.assertRegex(plan_offer_mock.create_file_path_name(), regex_pattern)

    # @patch('extraction.parser.OctopusPlanParser._download', DownloadException("test","test error","test"))
    # def test_should_raise_download_exception(self):
    #     with self.assertRaises(DownloadException):
    #         with mock.patch('extraction.parser.OctopusPlanParser._download') as mock_download:
    #             mock_download.side_effect = DownloadException("test", "test error", "test")
    #             # OctopusPlanParser(page_one_content, "test")._download_files()
    #             with mock.patch('extraction.parser.OctopusPlanParser.get_offers') as mock_offers:
    #                 mock_offers.return_value = [PlanOffer(), PlanOffer(), PlanOffer()]
    #                 OctopusPlanParser(page_one_content, "test")._download_files()
    #
    #         # parser_mock = Mock(spec_set=OctopusPlanParser, _download=Mock(side_effect=DownloadException("test","test error","test")))
    #         # seal(parser_mock)
    #         #
    #         # OctopusPlanParser(page_one_content, "test")._download_files()

    def test_should_raise_download_exception(self):
        with self.assertRaises(DownloadException):
            plan_offer = PlanOffer(name="Test File Name 12", commercial_cost=123.0, file_url="")
            OctopusPlanParser._download(plan_offer)

    def test_should_return_three_plan_offer_from_second_page(self):
        plan_offers = DetailedOfferParser(page_two_content, "test").get_offers()

        self.assertIsNotNone(plan_offers)
        self.assertEqual(3, len(plan_offers))

    def test_should_have_expected_data_for_each_complete_plan_offer(self):
        plan_offers = DetailedOfferParser(page_two_content, "test").get_offers()

        plan_offer = plan_offers[0]
        self.assertIsNotNone(plan_offer.name, "name cannot be None")
        self.assertIsNotNone(plan_offer.commercial_cost, "cost cannot be None")
        self.assertIsNotNone(plan_offer.time_rate_type, "Timely rate type cannot be None")
        self.assertIsNotNone(plan_offer.raw_material_cost, "Raw material cost cannot be None")
        self.assertIsNotNone(plan_offer.user_type, "User type cannot be None")
        self.assertEqual("Octopus Fissa 12M", plan_offer.name)
        self.assertEqual(96.0, plan_offer.commercial_cost)
        self.assertEqual(plan_offer.time_rate_type,'monoraria')
        self.assertEqual(plan_offer.raw_material_cost, "0,1243 €/kWh")
        self.assertEqual(plan_offer.user_type,'domestiche')


        plan_offer = plan_offers[1]
        self.assertIsNotNone(plan_offer.name, "name cannot be None")
        self.assertIsNotNone(plan_offer.commercial_cost, "cost cannot be None")
        self.assertIsNotNone(plan_offer.file_url, "file source url cannot be None")
        self.assertEqual("Octopus Flex", plan_offer.name)
        self.assertEqual(96.0, plan_offer.commercial_cost)
        self.assertEqual(plan_offer.time_rate_type,'multioraria')
        self.assertEqual(plan_offer.raw_material_cost, "PUN + 0,011 €/kWh")
        self.assertEqual(plan_offer.user_type,'domestiche')

        plan_offer = plan_offers[2]
        self.assertIsNotNone(plan_offer.name, "name cannot be None")
        self.assertIsNotNone(plan_offer.commercial_cost, "cost cannot be None")
        self.assertIsNotNone(plan_offer.file_url, "file source url cannot be None")
        self.assertEqual("Octopus Flex Mono", plan_offer.name)
        self.assertEqual(96.0, plan_offer.commercial_cost)
        self.assertEqual('monoraria', plan_offer.time_rate_type)
        self.assertEqual( "PUN + 0,011 €/kWh", plan_offer.raw_material_cost)
        self.assertEqual('domestiche', plan_offer.user_type)

    # def test_json_prop_extraction(self):

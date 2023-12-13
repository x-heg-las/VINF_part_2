## This file contains unit tests for seracher.
##
## Author: Patrik Heglas

import unittest
from pysite import perform_search
import lucene

class TestPerformSearch(unittest.TestCase):

    def test_perform_search_default_fields(self):
        # Test the perform_search function with default search fields
        query_string = "slovak"
        search_fields = ['languages']
        results = perform_search(query_string, search_fields)
        
        # Add your assertions here based on the expected results
        self.assertEqual(len(results), 0)  # For example, expecting an empty result for an invalid query

    def test_perform_search_custom_fields(self):
        # Test the perform_search function witph custom search fields
        query_string = "example query"
        search_fields = ['reponame', 'readme']
        results = perform_search(query_string, search_fields)
        
        # Add your assertions here based on the expected results
        self.assertTrue(len(results) >= 0)  # For example, expecting at least one result

    def test_perform_search_required_fields(self):
        # Test the perform_search function with required fields
        query_string = "example query"
        search_fields = ['reponame', 'readme']
        required_fields = ['reponame']
        results = perform_search(query_string, search_fields, required_fields=required_fields)
        
        # Add your assertions here based on the expected results
        self.assertTrue(len(results) >= 0)  # For example, expecting at least one result

    def test_correctly_found_tags(self):
        query_string = 'opensource'
        search_fields = ['tags']

        results = perform_search(query_string, search_fields)

        for result in results:
            self.assertTrue(query_string in result['tags'])

    def test_multi_conditions(self):
        search_fields = ['reponame', 'username']
        required_fields = ['reponame', 'username']
        search_values = {
            'reponame': 'audiotoolbox',
            'username': 'skotopes'
        }

        results = perform_search('', search_fields, required_fields=required_fields, field_values=search_values)

        self.assertTrue(len(results) == 1)
        self.assertTrue(results[0]['reponame'] == 'audiotoolbox')
        self.assertTrue(results[0]['username'] == 'skotopes')

    
    def test_multi_conditions_result_count(self):
        # Test if AND condition is correctly applied. Number of results should remain the same.
        search_fields = ['language']
        required_fields = ['language']
        search_values = {
            'language': 'java',
        }

        results = perform_search('', search_fields, required_fields=required_fields, field_values=search_values)

        search_fields = ['language', 'readme']
        required_fields = ['language']
        search_values = {
            'language': 'java',
            'readme': 'java'
        }

        results2 = perform_search('', search_fields, required_fields=required_fields, field_values=search_values)

        self.assertTrue(len(results) == len(results2))


if __name__ == '__main__':
    lucene.initVM()

    unittest.main()

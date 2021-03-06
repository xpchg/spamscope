#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2016 Fedele Mantuano (https://twitter.com/fedelemantuano)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
import unittest
from mailparser import MailParser

base_path = os.path.realpath(os.path.dirname(__file__))
root = os.path.join(base_path, '..')
sample_zip = os.path.join(base_path, 'samples', 'test.zip')
sample_zip_1 = os.path.join(base_path, 'samples', 'test1.zip')
sample_txt = os.path.join(base_path, 'samples', 'test.txt')
mail = os.path.join(base_path, 'samples', 'mail_thug')
sys.path.append(root)
import src.modules.sample_parser as sp

API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


class TestSampleParser(unittest.TestCase):

    def test_static_methods(self):
        """Test static methods."""

        # Init
        filename = "test.zip"
        mail_content_type = "application/zip"
        transfer_encoding = "application/zip"

        with open(sample_zip, 'rb') as f:
            data = f.read()
            data_base64 = data.encode('base64')

        sha1_archive = "8760ff1422cf2922b649b796cfb58bfb0ccf7801"

        # Test is_archive with write_sample=False
        result1 = sp.SampleParser.is_archive(data)
        self.assertEqual(True, result1)

        result2 = sp.SampleParser.is_archive_from_base64(data_base64)
        self.assertEqual(True, result2)

        self.assertEqual(result1, result2)

        # Test fingerprints
        result1 = sp.SampleParser.fingerprints(data)[1]
        self.assertEqual(sha1_archive, result1)

        result2 = sp.SampleParser.fingerprints_from_base64(data_base64)[1]
        self.assertEqual(sha1_archive, result2)

        self.assertEqual(result1, result2)

        # Test make_attachment
        result = sp.SampleParser.make_attachment(
            data, filename, mail_content_type, transfer_encoding)

        self.assertIsInstance(result, dict)
        self.assertIn('filename', result)
        self.assertIn('extension', result)
        self.assertIn('payload', result)
        self.assertIn('mail_content_type', result)
        self.assertIn('content_transfer_encoding', result)
        self.assertIn('size', result)
        self.assertIn('is_archive', result)

        # Test add_content_type
        sp.SampleParser.add_content_type(result)
        self.assertIn('Content-Type', result)

    def test_is_archive(self):
        """Test is_archive functions."""

        with open(sample_zip, 'rb') as f:
            data = f.read()
            data_base64 = data.encode('base64')

        sha1_archive = "8760ff1422cf2922b649b796cfb58bfb0ccf7801"

        # Test is_archive with write_sample=False
        result1 = sp.SampleParser.is_archive(data)
        self.assertEqual(True, result1)

        result2 = sp.SampleParser.is_archive_from_base64(data_base64)
        self.assertEqual(True, result2)

        self.assertEqual(result1, result2)

        # Test is_archive with write_sample=True
        result = sp.SampleParser.is_archive(data, write_sample=True)
        self.assertEqual(os.path.exists(result[1]), True)

        # Sample on disk
        with open(result[1], 'rb') as f:
            data_new = f.read()

        result = sp.SampleParser.fingerprints(data_new)
        self.assertEqual(sha1_archive, result[1])

        result = sp.SampleParser.is_archive_from_base64(
            data_base64, write_sample=True)
        self.assertEqual(True, result[0])
        self.assertEqual(os.path.exists(result[1]), True)

        # Test is_archive with write_sample=True
        result = sp.SampleParser.is_archive(data, write_sample=True)
        self.assertIsInstance(result, tuple)

    def test_fingerprints(self):
        """Test fingerprints functions."""

        with open(sample_zip, 'rb') as f:
            data = f.read()
            data_base64 = data.encode('base64')

        sha1_archive = "8760ff1422cf2922b649b796cfb58bfb0ccf7801"

        # Test fingerprints
        result1 = sp.SampleParser.fingerprints(data)[1]
        self.assertEqual(sha1_archive, result1)

        result2 = sp.SampleParser.fingerprints_from_base64(data_base64)[1]
        self.assertEqual(sha1_archive, result2)

        self.assertEqual(result1, result2)

    def test_parser_sample(self):
        """Test for parse_sample."""

        parser = sp.SampleParser()

        with open(sample_zip, 'rb') as f:
            data = f.read()

        with open(sample_txt, 'rb') as f:
            data_txt_base64 = f.read().encode('base64')

        parser.parse_sample(data, "test.zip")
        result = parser.result

        md5_file = "d41d8cd98f00b204e9800998ecf8427e"
        size_file = 0
        size_zip = 166

        self.assertIsInstance(result, dict)
        self.assertEqual(result['size'], size_zip)
        self.assertIsNotNone(result['files'])
        self.assertIsInstance(result['files'], list)
        self.assertEqual(len(result['files']), 1)
        self.assertEqual(result['files'][0]['size'], size_file)
        self.assertEqual(result['files'][0]['md5'], md5_file)
        self.assertEqual(result['files'][0]['filename'], "test.txt")
        self.assertEqual(result['files'][0]['payload'], data_txt_base64)

        self.assertIn('extension', result)
        self.assertEqual(result['extension'], ".zip")
        self.assertIn('extension', result['files'][0])
        self.assertEqual(result['files'][0]['extension'], '.txt')

    def test_complete(self):
        """Test with all functions enabled. """

        # Init
        p = MailParser()
        s = sp.SampleParser(
            blacklist_content_types=[],
            thug_enabled=True,
            tika_enabled=True,
            virustotal_enabled=True,
            tika_jar="/opt/tika/tika-app-1.14.jar",
            tika_memory_allocation=None,
            tika_valid_content_types=['application/zip'],
            virustotal_api_key=API_KEY,
            thug_referer="http://www.google.com/",
            thug_extensions=[".js"],
            thug_user_agents=["winxpie80"])

        # Parsing mail
        p.parse_from_file(mail)
        attachments = []

        for i in p.attachments_list:
            s.parse_sample_from_base64(
                data=i['payload'],
                filename=i['filename'],
                mail_content_type=i['mail_content_type'],
                transfer_encoding=i['content_transfer_encoding'])
            attachments.append(s.result)

        for i in attachments:
            self.assertIn("tika", i)
            self.assertIn("virustotal", i)
            self.assertNotIn("thug", i)

            for j in i['files']:
                self.assertNotIn("tika", j)
                self.assertIn("virustotal", j)
                self.assertIn("thug", j)


if __name__ == '__main__':
    unittest.main()

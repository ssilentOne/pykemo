"""
Auxiliar functions tests module.
"""

from unittest import TestCase

from src.pykemo._aux.aux_classes import FileHashResult


class FileHashResultTest(TestCase):

    def test_1_initializes_empty_instance_correctly(self) -> None:
        filehash_res = FileHashResult.empty()

        self.assertIsNone(filehash_res.file)
        self.assertListEqual(filehash_res.posts, [])
        self.assertListEqual(filehash_res.disc, [])

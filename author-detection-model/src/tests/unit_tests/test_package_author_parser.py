import os
import unittest
from loguru import logger
from author_parser.package_author_parser import PackageParser
from llama_index.core.schema import Node, Document

class TestPackageParser(unittest.TestCase):

    maxDiff = None

    def test_get_file_list(self):
        # Given — Defines a test input
        test_dir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(test_dir, "../test_data/")

        # When — Defines what happens after a specific action
        author_parser = PackageParser()
        result = author_parser.get_file_list(path, 100, 0)

        # Then — Defines the expected result
        expected_result = [f"{path}AUTHORS", f"{path}COPYING", f"{path}file.c", f"{path}test_authors"]
        self.assertListEqual(result, expected_result)

    def test_get_nodes_from_authors(self):
        # Given — Defines a test input
        documents = [Document(text = """
                                        John Doe wrote the main program and the ABC and KEC matchers.
                                        Roberta Colon contributed the heuristics for finding fixed substrings at the end of abc.py.

                                        Henry Spencer wrote the original test suite from which grep's was derived.
                                        Mortimer Fairbank invented the Khadafy test.

                                        Jack Valdez contributed to improve abc.py. In fact
                                        it came straight from xyz with small editing and fixes.
                              """)]

        # When — Defines what happens after a specific action
        author_parser = PackageParser()
        nodes = author_parser.get_nodes(documents)
        # nodes_text = [x.text for x in nodes]
        # for index, text in enumerate(nodes_text):
        #     print(f"Node: {index} {text}\n\n")

        # Then — Defines the expected result
        self.assertEqual(len(nodes), 1)

    def test_get_nodes_from_source_file(self):
        # Given
        documents = [Document(text = """
                                       /* $Copyright: $
                                        * Copyright (c) 1996 - 2018 by Steve Baker (ice@mama.indstate.edu)
                                        * All Rights reserved
                                        *
                                        * This program is free software; you can redistribute it and/or modify
                                        * it under the terms of the GNU General Public License as published by
                                        * the Free Software Foundation; either version 2 of the License, or
                                        * (at your option) any later version.
                                        *
                                        * This program is distributed in the hope that it will be useful,
                                        * but WITHOUT ANY WARRANTY; without even the implied warranty of
                                        * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                                        * GNU General Public License for more details.
                                        *
                                        * You should have received a copy of the GNU General Public License
                                        * along with this program; if not, write to the Free Software
                                        * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
                                        */
                                        #include "tree.h"

                                        extern bool dflag, Fflag, aflag, fflag, pruneflag;
                                        extern int (*cmpfunc)();
                              """)]

        # When
        author_parser = PackageParser()
        nodes = author_parser.get_nodes(documents)

        # Then
        self.assertEqual(len(nodes), 1)


    def test_locate_interest_regions_for_single_block_comment_without_buffer(self):
        # Given
        text = """\
                    include "tree.h"
                    extern bool dflag, Fflag, aflag, fflag, pruneflag;

                    /* $Copyright: $
                    * Copyright (c) 1996 - 2018 by Steve Baker (ice@mama.indstate.edu)
                    *
                    * This program is free software; you can redistribute it and/or modify
                    */
                """
        expected_result = [(3, 7)]
        max_buffer_lines = 0

        # When
        result = PackageParser.locate_interest_regions(text, max_buffer_lines)
        logger.info(f"\n{result}")

        # Then
        self.assertListEqual(result, expected_result)


    def test_locate_interest_regions_for_single_block_comment_with_buffer(self):
        # Given
        text = """\
                    include "tree.h"
                    extern bool dflag, Fflag, aflag, fflag, pruneflag;

                    /* $Copyright: $
                    * Copyright (c) 1996 - 2018 by Steve Baker (ice@mama.indstate.edu)
                    *
                    * This program is free software; you can redistribute it and/or modify
                    */
                """
        expected_result = [(3, 9)]
        max_buffer_lines = 10

        # When
        result = PackageParser.locate_interest_regions(text, max_buffer_lines)
        logger.info(f"\n{result}")

        # Then
        self.assertListEqual(result, expected_result)


    def test_locate_interest_regions_for_mixed_comments_without_buffer(self):
        # Given
        text = """\
                    /* $Copyright: $
                    * Copyright (c) 1996 - 2018 by Steve Baker (ice@mama.indstate.edu)
                    *
                    * This program is free software; you can redistribute it and/or modify
                    */
                    #include "tree.h"
                    // Test comment

                    extern bool dflag, Fflag, aflag, fflag, pruneflag;
                    // extern int (*cmpfunc)();
                """
        expected_result = [(0, 4), (6, 6), (9, 9)]
        max_buffer_lines = 0

        # When
        result = PackageParser.locate_interest_regions(text, max_buffer_lines=max_buffer_lines)
        logger.info(f"\n{result}")

        # Then
        self.assertListEqual(result, expected_result)

    def test_locate_interest_regions_for_mixed_comments_with_buffer(self):
        # Given
        text = """\
                    /* $Copyright: $
                    * Copyright (c) 1996 - 2018 by Steve Baker (ice@mama.indstate.edu)
                    *
                    * This program is free software; you can redistribute it and/or modify
                    */
                    #include "tree.h"
                    // Test comment

                    extern bool dflag, Fflag, aflag, fflag, pruneflag;
                    // extern int (*cmpfunc)();
                """

        expected_result = [(0, 7), (9, 9)]
        max_buffer_lines = 3

        # When
        result = PackageParser.locate_interest_regions(text, max_buffer_lines=max_buffer_lines)
        logger.info(f"\n{result}")

        # Then
        self.assertListEqual(result, expected_result)


    def test_extract_interest_regions(self):
        # Given
        text = """\
                    /* $Copyright: $
                    * Copyright (c) 1996 - 2018 by Steve Baker (ice@mama.indstate.edu)
                    *
                    * This program is free software; you can redistribute it and/or modify
                    */
                    #include "tree.h"
                    // Test comment

                    extern bool dflag, Fflag, aflag, fflag, pruneflag;
                    // extern int (*cmpfunc)();
                """
        interest_regions = [(0, 7), (9, 9)]
        expected_result = """\
                    /* $Copyright: $
                    * Copyright (c) 1996 - 2018 by Steve Baker (ice@mama.indstate.edu)
                    *
                    * This program is free software; you can redistribute it and/or modify
                    */
                    #include "tree.h"
                    // Test comment

                    // extern int (*cmpfunc)();
                """

        # When
        result = PackageParser.extract_interest_regions(text, interest_regions)

        # Then
        self.assertEqual(result, expected_result)


    def test_filter_documents(self):
        # Given
        documents = [
                        Document(doc_id = "1",
                                extra_info = {"filename": "file1.c"},
                                text ="""extern bool dflag, Fflag, aflag, fflag, pruneflag;
                                            // This is a comment text"""),
                        Document(doc_id = "1",
                                extra_info = {"filename": "file2"},
                                text = "This is a plain-text document")
                    ]
        expected_result = [
                        Document(doc_id = "1",
                                extra_info = {"filename": "file1.c"},
                                text ="This is a comment text"),
                        Document(doc_id = "1",
                                extra_info = {"filename": "file2"},
                                text = "This is a plain-text document")
        ]

        # When
        result = PackageParser.filter_documents(documents)

        # Then
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()

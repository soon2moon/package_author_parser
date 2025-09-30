import os
import tempfile
import unittest
from loguru import logger
from author_parser.package_author_parser import PackageParser


from pydantic import BaseModel
from llama_index.core.schema import Node, Document

from typing import List
from glob import glob

# Ollama LLM & Embedding
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# LLamaIndex
from llama_index.core import(
        Document,
        Settings,
        VectorStoreIndex,
        SimpleDirectoryReader
        )
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import(
        TextNode, 
        NodeRelationship,
        RelatedNodeInfo
        )
from llama_index.core.ingestion import (
        IngestionPipeline, 
        IngestionCache
        )

class TestAuthorsList(unittest.TestCase):

    def setUp(self):
        class Author(BaseModel):
            id: int
            name: str

        class Authors(BaseModel):
            names: List[Author]

        # Initialize Embedding Model

        ollama_embedding = OllamaEmbedding(
            model_name="nomic-embed-text",
            base_url="http://localhost:11434"
        )

        # Global Settings for LLM and Embedding
        Settings.llm = Ollama(model="gemma2:2b",
                              request_timeout=120.0,
                              context_window=1024, # Check different sizes of context_window: default 3900 tokens
                              ).as_structured_llm(output_cls=Authors)
        Settings.embed_model = ollama_embedding

    def test_authors_list_in_one_file_temp(self):
        # Given — Defines a test input
        # (1) List of Test-Cases
        documents = [
            Document(text="""Copyright (C) 1992, 1997-2002, 2004-2021 Free Software Foundation, Inc.

            Copying and distribution of this file, with or without modification,
            are permitted in any medium without royalty provided the copyright
            notice and this notice are preserved.

            Mike Haertel wrote the main program and the dfa and kwset matchers.

            Isamu Hasegawa wrote the POSIX regular expression matcher, which is
            part of the GNU C Library and is distributed as part of GNU grep for
            use on non-GNU systems.  Ulrich Drepper, Paul Eggert, Paolo Bonzini,
            Stanislav Brabec, Assaf Gordon, Jakub Jelinek, Jim Meyering, Arnold
            Robbins, Andreas Schwab and Florian Weimer also contributed to this
            matcher.

            Arthur David Olson contributed the heuristics for finding fixed substrings
            at the end of dfa.c.

            Henry Spencer wrote the original test suite from which grep's was derived.
            Scott Anderson invented the Khadafy test.

            David MacKenzie wrote the automatic configuration software used to
            produce the configure script.

            Authors of the replacements for standard library routines are identified
            in the corresponding source files.

            The idea of using Boyer-Moore type algorithms to quickly filter out
            non-matching text before calling the regexp matcher was originally due
            to James Woods.  He also contributed some code to early versions of
            GNU grep.

            Mike Haertel would like to thank Andrew Hume for many fascinating
            discussions of string searching issues over the years.  Hume and
            Sunday's excellent paper on fast string searching describes some of
            the history of the subject, as well as providing exhaustive
            performance analysis of various implementation alternatives.
            The inner loop of GNU grep is similar to Hume & Sunday's recommended
            "Tuned Boyer Moore" inner loop.  See: Hume A, Sunday D.
            Fast string searching. Software Pract Exper. 1991;21(11):1221-48.
            https://doi.org/10.1002/spe.4380211105

            Arnold Robbins contributed to improve dfa.[ch]. In fact
            it came straight from gawk-3.0.3 with small editing and fixes.

            Many folks contributed.  See THANKS; if I omitted someone please
            send me email.

            Alain Magloire maintained GNU grep until version 2.5e.

            Bernhard "Bero" Rosenkränzer <bero@arklinux.org> maintained GNU grep until
            version 2.5.1, ie. from Sep 2001 till 2003.

            Stepan Kasal <kasal@ucw.cz> maintained GNU grep since Feb 2004.

            Tony Abou-Assaleh <taa@acm.org> maintains GNU grep since Oct 2007.

            Jim Meyering <jim@meyering.net> and Paolo Bonzini <bonzini@gnu.org>
            began maintaining GNU grep in Nov 2009.  Paolo bowed out in 2012.

            ;; Local Variables:
            ;; coding: utf-8
            ;; End:
            """)
                    ]
        # query = "Given the following text, find the names of all the persons mentioned in the text. Do not repeat the names already found. Output only the names."
        query = "Find only the names of all the persons mentioned in the text. Do not repeat the names already found."   
        
        # When — Defines what happens after a specific action
        # Use ingestion cache for efficiency
        #text_splitter = SentenceSplitter(chunk_size=2048, chunk_overlap=32)
        text_splitter = SentenceSplitter(chunk_size=64, chunk_overlap=4)
        transformations = [text_splitter]
        pipeline = IngestionPipeline(transformations=transformations)
        # ingestion_cache = IngestionCache()
        # nodes = pipeline.run(documents=documents, ingestion_cache=ingestion_cache)
        nodes = pipeline.run(documents=documents)
        index = VectorStoreIndex(nodes=nodes)
        query_engine = index.as_query_engine()

        # author_parser = PackageParser()
        # author_parser.extract_authors(query)
        response = query_engine.query(query)
        
        author_names = set([x.name for x in response.response.names])
        logger.info(f"{len(author_names)} Authors from temp case: {author_names}")
        context = [node.text for node in response.source_nodes]
        logger.info(f"Context in temp case: {context}")

        # Then — Defines the expected result
        expected_names = set([
            "Mike Haertel",
            "Isamu Hasegawa",
            "Ulrich Drepper",
            "Paul Eggert",
            "Paolo Bonzini",
            "Stanislav Brabec",
            "Assaf Gordon",
            "Jakub Jelinek",
            "Jim Meyering",
            "Arnold Robbins",
            "Andreas Schwab",
            "Florian Weimer",
            "Arthur David Olson",
            "Henry Spencer",
            "Scott Anderson",
            "David MacKenzie",
            "James Woods",
            "Andrew Hume",
            "Sunday",
            "Alain Magloire",
            "Bernhard Rosenkränzer",
            "Stepan Kasal",
            "Tony Abou-Assaleh",
        ])

        #self.assertListEqual(result, expected_authors_list)
        true_positives = author_names & expected_names
        false_positives = author_names - expected_names
        accuracy = len(true_positives) / len(expected_names)
        precision = len(true_positives) / len(author_names)
        logger.info(f"Accuracy: {accuracy} Precision: {precision}")
        # self.assertGreaterEqual(accuracy, 0.50)
        # self.assertGreaterEqual(precision, 0.50)

    def test_authors_list_in_one_file(self):
        # Given — Defines a test input
        # (1) List of Test-Cases
        contents = ["""Copyright (C) 1992, 1997-2002, 2004-2021 Free Software Foundation, Inc.

            Copying and distribution of this file, with or without modification,
            are permitted in any medium without royalty provided the copyright
            notice and this notice are preserved.

            Mike Haertel wrote the main program and the dfa and kwset matchers.

            Isamu Hasegawa wrote the POSIX regular expression matcher, which is
            part of the GNU C Library and is distributed as part of GNU grep for
            use on non-GNU systems.  Ulrich Drepper, Paul Eggert, Paolo Bonzini,
            Stanislav Brabec, Assaf Gordon, Jakub Jelinek, Jim Meyering, Arnold
            Robbins, Andreas Schwab and Florian Weimer also contributed to this
            matcher.

            Arthur David Olson contributed the heuristics for finding fixed substrings
            at the end of dfa.c.

            Henry Spencer wrote the original test suite from which grep's was derived.
            Scott Anderson invented the Khadafy test.

            David MacKenzie wrote the automatic configuration software used to
            produce the configure script.

            Authors of the replacements for standard library routines are identified
            in the corresponding source files.

            The idea of using Boyer-Moore type algorithms to quickly filter out
            non-matching text before calling the regexp matcher was originally due
            to James Woods.  He also contributed some code to early versions of
            GNU grep.

            Mike Haertel would like to thank Andrew Hume for many fascinating
            discussions of string searching issues over the years.  Hume and
            Sunday's excellent paper on fast string searching describes some of
            the history of the subject, as well as providing exhaustive
            performance analysis of various implementation alternatives.
            The inner loop of GNU grep is similar to Hume & Sunday's recommended
            "Tuned Boyer Moore" inner loop.  See: Hume A, Sunday D.
            Fast string searching. Software Pract Exper. 1991;21(11):1221-48.
            https://doi.org/10.1002/spe.4380211105

            Arnold Robbins contributed to improve dfa.[ch]. In fact
            it came straight from gawk-3.0.3 with small editing and fixes.

            Many folks contributed.  See THANKS; if I omitted someone please
            send me email.

            Alain Magloire maintained GNU grep until version 2.5e.

            Bernhard "Bero" Rosenkränzer <bero@arklinux.org> maintained GNU grep until
            version 2.5.1, ie. from Sep 2001 till 2003.

            Stepan Kasal <kasal@ucw.cz> maintained GNU grep since Feb 2004.

            Tony Abou-Assaleh <taa@acm.org> maintains GNU grep since Oct 2007.

            Jim Meyering <jim@meyering.net> and Paolo Bonzini <bonzini@gnu.org>
            began maintaining GNU grep in Nov 2009.  Paolo bowed out in 2012.

            ;; Local Variables:
            ;; coding: utf-8
            ;; End:
            """]
        tmp_file = tempfile.NamedTemporaryFile()
        with open(tmp_file.name, "w") as f:
            f.write("\n".join(contents))
        
        # query = "Given the following text, find the names of all the persons mentioned in the text. Don not repeat the names already found. Output only the names."
        query = "Find only the names of all the persons mentioned in the text. Do not repeat the names already found."
        # When — Defines what happens after a specific action
        # Use ingestion cache for efficiency
        author_parser = PackageParser()
        author_parser.set_query_string(query=query)
        response = author_parser.extract_authors(package_path=os.path.dirname(tmp_file.name))
        context = [node.text for node in response.source_nodes]
        logger.info(f"Context: {context}")

        author_names = set([x.name for x in response.response.names])
        logger.info(f"{len(author_names) }Authors: {author_names}")

        # Then — Defines the expected result
        expected_names = set([
            "Mike Haertel",
            "Isamu Hasegawa",
            "Ulrich Drepper",
            "Paul Eggert",
            "Paolo Bonzini",
            "Stanislav Brabec",
            "Assaf Gordon",
            "Jakub Jelinek",
            "Jim Meyering",
            "Arnold Robbins",
            "Andreas Schwab",
            "Florian Weimer",
            "Arthur David Olson",
            "Henry Spencer",
            "Scott Anderson",
            "David MacKenzie",
            "James Woods",
            "Andrew Hume",
            "Sunday",
            "Alain Magloire",
            "Bernhard Rosenkränzer",
            "Stepan Kasal",
            "Tony Abou-Assaleh",
        ])

        #self.assertListEqual(result, expected_authors_list)
        true_positives = author_names & expected_names
        false_positives = author_names - expected_names
        accuracy = len(true_positives) / len(expected_names)
        precision = len(true_positives) / len(author_names)

        logger.info(f"Accuracy: {accuracy} Precision: {precision}")
        # self.assertGreaterEqual(accuracy, 0.50)
        # self.assertGreaterEqual(precision, 0.50)


if __name__ == '__main__':
    unittest.main()

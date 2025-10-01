import unittest
from loguru import logger
from unittest import TestCase
from llama_index.core.schema import Document

from evaluations.core.metrics import *
from author_parser.package_author_parser import *
from evaluations.core.data_loader import load_data
from evaluations.core.results_logger import log_results

class TestContextVariationEffectsDefaultPrompt(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.category = "context-variation-effects-default-prompt"
        cls.author_parser = PackageParser(
            system_prompt_template="",  # Leerer String für Default LlamaIndex Prompt
            query="Find authors"  # Minimalistische Query
        )
        cls.eval_documents = load_data("documents")
        cls.eval_results = []

    @classmethod
    def tearDownClass(cls):
        log_results(cls.category, cls.eval_results)

    @classmethod
    def update_result(cls, test_case, doc_ids, duration, full_result, result, expected_result, score):
        result = {
            "category": cls.category,
            "eval_name": test_case,
            "llm_model_name": DEFAULT_LLM_MODEL,
            "embedding_model_name": DEFAULT_EMBEDDING_MODEL,
            "query": cls.author_parser.query,
            "prompt": cls.author_parser.query_prompt_template_str,
            "documents": doc_ids,
            "duration": duration,
            "result": result,
            "expected_result": expected_result,
            "full_result": full_result,
            "f1_score": score["f1_score"],
            "precision": score["precision"],
            "recall": score["recall"],
        }
        cls.eval_results.append(result)

    def test_extract_authors_single_plain_text_input(self):
        # Given - Identisch zu test_context_variation_effects.py
        test_doc = [doc for doc in self.eval_documents if doc["type"] == "text"][0]
        doc_ids = [test_doc["id"]]
        documents = [
            Document(id=test_doc["id"],
                    text=test_doc["text"],
                    metadata={"file_name": test_doc["file_name"], "category": "test"})
        ]
        expected_author_names = test_doc["entities"]

        # When
        result = self.author_parser.extract_authors_from_docs(documents)

        # Then
        full_result = str(result.response)
        author_names = [author.name for author in result.response.names]

        score = f1_score(author_names, expected_author_names)
        self.update_result("single-plain-text-document",
                          doc_ids,
                          self.author_parser.extract_authors_from_docs_duration,
                          full_result,
                          author_names,
                          expected_author_names,
                          score)

    def test_extract_authors_single_code_text_input(self):
        # Given - Identisch zu test_context_variation_effects.py
        test_doc = [doc for doc in self.eval_documents if doc["type"] == "code"][0]
        doc_ids = [test_doc["id"]]
        documents = [
            Document(id=test_doc["id"],
                    text=test_doc["text"],
                    metadata={"file_name": test_doc["file_name"], "category": "test"})
        ]
        expected_author_names = test_doc["entities"]

        # When
        result = self.author_parser.extract_authors_from_docs(documents)

        # Then
        full_result = str(result.response)
        author_names = [author.name for author in result.response.names]

        score = f1_score(author_names, expected_author_names)
        self.update_result("single-code-text-document",
                          doc_ids,
                          self.author_parser.extract_authors_from_docs_duration,
                          full_result,
                          author_names,
                          expected_author_names,
                          score)

    def test_four_plain_text_input(self):
        # Given - Identisch zu test_context_variation_effects.py
        test_docs = [doc for doc in self.eval_documents if doc["type"] == "text"][:4]
        doc_ids = [doc["id"] for doc in test_docs]
        documents = [
            Document(id=test_doc["id"],
                    text=test_doc["text"],
                    metadata={"file_name": test_doc["file_name"], "category": "test"})
            for test_doc in test_docs
        ]
        expected_author_names = [name for test_doc in test_docs for name in test_doc["entities"]]

        # When
        result = self.author_parser.extract_authors_from_docs(documents)

        # Then
        full_result = str(result.response)
        author_names = [author.name for author in result.response.names]

        score = f1_score(author_names, expected_author_names)
        self.update_result("four-plain-text-documents",
                          doc_ids,
                          self.author_parser.extract_authors_from_docs_duration,
                          full_result,
                          author_names,
                          expected_author_names,
                          score)

    def test_four_code_text_input(self):
        # Given - Identisch zu test_context_variation_effects.py
        test_docs = [doc for doc in self.eval_documents if doc["type"] == "code"][:4]
        doc_ids = [doc["id"] for doc in test_docs]
        documents = [
            Document(id=test_doc["id"],
                    text=test_doc["text"],
                    metadata={"file_name": test_doc["file_name"], "category": "test"})
            for test_doc in test_docs
        ]
        expected_author_names = [name for test_doc in test_docs for name in test_doc["entities"]]

        # When
        result = self.author_parser.extract_authors_from_docs(documents)

        # Then
        full_result = str(result.response)
        author_names = [author.name for author in result.response.names]

        score = f1_score(author_names, expected_author_names)
        self.update_result("four-code-text-documents",
                          doc_ids,
                          self.author_parser.extract_authors_from_docs_duration,
                          full_result,
                          author_names,
                          expected_author_names,
                          score)

    def test_four_mixed_text_input(self):
        # Given - Identisch zu test_context_variation_effects.py
        test_docs = [doc for doc in self.eval_documents if doc["type"] == "code"][:2]
        test_docs += [doc for doc in self.eval_documents if doc["type"] == "text"][:2]
        doc_ids = [doc["id"] for doc in test_docs]
        documents = [
            Document(id=test_doc["id"],
                    text=test_doc["text"],
                    metadata={"file_name": test_doc["file_name"], "category": "test"})
            for test_doc in test_docs
        ]
        expected_author_names = [name for test_doc in test_docs for name in test_doc["entities"]]

        # When
        result = self.author_parser.extract_authors_from_docs(documents)

        # Then
        full_result = str(result.response)
        author_names = [author.name for author in result.response.names]

        score = f1_score(author_names, expected_author_names)
        self.update_result("four-mixed-text-documents",
                          doc_ids,
                          self.author_parser.extract_authors_from_docs_duration,
                          full_result,
                          author_names,
                          expected_author_names,
                          score)

    def test_all_input(self):
        # Given - Identisch zu test_context_variation_effects.py
        test_docs = [doc for doc in self.eval_documents]
        doc_ids = [doc["id"] for doc in test_docs]
        documents = [
            Document(id=test_doc["id"],
                    text=test_doc["text"],
                    metadata={"file_name": test_doc["file_name"], "category": "test"})
            for test_doc in test_docs
        ]
        expected_author_names = [name for test_doc in test_docs for name in test_doc["entities"]]

        # When
        result = self.author_parser.extract_authors_from_docs(documents)

        # Then
        full_result = str(result.response)
        author_names = [author.name for author in result.response.names]

        score = f1_score(author_names, expected_author_names)
        self.update_result("all-documents",
                          doc_ids,
                          self.author_parser.extract_authors_from_docs_duration,
                          full_result,
                          author_names,
                          expected_author_names,
                          score)

if __name__ == '__main__':
    unittest.main()
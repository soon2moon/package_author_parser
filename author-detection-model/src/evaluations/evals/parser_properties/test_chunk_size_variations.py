import unittest
from typing import List
from loguru import logger
from unittest import TestCase
from unittest.mock import patch
from pydantic import BaseModel, Field
from llama_index.core.schema import Document

from evaluations.core.metrics import *
from author_parser.package_author_parser import *
from evaluations.core.data_loader import load_data
from evaluations.core.results_logger import log_results

class AuthorName(BaseModel):
    """Name of an author, maintainer, contributor or copyright holder."""
    name: str = Field(description="Name of the individual")

class AuthorsWithName(BaseModel):
    """List of Authors"""
    names: List[AuthorName] = Field(description="List of all the copyright holders, authors, maintainers, or contributors mentioned in the text")

class AuthorNameAndRole(BaseModel):
    """Name of an author, maintainer, contributor or copyright holder."""
    name: str = Field(description="Name of the individual")
    role: str = Field(description="Role of the individual. One of following: author, maintainer, contributor, or copyright holder. Default is author")

class AuthorsWithNameAndRole(BaseModel):
    names: List[AuthorNameAndRole] = Field(description="List of all the copyright holders, authors, maintainers, or contributors mentioned in the text")

class TestContextVariationEffects(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.category = "query-prompt-variation-effects"
        cls.author_parser = PackageParser()
        cls.eval_documents = load_data("documents")
        cls.eval_chunk_params = load_data("chunk_params") # [{ 'id': 'chunk_1', 'chunk_size': 512, 'chunk_overlap': 0 }, 'id': 'chunk2', 'chunk_size': 512, ...]
        cls.eval_query_prompts = load_data("query_prompts")
        cls.eval_results = []

        cls.documents = [
                                Document(
                                    id=test_doc["id"],
                                    text=test_doc["text"],
                                    metadata={"file_name": test_doc["file_name"], "category": "test"}
                                ) 
                                for test_doc in cls.eval_documents
                              ]
        cls.doc_ids = [doc["id"] for doc in cls.eval_documents]
        cls.expected_author_names = [name for test_doc in cls.eval_documents for name in test_doc["entities"]]


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
                  "chunk_size": cls.author_parser.chunk_params["chunk_size"],
                  "chunk_overlap": cls.author_parser.chunk_params["chunk_overlap"],
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


    @patch("author_parser.package_author_parser.Authors", AuthorsWithName)
    def test_chunk_size_512(self):
      # Given

      # Select the first document with type 'text' from the evaluation documents.
      test_doc = [doc for doc in self.eval_documents if doc["type"] == "text"][0]

      # Create a list containing the ID of the selected document.
      doc_ids = [test_doc["id"]]

      # Select the first chunk parameter configuration from the loaded chunk parameters.
      chunk_params = [chunk for chunk in self.eval_chunk_params][0]

      # Wrap the test document in a Document object, adding metadata for file name and category.
      documents = [
                    Document(
                        id=test_doc["id"],
                        text=test_doc["text"],
                        metadata={"file_name": test_doc["file_name"], "category": "test"}
                    )
                  ]

      # Extract the expected author names from the test document for later validation.
      expected_author_names = test_doc["entities"]

      chunk_size = self.eval_chunk_params["chunk_size"]
      chunk_params = chunk_size["chunk_overlap"]

      # self.author_parser.chunk_config = self.eval_chunk_size[0]
      self.author_parser.chunk_params = {
          "chunk_size": chunk_params["chunk_size"],
          "chunk_overlap": chunk_params["chunk_overlap"]
          }

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

    @patch("author_parser.package_author_parser.Authors", AuthorsWithName)
    def test_chunk_size_and_queries(self):
      # Given
      prompt_template_id = "Q1"
      author_parser = PackageParser()
      query_prompt = [qp for qp in self.eval_query_prompts if qp["id"] == prompt_template_id][0]
      chunk_size = self.eval_chunk_params["chunk_size"]
      author_parser = 

      # When
      author_parser.set_system_prompt_template(query_prompt)
      result = author_parser.extract_authors_from_docs(self.documents)

      # Then
      full_result = str(result.response)
      author_names = [author.name for author in result.response.names]

      score = f1_score(author_names, self.expected_author_names)
      self.update_result(query_prompt["type"],
                         author_parser,
                         prompt_template_id,
                         full_result,
                         author_names,
                         score)

if __name__ == '__main__':
    unittest.main()


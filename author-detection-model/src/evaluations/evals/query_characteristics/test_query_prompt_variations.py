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


class TestQueryPromptVariationEffects(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.category = "query-prompt-variation-effects"
        cls.eval_documents = load_data("documents")
        cls.eval_query_prompts = load_data("query_prompts")
        cls.eval_results = []

        cls.documents = [
                                Document(id=test_doc["id"],
                                          text=test_doc["text"],
                                          metadata={"file_name": test_doc["file_name"], "category": "test"}) \
                                for test_doc in cls.eval_documents
                              ]
        cls.doc_ids = [doc["id"] for doc in cls.eval_documents]
        cls.expected_author_names = [name for test_doc in cls.eval_documents for name in test_doc["entities"]]


    @classmethod
    def tearDownClass(cls):
        log_results(cls.category, cls.eval_results)


    @classmethod
    def update_result(cls, test_case, author_parser, query_prompt_template, full_result, result, score):
      result = {
                  "category": cls.category,
                  "eval_name": test_case,
                  "llm_model_name": DEFAULT_LLM_MODEL,
                  "embedding_model_name": DEFAULT_EMBEDDING_MODEL,
                  "query": author_parser.query,
                  "prompt": query_prompt_template,
                  "documents": cls.doc_ids,
                  "duration": author_parser.extract_authors_from_docs_duration,
                  "result": result,
                  "expected_result": cls.expected_author_names,
                  "full_result": full_result,
                  "f1_score": score["f1_score"],
                  "precision": score["precision"],
                  "recall": score["recall"],
                }

      cls.eval_results.append(result)


    @patch("author_parser.package_author_parser.Authors", AuthorsWithName)
    def test_extract_name(self):
      # Given
      prompt_template_id = "Q1"
      author_parser = PackageParser()
      query_prompt = [qp for qp in self.eval_query_prompts if qp["id"] == prompt_template_id][0]

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


    @patch("author_parser.package_author_parser.Authors", AuthorsWithName)
    def test_extract_name_with_context_input(self):
      # Given
      prompt_template_id = "Q2"
      author_parser = PackageParser()
      query_prompt = [qp for qp in self.eval_query_prompts if qp["id"] == prompt_template_id][0]

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


    @patch("author_parser.package_author_parser.Authors", AuthorsWithName)
    def test_extract_name_with_context_and_example_input(self):
      # Given
      prompt_template_id = "Q3"
      author_parser = PackageParser()
      query_prompt = [qp for qp in self.eval_query_prompts if qp["id"] == prompt_template_id][0]

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


    @patch("author_parser.package_author_parser.Authors", AuthorsWithNameAndRole)
    def test_extract_name_and_role_with_context_and_exmple_input(self):
      # Given
      prompt_template_id = "Q4"
      author_parser = PackageParser()
      query_prompt = [qp for qp in self.eval_query_prompts if qp["id"] == prompt_template_id][0]

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


    def test_extract_name_role_and_description_with_context_and_guideline_input(self):
      # Given
      prompt_template_id = "Q5"
      author_parser = PackageParser()
      query_prompt = [qp for qp in self.eval_query_prompts if qp["id"] == prompt_template_id][0]

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


    def test_extract_name_role_and_description_with_contex_guideline_and_example_input(self):
      # Given
      prompt_template_id = "Q6"
      author_parser = PackageParser()
      query_prompt = [qp for qp in self.eval_query_prompts if qp["id"] == prompt_template_id][0]

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


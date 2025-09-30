# Standard Library Imports
import os
import plac
from glob import glob
from typing import List
from loguru import logger

# Pydantic for Data Validation
from pydantic import BaseModel, Field
from comment_parser import comment_parser

# LlamaIndex Components
from llama_index.llms.ollama import Ollama
from llama_index.core.schema import Document
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_QA_PROMPT_TMPL
from llama_index.core.prompts import ChatMessage, ChatPromptTemplate, MessageRole

from llama_index.core import (
                                Settings,
                                PromptTemplate,
                                VectorStoreIndex,
                                SimpleDirectoryReader
                            )
from author_parser.logging_utils import store_timing

DEFAULT_LLM_MODEL = "gemma2:2b"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"

class Author(BaseModel):
    """Name of an author, maintainer, contributor or copyright holder."""

    name: str = Field(description="Name of the individual")
    role: str = Field(description="Role of the individual. One of following: author, maintainer, contributor, or copyright holder. Default is author")
    description: str = Field(description="Short information about the contribution")

class Authors(BaseModel):
    """List of Authors"""
    names: List[Author] = Field(description="List of all the copyright holders, authors, maintainers, or contributors mentioned in the text")


DEFAULT_SYSTEM_TEMPLATE = """
You are a system for finding all authors, copyright holders, maintainers or contributors information.

Your are given a text that includes information from various parts of a source code of a project.
Your task is to extract the names of all the persons that are authors, copyright holders, maintainers or contributers mentioned inside the text.

Follow these guidelines for giving out your response:
    - Response must be in separate lines.
    - Each line must contain name, role and very short description about the contribution.
    - Each name must strictly must be present inside the text and must be a valid common name of an individual or an organization.
    - Variables or flags inside the program code must not be identified as name.
    - Names must not be grouped together based on their role or contribution. Each name must be in separate line.
    - Role must be one of the following: author, maintainer, contributor, or copyright holder.
    - Description of the contribution must be understandable and less that 5 words if possible.

Do not return answers in any other format.

Example Response:
    Kendall Riley, Author, Wrote abc.py
    James Trucker, Author, code.c
    Kensley Keller, Maintainer, Maintained project ABC until 2007
"""

class PackageParser():
    """Class for extracting author information from package files using LLM"""
    def __init__(self,
                 llm_modelname=DEFAULT_LLM_MODEL,
                 embedding_modelname=DEFAULT_EMBEDDING_MODEL,
                 query=None,
                 system_prompt_template=None,
                 use_reranker=False,
                 timeout=500.0,
                 display_nodes=False,
                 display_entities=False,
                 chunk_params={"chunk_size": 512, "chunk_overlap": 0}):

        logger.info("Init PackageParser")

        self.llm_modelname = llm_modelname
        self.embedding_modelname = embedding_modelname
        self.llm_timeout = timeout
        self.use_reranker = use_reranker
        self.display_nodes = display_nodes
        self.display_entities = display_entities
        self.chunk_params = chunk_params

        logger.info("LLM: {}", llm_modelname)
        logger.info("Embedding: {}", embedding_modelname)


        self.llm = None
        self.sllm = None
        self.llm_reranker = None
        self.init_llm_modules()

        self.query = query or self.get_default_query_string()

        self.query_prompt_template_str = system_prompt_template or DEFAULT_SYSTEM_TEMPLATE
        self.query_prompt_template = self.set_system_prompt_template(self.query_prompt_template_str)


    @store_timing("init_llm_duration")
    def init_llm_modules(self):
        """Initialize LLM and embedding models."""

        self.ollama_embedding = OllamaEmbedding(
                model_name=self.embedding_modelname,
                base_url="http://localhost:11434",
                )

        # Set global settings for embedding and LLM models
        Settings.embed_model = self.ollama_embedding

        # Initialize LLM with model and timeout
        self.llm = Ollama(model=self.llm_modelname, request_timeout=self.llm_timeout)

        # Convert LLM to structured output format
        self.sllm = self.llm.as_structured_llm(output_cls=Authors)

        # Set structured LLM as global setting
        Settings.llm = self.sllm
        self.llm_reranker = LLMRerank(choice_batch_size=1, top_n=5) if self.use_reranker else None

        logger.info("LLM Initialized")
        logger.info("Embedding Model Initialized")


    @store_timing("extract_authors_duration")
    def extract_authors(self, package_path, batch_size=10, offset=0):
        """Extract author information from a given package path."""

        logger.info("Processing files")
        files = self.get_file_list(package_path, batch_size, offset)
        docs =  self.load_documents(files)
        authors = self.extract_authors_from_docs(docs)

        # self.get_display_nodes(authors.source_nodes)

        logger.info("Extraction done")
        return authors


    @store_timing("extract_authors_from_docs_duration")
    def extract_authors_from_docs(self, docs):
        nodes = self.get_nodes(docs)
        index = self.get_vector_index(nodes)
        engine = self.get_query_engine(index)
        authors = engine.query(self.query)
        return authors


    @store_timing("get_file_list_duration")
    def get_file_list(self, path, size, offset):
        """Retrieve a list of files from the given path, applying an offset and size limit."""
        recursive_path = os.path.join(path, "**")        
        files = sorted([file for file in glob(recursive_path) if os.path.isfile(file)])
        return files[offset:offset+size]


    def load_documents(self, files):
        # Load document data from the given files
        documents = SimpleDirectoryReader(input_files=files).load_data()
        filtered_documents = self.filter_documents(documents)
        return filtered_documents


    @classmethod
    def locate_interest_regions(cls, text, max_buffer_lines=20):
        comments = comment_parser.extract_comments_from_str(text)

        if len(comments) == 0:
            return []

        max_lines = len(text.splitlines())
        interest_regions = []
        line_start = None
        line_end = None
        for comment in comments:
            new_line_start = comment.line_number() - 1
            buffer_lines = max_buffer_lines + len(comment.text().splitlines()) - 1 if comment.is_multiline() else 0

            if line_end:
                if new_line_start <= line_end + 1:
                    line_end = max(new_line_start + 1, line_end)
                    line_end = min(line_end + buffer_lines, max_lines)
                    continue
                else:
                    interest_regions.append((line_start, line_end))

            line_start = new_line_start
            line_end = min(new_line_start + buffer_lines, max_lines)

        if line_start and line_end:
            interest_regions.append((line_start, line_end))

        return interest_regions


    @classmethod
    def extract_interest_regions(cls, text, interest_regions):
        filtered_lines = []
        for index, line in enumerate(text.splitlines()):
            index_in_interest_region = any([(index >= start and index <= end) for start, end in interest_regions])
            if index_in_interest_region:
                filtered_lines.append(line.strip())

        return "\n".join([line for line in filtered_lines])


    @classmethod
    def parse_interest_regions(cls, text):
        interest_regions = cls.locate_interest_regions(text)
        if not len(interest_regions):
            return ""

        return cls.extract_interest_regions(text, interest_regions)


    @classmethod
    def filter_documents(cls, documents):
        filtered_documents = []
        for doc in documents:
            try:
                filtered_content = cls.parse_interest_regions(doc.text)
            except:
                filtered_content = doc.text

            if not filtered_content:
                continue
            filtered_documents.append(Document(**{"text": filtered_content,
                                                  "doc_id": doc.id_,
                                                  "extra_info": doc.metadata}))
        return documents


    @store_timing("get_nodes_duration")
    def get_nodes(self, documents):
        """Convert files into text nodes with metadata."""
        logger.info("Creating nodes")

        logger.info("Extracting Entities from Nodes")
        text_splitter = SentenceSplitter(**self.chunk_params)

        transformations = [text_splitter]
        pipeline = IngestionPipeline(transformations=transformations)
        nodes = pipeline.run(documents=documents)

        logger.info(f"Extracted {len(nodes)} nodes.")

        return nodes

    @store_timing("get_vector_index_duration")
    def get_vector_index(self, nodes):
        """Create a vector index from text nodes."""
        logger.info("Building index")
        index = VectorStoreIndex(nodes=nodes)
        logger.info("Index created.")

        return index

    @store_timing("get_query_engine_duration")
    def get_query_engine(self, index):
        """Create a query engine from the vector index."""
        logger.info("Querying engine")
        postprocessors = []
        if self.use_reranker:
            postprocessors = [self.llm_reranker]

        query_engine = index.as_query_engine(text_qa_template=self.query_prompt_template,
                                             similarity_top_k=10,
                                             postprocessors=postprocessors)

        return query_engine


    def get_default_query_string(self):
        """Define the default query string used for extracting author information."""
        query_string = "Extract the names of all individuals that are authors, copyright holders, maintainers or contributers mentioned inside the text."
        return query_string


    def set_system_prompt_template(self, system_prompt_template):
        """Sets system query template for instructing Chat-Bot."""
        self.query_prompt_template = ChatPromptTemplate(
            message_templates=[
                ChatMessage(role=MessageRole.SYSTEM, content=system_prompt_template),
                ChatMessage(role=MessageRole.USER, content=DEFAULT_TEXT_QA_PROMPT_TMPL),
            ]
        )

def main(package_path):

    """Main function to execute the package parser and extract author information."""

    logger.info("Starting extraction")
    package_parser = PackageParser()
    authors_response = package_parser.extract_authors(package_path) 
    final_author_list = authors_response.response.names
    print("\n--- Extracted Authors ---") 
    for author in final_author_list:
        print(f"- Name: {author.name}, Role: {author.role}, Description: {author.description}")

    # Returning the list is optional now that we are printing it.
    return final_author_list
#    authors = package_parser.extract_authors(package_path)
#    return authors

if __name__ == '__main__':
    plac.call(main)

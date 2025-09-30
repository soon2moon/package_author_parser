# Run Ollama
`docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama`

# Author Detection for Open Source Code with LLMs and RAG

## Goal / Purpose

## Team

* Ufuk
* Georg
* Nils
* (Ashish, Florian)

## Compute Resources

Start with local setup

## Approach

* ollama running very small model
* retrieval augmented generation
* embedding with structured output

For example, using `langchain` or `llama_index`.

1. Apply to a single package
2. Fully scripted setup and interaction

First steps

* Access to repo (done)
* subdirectory for project (done)
* setup e.g. in gitlab ci (Nils with Ufuk)
* add example zip files (Georg)
* initial session based on an example (Nils with Ufuk)

## Example Code / Hints

Main hint: https://docs.llamaindex.ai/en/stable/examples/structured_outputs/structured_outputs/

* Example with LlamaIndex: https://docs.llamaindex.ai/en/stable/examples/citation/pdf_page_reference/
* Ollama Embeddings: https://ollama.com/blog/embedding-models
* Example with LangChain: https://python.langchain.com/docs/integrations/text_embedding/ollama/

## Test Examples



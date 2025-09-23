# AI Agent

A streamlined interface for LangChain AI agent creation with multi-modal support (text and images).

## Features

- **Simple API**: Easy-to-use interface for creating AI agents
- **Multi-modal Support**: Handle both text and image inputs seamlessly
- **LangChain Integration**: Built on top of the powerful LangChain framework
- **Flexible Models**: Support for OpenAI, Anthropic, and other LLM providers
- **Document Processing**: PDF and image processing capabilities
- **Context Management**: Advanced context engineering utilities
- **Async Support**: Both synchronous and asynchronous execution

## Installation

```bash
pip install agi-agents
```

## Quick Start

```python
from agi_agents import Agents
from langchain_openai import ChatOpenAI

# Initialize your model
llm = ChatOpenAI(model_name='gpt-4o-mini')

# Create a simple text processing chain
chain = Agents.chain_create(
    model=llm,
    text_prompt_template="Answer this question: {question}",
)

# Use the chain
response = Agents.chain_batch_generator(
    chain, 
    {"question": "What is artificial intelligence?"}
)
print(response)
```

## Multi-modal Example

```python
# Create a chain that processes both text and images
chain = Agents.chain_create(
    model=llm,
    text_prompt_template="Describe this image: {description}",
    image_prompt_template=True
)

# Process an image
base64_image = Agents.normalize_image_to_base64("path/to/image.jpg")
response = Agents.chain_batch_generator(
    chain,
    {
        "description": "What do you see?",
        "base64_image": base64_image,
        "detail_parameter": "high"
    }
)
```

## Main Classes

### Agents
The core class for creating and managing AI agents:
- `chain_create()`: Create LangChain processing chains
- `chain_batch_generator()`: Execute chains synchronously  
- `chain_stream_generator()`: Stream responses in real-time
- `continue_chain_batch_generator()`: Handle long conversations with continuation

### Contexts
Utility class for context engineering:
- `create_context_layer()`: Create context templates
- `compress_context()`: Compress contexts to fit token limits

### Document
Document processing utilities:
- `extract_text_from_pdf()`: Extract text from PDFs
- `convert_pdf_to_images()`: Convert PDFs to images
- `pdf_to_base64_images()`: Convert PDFs to base64 for LLM processing

## Requirements

- Python 3.8+
- langchain-openai
- langchain-anthropic  
- langchain-core
- PyMuPDF
- Pillow
- pillow-heif

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
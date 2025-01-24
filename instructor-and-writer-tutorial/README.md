# Using Writer and Instructor for Data Extraction

This project demonstrates how to use [Writer](https://www.writer.com?utm_source=github&utm_medium=readme&utm_campaign=api) and [Instructor](https://useinstructor.com/) to extract structured data from text and PDF files.

## Prerequisites

- Python 3.8+
- A Writer API key (follow the [Quickstart](http://dev.writer.com/api-guides/quickstart) to create an app and obtain an API key)
- Poetry (for dependency management)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd instructor-and-writer-tutorial
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file in the root directory and add your Writer.ai API key:
```
WRITER_API_KEY=your_api_key_here
```

## Project Structure

- `main.py`: Main application file containing the data extraction logic
- `example_data/`: Directory containing sample files for testing
- `out/`: Directory for output files (will be created if it doesn't exist)

## Usage

The application can process both text and PDF files. It extracts user information (first name, last name, and email) from the files and outputs the data in CSV format.

Run the application using Poetry:

```bash
poetry run python main.py
```

The application will:
1. Read files (.txt or .pdf) from the `example_data` directory
2. Extract user information using Writer.ai and Instructor
3. Generate CSV files with the extracted data

## Output

The application generates CSV files containing the extracted and repaired user information. By default, files are saved in the project root directory, but you can specify an output directory in the `main()` function.

## Documentation

Full documentation, including how to use Writer's text generation, chat completion, Knowledge Graph, and tool calling capabilities, is available at [Writer](https://dev.writer.com/api?utm_source=github&utm_medium=readme&utm_campaign=api).

## About Writer

Writer is the full-stack generative AI platform for enterprises. Quickly and easily build and deploy generative AI apps with a suite of developer tools fully integrated with our platform of LLMs, graph-based RAG tools, AI guardrails, and more. Learn more at [writer.com](https://www.writer.com?utm_source=github&utm_medium=readme&utm_campaign=api).
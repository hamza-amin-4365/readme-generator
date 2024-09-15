# README Generator

## Overview

The README Generator is a Python application designed to automatically generate comprehensive `README.md` files for GitHub repositories. It utilizes advanced language models (GPT-4 and Gemini) to analyze repository contents and produce well-structured documentation, including project descriptions, installation instructions, and usage guidelines.

## Features

- **Automatic Cloning**: Clones any specified GitHub repository to a temporary directory for analysis.
- **Content Analysis**: Reads the contents of important files in the repository to gather relevant information.
- **README Generation**: Uses state-of-the-art AI models to generate a detailed `README.md` file based on the repository�s content.
- **Multi-Model Support**: Integrates with multiple AI models (OpenAI GPT-4 and Google Gemini) for enhanced versatility.
- **Logging**: Provides informative logging for tracking the progress and troubleshooting potential issues.

## Files

- `app.py`: The main application file that handles user input, repository cloning, content reading, and README generation using GPT-4.
- `gemini.py`: A variant that uses the Gemini API to generate concise README files with rate limit handling.
- `mistral.py`: Another variant that leverages Hugging Face's Mixtral model for generating README files.
- `LICENSE`: The MIT License under which this project is distributed.

## Installation

To run the README Generator, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/hamza-amin-4365/readme-generator.git
   cd readme-generator
   ```

2. **Set Up Environment**:
   - Ensure you have Python 3.7 or later installed.
   - Install the required packages:
     ```bash
     pip install langchain_openai google-generativeai python-dotenv
     ```

3. **Set Up API Keys**:
   - Create a `.env` file in the root directory of the project with the following content:
     ```plaintext
     OPENAI_API_KEY=your_openai_api_key
     GEMINI_API_KEY=your_gemini_api_key
     huggingfacehub_api_token=your_huggingfacehub_token
     ```

## Usage

1. **Run the Application**:
   To generate a `README.md` for a specific GitHub repository, run:
   ```bash
   python app.py
   ```
   or for the Gemini version:
   ```bash
   python gemini.py <repository_url>
   ```

2. **Input the Repository URL**:
   When prompted, enter the URL of the GitHub repository you want to analyze.

3. **Generated README**:
   After successful execution, a `README.md` file will be created in the current directory with the generated content.

## Logging

The application uses the built-in `logging` module to provide insights into its operation. You can adjust the logging level in the source code if you wish to see more or less detail.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests for any improvements or additional features.

## Acknowledgments

This project utilizes the following libraries and APIs:
- [LangChain](https://langchain.com/) for AI-driven generation.
- [GitPython](https://gitpython.readthedocs.io/en/stable/) for Git repository interactions.
- [dotenv](https://pypi.org/project/python-dotenv/) for environment variable management.

## Contact

For questions or feedback, please contact [Hamza Amin](mailto:mh4070685@gmail.com).
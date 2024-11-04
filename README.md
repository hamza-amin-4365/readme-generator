# AI-Powered README Generator

## Overview

A powerful tool that automatically generates comprehensive README files for GitHub repositories using multiple AI models (OpenAI GPT-4, Google Gemini, and Mixtral-8x7B). The generator analyzes repository contents and creates well-structured documentation with project descriptions, setup instructions, and usage guidelines.

## Features
- 🤖 Multiple AI Model Support
  - OpenAI GPT-4 for high accuracy
  - Google Gemini with rate limiting for larger repos
  - Mixtral-8x7B through HuggingFace for open-source option
- 📝 Comprehensive Documentation Generation
- ⚡ Parallel Repository Processing
- 🔄 Smart Chunking for Large Codebases
- 💾 Dataset Collection for Fine-tuning

## Roadmap
- ✅ Multi-model support (OpenAI, Gemini, Mistral)
- ✅ Dataset collection and processing pipeline
- ✅ HuggingFace Hub integration for data storage
- [ ] Fine-tune starcoder-base1 model on collected dataset
- [ ] Implement chunking and parallel processing for large codebases
- [ ] Add unit tests and CI/CD pipeline
- [ ] Create web interface for easier access

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
     pip install -r requirements.txt
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
   python openai.py
   ```
   or for the Gemini version:
   ```bash
   python gemini.py <repository_url>
   ```

2. **Input the Repository URL**:
   When prompted, enter the URL of the GitHub repository you want to analyze.

3. **Generated README**:
   After successful execution, a `README.md` file will be created in the current directory with the generated content.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests for any improvements or additional features.

## Contact

For questions or feedback, please contact [Hamza Amin](mailto:mh4070685@gmail.com).


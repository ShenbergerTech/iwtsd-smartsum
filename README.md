# IWTSD Smart Summary Installation Guide

This guide provides step-by-step instructions to install and set up the IWTSD project on Windows.

## Prerequisites

Ensure you have the following installed before proceeding:

- **cuDNN**: Download and install from [NVIDIA cuDNN Downloads](https://developer.nvidia.com/cudnn-downloads).
- **CUDA 12**: Download and install from [NVIDIA CUDA 12 Download Archive](https://developer.nvidia.com/cuda-12-9-0-download-archive).
- **Python**: Download and install from [Python Downloads](https://www.python.org/downloads/).
- **Git**: Required for cloning the repository. Download from [Git Downloads](https://git-scm.com/downloads).
- **Ollama**: Required for local summarization. [Ollama Download](https://ollama.com/download).

### Environment Setup

Add the following NVIDIA library paths to your system PATH:

- `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9\bin`
- `C:\Program Files\NVIDIA\CUDNN\v9.12\bin\12.9`

## Installation Steps

1. **Clone the Repository**

   Open a command prompt and run:

   ```Command Prompt
   git clone https://github.com/ShenbergerTech/iwtsd-smartsum.git
   cd iwtsd-smartsum
   ```

2. **Install Dependencies**

   Install the required Python dependencies using `uv`:

   ```Command Prompt
   pip install uv
   uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu129
   uv add argostranslate django faster-whisper jiwer pyannote-audio transformers[torch] langchain langchain-ollama langchain-community langchain-core
   ```

3. **Set Up the Django Project**

   Navigate to the `iwtsd` directory and run the following commands:

   ```Command Prompt
   cd iwtsd
   uv run ./manage.py makemigrations
   uv run ./manage.py migrate
   uv run ./manage.py createsuperuser
   ```

   Follow the prompts to choose your own credentials for the superuser account.

4. **Load Language Models**

   Run the following command to load secondary translation language models:

   ```Command Prompt
   uv run ./manage.py load_langs
   ```

5. **Download Ollama models**

   1. From the Ollama app, click the model dropdown and enter `llama3.2`, then click the download icon.
   2. Type any text to trigger the automatic model download.


6. **Start the Development Server**

   Launch the server with:

   ```Command Prompt
   uv run ./manage.py runserver 0.0.0.0:8080
   ```

## Usage

1. Open a web browser and navigate to [http://localhost:8080/admin](http://localhost:8080/admin).
2. Log in using the credentials you created during the `createsuperuser` step.
3. Add a project.
4. Add media line items:
   - Specify titles.
   - Attach media source files.
   - Specify source languages.
5. Navigate to the **Media** section.
6. Select the item you want to process, then choose the desired processing task from the **Actions** dropdown.
7. Navigate to the Transcripts section to view the output, evaluate WER against reference material, or run Summarize or alternative Translate actions.

**Note**: The first time you process an item, the system will download the required model library from the internet. Different libraries are used depending on the source language (Hebrew or Farsi/English). Once downloaded, an internet connection is no longer required for future processing.
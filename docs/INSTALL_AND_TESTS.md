# 🚀 Installation Guide - ReqEngine

This guide provides comprehensive installation instructions for the ReqEngine intelligent requirements engineering tool.

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 12+, or Ubuntu 20.04+
- **Python**: 3.9 or higher
- **Node.js**: 18.0 or higher
- **Memory**: 8GB RAM minimum
- **Storage**: 10GB free space
- **Internet**: Required for model downloads and dependencies

### Recommended Requirements
- **Memory**: 16GB+ RAM (32GB for large documents)
- **GPU**: NVIDIA GPU with 8GB+ VRAM for optimal performance
- **Storage**: 50GB+ SSD for models and data
- **CUDA**: Version 12.1+ for GPU acceleration

## 🛠️ Prerequisites Installation

### 1. Python Installation

**Windows:**
```bash
# Download from python.org or use chocolatey
choco install python --version=3.11.0
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

### 2. Node.js Installation

**Windows:**
```bash
# Download from nodejs.org or use chocolatey
choco install nodejs --version=20.0.0
```

**macOS:**
```bash
# Using Homebrew
brew install node@20
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 3. Git Installation

**Windows:**
```bash
choco install git
```

**macOS:**
```bash
brew install git
```

**Ubuntu/Debian:**
```bash
sudo apt install git
```

## 📦 Project Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Pradyumna-Chacham/CSC510-SE-Group17.git
cd CSC510-SE-Group17/proj2
```

### Step 2: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create Python virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install PyTorch with CUDA support** (for GPU acceleration):
   ```bash
   # For CUDA 12.1 (recommended)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

   # For CPU-only installation
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

   # Install quantization support
   pip install bitsandbytes
   ```

5. **Set up Hugging Face authentication in .env:**
   ```bash
   # Get token from https://huggingface.co/settings/tokens
   export HF_TOKEN="your_huggingface_token_here"

   # On Windows
   set HF_TOKEN=your_huggingface_token_here
   ```

   NOTE:

   After obtaining your huggingface token, you must fill out this [FORM](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct) to gain access to the model. You will have to wait for approval (<20 min approx).

6. **Include Google OAuth 2.0 Credentials in .env:**

   ```bash
      #Get credentials from https://console.cloud.google.com/
      CLIENT_ID=""
      CLIENT_SECRET=""
   ```

8. **Initialize the database:**
   ```bash
   python -c "import db; db.init_db()"
   ```

### MacOS Further Instructions 

Due to hardware & CUDA constraints, please make the following 5 changes to the ```MODEL LOADING``` section
in ```main.py```. Changes are wrapped with hashtags

```bash
if not os.getenv("TESTING"):
    # --- Load LLaMA 3.2 3B Instruct ---
    token = os.getenv("HF_TOKEN")

    embedder = initializeEmbedder()

    print("Loading model with 4-bit quantization...")

    ################# (1) COMMENT OUT #####################
    # Configure 4-bit quantization for RTX 3050
    # bnb_config = BitsAndBytesConfig(
    #     load_in_4bit=True,
    #     bnb_4bit_quant_type="nf4",
    #     bnb_4bit_use_double_quant=True,
    #     bnb_4bit_compute_dtype=torch.float16,
    # )
   ####################################################

    tokenizer = initializeTokenizer(MODEL_NAME, token)

   ################# (2) COMMENT OUT #####################
    # Load model with 4-bit quantization
    # model = AutoModelForCausalLM.from_pretrained(
    #     MODEL_NAME,
    #     quantization_config=bnb_config,
    #     device_map="auto",
    #     token=token,
    #     torch_dtype=torch.float16,
    #     low_cpu_mem_usage=True,
    # )
   ##################################################

   ############# (3) ADD THIS LINE ###################
    device = "cpu"
   ##################################################

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
      ###### (4 & 5) EDIT device_map & Comment out qauntization_config ######
        # quantization_config=bnb_config,
        device_map={"": device},
      ###########################################
        token=token,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )

    ... Rest of file 
```

If after following the MacOS Instructions you still recieve errors regarding access, try running ```hf auth login```. 

### Step 3: Frontend Setup

1. **Open a new terminal and navigate to frontend:**
   ```bash
   cd proj2/frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Verify installation:**
   ```bash
   npm run lint
   npm test -- --run
   ```

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
# Activate virtual environment if not already active
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- **API Server**: http://localhost:8000
### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend application will be available at:
- **Frontend App**: http://localhost:5173

## 🧪 Running Tests

### Backend Tests

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Run test suite:**
   ```bash
   # Run all tests
   pytest

   # Run tests with coverage report
   pytest --cov=. --cov-report=html

   # Run specific test categories
   pytest -m unit          # Unit tests only
   pytest -m integration   # Integration tests only

   # Run specific test file
   pytest tests/test_main.py -v
   ```

4. **View coverage report:**
   ```bash
   # Coverage report will be generated in htmlcov/index.html
   # Open in browser to view detailed coverage
   ```

### Frontend Tests

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Run test suite:**
   ```bash
   # Run all tests
   npm test

   # Run tests with coverage
   npm run test:coverage

   # Run tests with UI interface
   npm run test:ui

   # Specific test file
   npm test -- FileUploader.test.jsx
   ```

3. **Test output:**
   - Tests run in watch mode by default
   - Coverage reports generated in `coverage/` directory
   - Results displayed in terminal with detailed output

### Test Requirements
- **Backend**: 80%+ code coverage target, 90+ test cases
- **Frontend**: 80%+ code coverage target, 100+ test cases
- **Categories**: Unit tests, integration tests, API endpoint tests




---

**Installation complete!** 🎉 You're now ready to use ReqEngine for intelligent requirements engineering.

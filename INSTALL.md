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

5. **Set up Hugging Face authentication:**
   ```bash
   # Get token from https://huggingface.co/settings/tokens
   export HF_TOKEN="your_huggingface_token_here"

   # On Windows
   set HF_TOKEN=your_huggingface_token_here
   ```

6. **Initialize the database:**
   ```bash
   python -c "import db; db.init_db()"
   ```

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
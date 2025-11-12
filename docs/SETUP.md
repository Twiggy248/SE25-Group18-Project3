# 🛠️ Setup Guide - ReqEngine

Quick setup guide for getting ReqEngine running on your system.

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Git**
- **8GB+ RAM** (16GB recommended)
- **GPU with CUDA support** (optional but recommended)

## ⚡ Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/Pradyumna-Chacham/CSC510-SE-Group17.git
cd CSC510-SE-Group17/proj2
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. GPU Support (Recommended)
```bash
# Install PyTorch with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install bitsandbytes
```

### 4. Hugging Face Authentication
```bash
# Get token from https://huggingface.co/settings/tokens
export HF_TOKEN="your_token_here"
# Windows: set HF_TOKEN=your_token_here
```

### 5. Initialize Database
```bash
python -c "import db; db.init_db()"
```

### 6. Start Backend
```bash
uvicorn main:app --reload
```
Backend runs at: http://localhost:8000

### 7. Frontend Setup (New Terminal)
```bash
cd ../frontend
npm install
npm run dev
```
Frontend runs at: http://localhost:5173

## 🧪 Verify Setup

### Test Backend
```bash
curl http://localhost:8000/health
```

### Test Frontend
Open http://localhost:5173 in your browser

### Run Tests
```bash
# Backend tests
cd backend && pytest

# Frontend tests  
cd frontend && npm test
```

## 🐛 Common Issues

### Python Virtual Environment
```bash
# If activation fails
python -m pip install --upgrade pip
python -m venv venv --clear
```

### CUDA Memory Issues
```bash
# Use CPU only if GPU issues
export CUDA_VISIBLE_DEVICES=""
```

### Port Conflicts
```bash
# Backend on different port
uvicorn main:app --port 8001

# Frontend on different port
npm run dev -- --port 3000
```

### Hugging Face Token Issues
```bash
# Login via CLI
pip install huggingface_hub[cli]
huggingface-cli login
```

## 🔧 Configuration

### Environment Variables
Create `.env` in backend directory:
```bash
HF_TOKEN=your_huggingface_token
CUDA_VISIBLE_DEVICES=0
MODEL_CACHE_DIR=./models
LOG_LEVEL=INFO
```

## 📊 Performance Tips

### For Low-End Systems
- Use CPU-only PyTorch installation
- Reduce batch sizes in model configuration
- Close other memory-intensive applications

### For High-End Systems
- Enable GPU acceleration with CUDA
- Increase worker processes: `uvicorn main:app --workers 4`
- Use SSD storage for faster model loading


For detailed installation instructions, see [INSTALL.md](INSTALL.md).
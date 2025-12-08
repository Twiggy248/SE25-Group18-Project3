## Troubleshooting

### 🚨 Common Issues and Solutions

#### **Backend Issues**

**1. Model Loading Errors**
```bash
# Problem: HuggingFace authentication failed
# Error: "Repository not found" or "Access denied"

# Solution: Set up HuggingFace token
export HF_TOKEN="your_huggingface_token_here"
# Windows: set HF_TOKEN=your_huggingface_token_here

# Verify token: 
huggingface-cli login
```

**2. CUDA/GPU Memory Issues**
```bash
# Problem: "RuntimeError: CUDA out of memory"
# Solution: Force CPU usage
export CUDA_VISIBLE_DEVICES=""

# Or reduce batch size in main.py
# max_length=1024  # Instead of 4096
```

**3. Database Lock Errors**
```bash
# Problem: "database is locked"
# Solution: Close all connections and restart
pkill -f "python main.py"
rm -f requirements.db test_requirements*.db
python main.py
```

**4. Vector Store Issues**
```bash
# Problem: ChromaDB dimension errors
# Solution: Reset vector store
rm -rf vector_store/
# Restart the application to rebuild embeddings
```

#### **Frontend Issues**

**5. Module Not Found Errors**
```bash
# Problem: "Module not found" or dependency issues
# Solution: Clean install
rm -rf node_modules package-lock.json
npm install

# Verify Node.js version (requires 18+)
node --version
```

**6. Build Failures**
```bash
# Problem: Vite build fails
# Solution: Clear cache and rebuild
npm run build --clear-cache

# Check for ESLint errors
npm run lint
```

**7. API Connection Issues**
```bash
# Problem: Frontend can't connect to backend
# Solution: Verify backend is running
curl http://localhost:8000/health

# Check CORS settings in main.py
# Ensure frontend URL is allowed
```

#### **Installation Issues**

**8. Python Version Conflicts**
```bash
# Problem: Python version incompatibility
# Solution: Use Python 3.9+
python --version  # Should show 3.9+

# Create fresh virtual environment
python -m venv fresh_venv
source fresh_venv/bin/activate  # Linux/Mac
fresh_venv\Scripts\activate      # Windows
```

**9. Dependency Conflicts**
```bash
# Problem: Package version conflicts
# Solution: Install specific versions
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**10. Port Already in Use**
```bash
# Problem: "Address already in use"
# Solution: Find and kill processes
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### 🆘 Getting Help

**Before Reporting Issues:**
1. Check this troubleshooting guide
2. Search [existing GitHub issues](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/issues)
3. Verify you're using supported versions (Python 3.9+, Node.js 18+)

**When Reporting Issues:**
- Include error messages (full stack traces)
- Specify your operating system and versions
- Provide steps to reproduce the problem
- Attach relevant log files if available

**Support Channels:**
- **GitHub Issues**: Primary support channel
- **Documentation**: See [docs/](docs/) folder for detailed guides
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development help

---

## 🆘 Support

### 📧 Contact Us

For questions, support, or collaboration inquiries, reach out to us:

**Email**: [reqenginequery@gmail.com](mailto:reqenginequery@gmail.com)

### 🔗 Additional Support Resources

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/issues)
- **💡 Feature Requests**: [GitHub Issues](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/issues)
- **� Documentation**: [Project Documentation](docs/)
- **🤝 Contributing**: [Contributing Guidelines](docs/CONTRIBUTING.md)
- **❓ Troubleshooting**: See the Troubleshooting section above

# 🤝 Contributing to ReqEngine

Thank you for your interest in contributing to **ReqEngine** - an intelligent requirements engineering tool that transforms unstructured text into structured use case specifications using LLaMA 3.2 3B.

Please note that this project is released with a [Contributor Code of Conduct](CODE-OF-CONDUCT.md). By participating in this project you agree to abide by its terms.

---

## 🚀 Quick Start for Contributors

### Getting Started
1. **Fork and clone** the repository
2. **Set up your development environment** (see [INSTALL.md](INSTALL.md))
3. **Create a feature branch** for your work
4. **Make your changes** following our coding standards
5. **Test thoroughly** before submitting
6. **Submit a pull request** with clear description

### Development Environment Setup
```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/CSC510-SE-Group17.git
cd CSC510-SE-Group17/proj2

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup (new terminal)
cd frontend
npm install
```

---

## 🐛 Issues and Pull Requests

### Reporting Issues
We'd love to hear about bugs, feature requests, or improvements! When opening an issue:

#### 🐛 Bug Reports
- **Use descriptive titles** (e.g., "Use case extraction fails for PDF files > 10MB")
- **Provide steps to reproduce** the issue
- **Include system information** (OS, Python version, Node.js version)
- **Attach relevant logs** or error messages
- **Include sample files** if the issue is file-specific

#### ✨ Feature Requests
- **Describe the problem** you're trying to solve
- **Explain your proposed solution**
- **Consider impact** on existing functionality

#### 📋 Template for Issues
```markdown
## Problem Description
Brief description of the issue or feature request.

## Steps to Reproduce (for bugs)
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen instead.

## System Information
- OS: [e.g., Windows 11, macOS 13.0, Ubuntu 22.04]
- Python: [e.g., 3.11.0]
- Node.js: [e.g., 20.0.0]
- Browser: [e.g., Chrome 118, Firefox 119]

## Additional Context
Any other context, screenshots, or files that help explain the issue.
```

---

## 🔄 Submitting Pull Requests

### Before You Start
- **Check existing issues** to avoid duplicate work
- **Open an issue first** for large changes
- **Ensure compatibility** with current architecture

### Pull Request Process

#### 1. Prepare Your Branch
```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b fix/issue-description

# For documentation
git checkout -b docs/what-you-are-documenting
```

#### 2. Make Your Changes
Follow our coding standards and ensure:
- **Code is well-documented**
- **Functions have clear docstrings**
- **Variables have descriptive names**

#### 3. Test Your Changes

See [INSTALL_AND_TESTS.md for testing instructions](./docs/INSTALL_AND_TESTS.md)

#### 4. Commit Your Changes
```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add semantic duplicate detection for use cases

- Implement sentence embedding similarity comparison
- Add unit tests for duplicate detection logic
- Update documentation

Fixes #123"
```

#### 5. Push and Create PR
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Fill out the PR template with detailed information
```

## 📋 Pull Request Checklist

Before submitting your PR, ensure:

### ✅ Code Quality
- [ ] Code follows established style guidelines
- [ ] All functions have appropriate documentation
- [ ] No commented-out code or debug statements
- [ ] Variable names are descriptive and clear

### ✅ Testing
- [ ] All existing tests pass
- [ ] New tests written for new functionality
- [ ] Test coverage meets minimum requirements
- [ ] Manual testing completed for UI changes

### ✅ Documentation
- [ ] README updated if needed
- [ ] Inline documentation added for complex logic
- [ ] Examples provided for new features

### ✅ Compatibility
- [ ] Changes work with existing functionality
- [ ] Dependencies updated in requirements files

---

## 🎯 Commit Message Guidelines

### Format
```
<type>(<scope>): <description>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Build process or auxiliary tool changes

### Examples
```bash
feat(extraction): add PDF text extraction support

- Implement PyPDF2 integration for text extraction
- Add error handling for corrupted files
- Include unit tests for extraction functions

Closes #45

fix(api): resolve memory issue in model loading

The model was not being properly managed after inference.
This fix ensures proper cleanup after each request.

Fixes #67

docs(readme): update installation instructions

- Add platform-specific commands
- Update dependency versions

test(frontend): add tests for UseCaseCard component

- Test rendering with different use case data
- Test user interactions (edit, delete, expand)
- Achieve good coverage for component
```

---

## 🌟 Recognition

### Contribution Recognition
- **All contributors** will be listed in project documentation
- **Significant contributions** will be highlighted in release notes

## 📚 Resources

### Learning Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://reactjs.org/docs/
- **Python Testing**: https://docs.pytest.org/

---

*Happy coding! 🚀*

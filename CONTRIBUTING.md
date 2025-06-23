# Contributing to PixelTwin Website Cloner

Thank you for your interest in contributing to PixelTwin Website Cloner! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites
- **Python 3.13+** for the backend
- **Node.js 18+** for the frontend
- **Git** for version control
- At least one LLM API key (OpenAI, Anthropic, or Google Gemini)

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/PixelTwinWebCloner.git
   cd PixelTwinWebCloner
   ```

2. **Backend setup:**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux
   uv pip install --requirements requirements.txt
   playwright install
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment configuration:**
   - Copy `backend/.env.example` to `backend/.env`
   - Add your LLM API keys

## Development Guidelines

### Code Style
- **Python**: Follow PEP 8 guidelines
- **TypeScript/React**: Follow standard ESLint rules
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for Python functions

### Security Considerations
- **Never commit API keys or sensitive data**
- Always use environment variables for configuration
- Review the `.gitignore` before committing
- Sanitize user input in both frontend and backend

### Testing
- Test your changes with multiple website types
- Verify both static and JavaScript-heavy sites work
- Test all three LLM providers if possible
- Check both successful clones and error cases

## Making Contributions

### Bug Reports
When reporting bugs, please include:
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots/videos if applicable
- Browser and OS information
- Console logs and error messages

### Feature Requests
For new features, please:
- Check existing issues to avoid duplicates
- Describe the use case and benefit
- Consider implementation complexity
- Discuss potential security implications

### Pull Requests

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the coding standards
   - Add/update tests as needed
   - Update documentation if required

3. **Test thoroughly:**
   ```bash
   # Backend tests
   cd backend
   python -m pytest  # If tests exist

   # Frontend tests
   cd frontend
   npm test  # If tests exist
   ```

4. **Commit with clear messages:**
   ```bash
   git commit -m "feat: add support for new website type"
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format
Use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code restructuring
- `test:` for adding tests
- `chore:` for maintenance tasks

## Areas for Contribution

### High Priority
- **Performance improvements** for large websites
- **Error handling** for edge cases
- **Support for additional website types**
- **UI/UX improvements**
- **Documentation and examples**

### Medium Priority
- **Additional LLM provider support**
- **Caching mechanisms**
- **Batch processing capabilities**
- **Export format options**

### Beginner Friendly
- **Code comments and documentation**
- **Example configurations**
- **Bug fixes for specific website types**
- **UI polish and accessibility**

## Code Review Process

1. All PRs require review before merging
2. Address reviewer feedback promptly
3. Keep PRs focused and reasonably sized
4. Ensure CI passes before requesting review
5. Update documentation for user-facing changes

## Community Guidelines

- Be respectful and constructive
- Help newcomers get started
- Share knowledge and best practices
- Focus on the technology, not personal preferences
- Follow the project's code of conduct

## Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Create an issue with the bug template
- **Feature requests**: Create an issue with the feature template
- **Security issues**: Email the maintainers privately

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make PixelTwin Website Cloner better for everyone! 🚀 
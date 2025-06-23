# Contributing to Dewata Motor

Thank you for your interest in contributing to the Dewata Motor rental management system! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- MySQL 5.7 or higher
- Git

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/DewataMotorRent.git
   cd DewataMotorRent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set Up Database**
   - Create MySQL database named `motordewata`
   - Run the database schema: `mysql -u root -p motordewata < database_schema.sql`

5. **Configure Application**
   - Update database credentials in `app.py` if needed
   - Default MySQL password in code: `Bambang0912`

## Development Guidelines

### Code Style
- Follow PEP 8 standards
- Use Black for code formatting: `black .`
- Use isort for import sorting: `isort .`
- Lint with flake8: `flake8 .`

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(auth): add password change functionality`
- `fix(ui): resolve mobile navigation toggle issue`
- `docs(readme): update installation instructions`

### Branch Naming
- `feature/feature-name` for new features
- `bugfix/issue-description` for bug fixes
- `hotfix/critical-fix` for urgent fixes
- `docs/documentation-update` for documentation

## Types of Contributions

### 🐛 Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide screenshots if UI-related
- Mention your environment details

### 💡 Feature Requests
- Use the feature request template
- Describe the problem you're solving
- Explain your proposed solution
- Consider backwards compatibility

### 🔧 Code Contributions
1. Check existing issues and PRs
2. Create an issue for major changes
3. Fork the repository
4. Create a feature branch
5. Make your changes
6. Add tests if applicable
7. Update documentation
8. Submit a pull request

### 📝 Documentation
- Update README.md for setup changes
- Add comments for complex code
- Update CHANGELOG.md for releases
- Improve inline documentation

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Writing Tests
- Write tests for new features
- Maintain existing test coverage
- Use meaningful test names
- Include edge cases

## Database Changes

### Schema Modifications
1. Create migration SQL file in format: `YYYY-MM-DD_description.sql`
2. Update `database_schema.sql` with complete schema
3. Test migration on fresh database
4. Document breaking changes

### Sample Data
- Keep sample data realistic
- Ensure data covers all use cases
- Update `database_schema.sql` with new sample data

## UI/UX Guidelines

### Design Principles
- Mobile-first responsive design
- Consistent use of Tailwind CSS
- Accessibility considerations
- Clean and intuitive interfaces

### Component Standards
- Reusable components when possible
- Consistent naming conventions
- Proper semantic HTML
- ARIA labels for accessibility

## Security Considerations

### Code Security
- Validate all user inputs
- Use parameterized queries
- Implement proper authentication
- Follow OWASP guidelines

### Data Protection
- Hash passwords properly
- Secure file uploads
- Protect against XSS/CSRF
- Implement rate limiting

## Pull Request Process

1. **Before Submitting**
   - Run tests and ensure they pass
   - Update documentation
   - Rebase on latest main branch
   - Run code formatting tools

2. **PR Description**
   - Clear title and description
   - Link related issues
   - List breaking changes
   - Include screenshots for UI changes

3. **Review Process**
   - Respond to feedback promptly
   - Make requested changes
   - Keep discussion professional
   - Be open to suggestions

## Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backwards compatible)
- Patch: Bug fixes

### Release Steps
1. Update version numbers
2. Update CHANGELOG.md
3. Create release tag
4. Generate release notes
5. Deploy to production

## Getting Help

### Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [MySQL Documentation](https://dev.mysql.com/doc/)

### Community
- Create GitHub issues for questions
- Join project discussions
- Follow project updates

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Dewata Motor! 🚗✨ 
# Contributing to Dewata Motor

Terima kasih atas minat Anda untuk berkontribusi pada sistem manajemen rental motor Dewata Motor! Dokumen ini memberikan panduan untuk berkontribusi pada proyek.

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+**
- **MySQL 5.7+**
- **Git**
- **Virtual environment** (recommended)

### Development Setup

1. **Fork dan Clone Repository**
   ```bash
   git clone https://github.com/yourusername/DewataMotorRent.git
   cd DewataMotorRent
   ```

2. **Buat Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   # Production dependencies
   pip install -r requirements.txt
   
   # Development dependencies (untuk testing dan linting)
   pip install -r requirements-dev.txt
   ```

4. **Setup Database**
   ```bash
   # Buat database MySQL
   mysql -u root -p
   CREATE DATABASE motordewata;
   exit
   
   # Import schema
   mysql -u root -p motordewata < database_schema.sql
   ```

5. **Konfigurasi Aplikasi**
   ```python
   # Update database config di app.py jika diperlukan
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_password',  # Sesuaikan
       'database': 'motordewata',
       'charset': 'utf8mb4'
   }
   ```

6. **Test Setup**
   ```bash
   python app.py
   # Akses http://localhost:5000
   # Login: superadmin / admin123
   ```

## 📝 Development Guidelines

### Code Style dan Standards

#### Python Code Style
- **Follow PEP 8** standards
- **Gunakan Black** untuk formatting: `black .`
- **Gunakan isort** untuk import sorting: `isort .`
- **Lint dengan flake8**: `flake8 .`

```bash
# Format code sebelum commit
black app.py
isort app.py
flake8 app.py
```

#### Template dan Frontend
- **Tailwind CSS** untuk styling (gunakan utility classes)
- **Responsive design** - mobile-first approach
- **Semantic HTML** untuk accessibility
- **Consistent naming** untuk CSS classes

#### Database
- **Gunakan parameterized queries** untuk mencegah SQL injection
- **Follow naming convention**: snake_case untuk table dan column
- **Add proper indexes** untuk performance
- **Document schema changes** di migration files

### Commit Message Convention

Gunakan **Conventional Commits** format:

```
type(scope): description

[optional body]

[optional footer]
```

#### Types:
- `feat`: Fitur baru
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding atau updating tests
- `chore`: Maintenance tasks

#### Examples:
```bash
feat(auth): add password strength validation
fix(ui): resolve mobile navigation toggle issue
docs(readme): update installation instructions
style(app): format code with black
refactor(db): optimize motor query performance
test(auth): add login rate limiting tests
chore(deps): update Flask to 2.3.3
```

### Branch Naming Convention
- `feature/feature-name` - Fitur baru
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-fix` - Urgent fixes
- `docs/documentation-update` - Documentation
- `refactor/component-name` - Refactoring

Example: `feature/motor-export-pdf`, `bugfix/login-rate-limit`

## 🤝 Types of Contributions

### 🐛 Bug Reports
1. **Check existing issues** terlebih dahulu
2. **Gunakan bug report template**
3. **Include steps to reproduce**
4. **Provide screenshots** untuk UI issues
5. **Mention environment details** (OS, Python version, browser)

**Template Bug Report:**
```markdown
**Bug Description**
Brief description of the issue

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python: [e.g. 3.8.10]
- Browser: [e.g. Chrome 96.0]
- MySQL: [e.g. 8.0.27]

**Screenshots**
Add screenshots if applicable
```

### 💡 Feature Requests
1. **Describe the problem** yang ingin diselesaikan
2. **Explain proposed solution** dengan detail
3. **Consider backwards compatibility**
4. **Provide mockups** untuk UI changes

### 🔧 Code Contributions

#### Before Starting
1. **Check existing issues** dan PRs
2. **Create issue** untuk major changes
3. **Discuss approach** dengan maintainers
4. **Fork repository** dan create branch

#### Development Process
1. **Write clean, readable code**
2. **Add comments** untuk complex logic
3. **Follow security best practices**
4. **Test your changes** thoroughly
5. **Update documentation** jika diperlukan

#### Code Review Checklist
- [ ] Code follows project style guidelines
- [ ] No hardcoded credentials atau sensitive data
- [ ] Proper error handling implemented
- [ ] Input validation dan sanitization
- [ ] Security considerations addressed
- [ ] Performance impact considered
- [ ] Documentation updated
- [ ] Tests added/updated (if applicable)

### 📚 Documentation Contributions
- **Update README.md** untuk setup changes
- **Add inline comments** untuk complex code
- **Update CHANGELOG.md** untuk releases
- **Improve user guide** dan tutorials
- **Translate documentation** ke bahasa lain

## 🧪 Testing

### Manual Testing
```bash
# Test basic functionality
1. Login sebagai superadmin
2. Create admin account
3. Login sebagai admin
4. Add, edit, delete motor
5. Upload dan manage images
6. Test responsive design di berbagai device
```

### Testing Guidelines
- **Test all user roles** (superadmin, admin)
- **Test form validations** dan error handling
- **Test file upload** dengan berbagai format
- **Test responsive design** di mobile/tablet/desktop
- **Test database operations** (CRUD)
- **Test security features** (rate limiting, etc.)

### Automated Testing (Future)
```bash
# Ketika tests sudah tersedia
pytest
pytest --cov=app  # dengan coverage
```

## 🔐 Security Guidelines

### Code Security
- **Validate all user inputs** dengan proper sanitization
- **Use parameterized queries** untuk database operations
- **Implement proper authentication** dan authorization
- **Follow OWASP guidelines** untuk web security
- **No hardcoded secrets** atau credentials

### File Upload Security
- **Validate file types** dan extensions
- **Check file size limits**
- **Sanitize filenames**
- **Process images** untuk remove metadata
- **Store uploads** di secure location

### Database Security
- **Use strong passwords** untuk database users
- **Implement proper access controls**
- **Regular backup** strategies
- **Monitor for suspicious activities**

## 📊 Database Changes

### Schema Modifications
1. **Create migration file**: `migrations/YYYY-MM-DD_description.sql`
2. **Update `database_schema.sql`** dengan complete schema
3. **Test migration** pada fresh database
4. **Document breaking changes** di CHANGELOG.md

### Sample Data Updates
- **Keep realistic data** yang representative
- **Ensure data covers** semua use cases
- **Update documentation** jika sample data berubah
- **Maintain data consistency** across tables

## 🎨 UI/UX Guidelines

### Design Principles
- **Mobile-first** responsive design
- **Consistent** use of Tailwind CSS utility classes
- **Accessibility** considerations (ARIA labels, keyboard navigation)
- **Clean and intuitive** interfaces
- **Performance optimized** images dan assets

### Component Standards
- **Reusable components** when possible
- **Consistent naming** conventions
- **Proper semantic HTML** structure
- **WCAG compliance** untuk accessibility
- **Cross-browser compatibility**

### Color Palette
```css
/* Primary Colors */
bg-blue-600    /* Primary button, links */
bg-blue-700    /* Primary hover states */

/* Secondary Colors */
bg-gray-100    /* Light backgrounds */
bg-gray-800    /* Dark text, headers */

/* Status Colors */
bg-green-500   /* Success states */
bg-red-500     /* Error states */
bg-yellow-500  /* Warning states */
```

## 🚀 Pull Request Process

### Before Submitting
- [ ] **Rebase on latest main** branch
- [ ] **Run tests** dan ensure they pass
- [ ] **Format code** dengan Black dan isort
- [ ] **Update documentation** jika diperlukan
- [ ] **Check for linting errors**

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## How Has This Been Tested?
Describe testing steps

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process
1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Address feedback** promptly
4. **Final approval** dan merge

## 📈 Release Process

### Version Numbering
Menggunakan [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH**
- **Major**: Breaking changes
- **Minor**: New features (backwards compatible)
- **Patch**: Bug fixes

### Release Steps
1. **Update version numbers** di relevant files
2. **Update CHANGELOG.md** dengan changes
3. **Create release tag**: `git tag -a v2.1.0 -m "Release v2.1.0"`
4. **Generate release notes**
5. **Deploy to production** (if applicable)

## 🆘 Getting Help

### Resources
- **[Flask Documentation](https://flask.palletsprojects.com/)**
- **[Tailwind CSS Documentation](https://tailwindcss.com/docs)**
- **[MySQL Documentation](https://dev.mysql.com/doc/)**
- **[Python Security Guidelines](https://python-security.readthedocs.io/)**

### Communication
- **GitHub Issues** untuk bug reports dan feature requests
- **GitHub Discussions** untuk general questions
- **Pull Request comments** untuk code-specific discussions

### Development Tips
- **Start small** dengan minor improvements
- **Ask questions** jika tidak yakin dengan approach
- **Follow existing patterns** di codebase
- **Write clear commit messages**
- **Document your reasoning** untuk complex changes

## 🙏 Recognition

Kontributor akan diakui dalam:
- **README.md** contributors section
- **CHANGELOG.md** untuk specific contributions
- **Release notes** untuk major contributions

---

**Terima kasih telah berkontribusi pada Dewata Motor! 🏍️**

> 💡 **Tips**: Start dengan issue yang dilabel `good first issue` untuk contribusi pertama Anda. 
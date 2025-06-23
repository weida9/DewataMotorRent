@echo off
echo 🏍️ Setting up Dewata Motor Git Repository...

REM Initialize git if not already initialized
if not exist ".git" (
    echo 📦 Initializing Git repository...
    git init
) else (
    echo ✅ Git repository already initialized
)

REM Add all files
echo 📁 Adding files to staging area...
git add .

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "feat: initial commit - complete dewata motor rental system - Add Flask web application with session authentication - Implement role-based access control (superadmin/admin) - Add motor management with image upload - Create responsive UI with Tailwind CSS - Include password management features - Add comprehensive database schema with sample data - Include project documentation and contribution guidelines"

REM Set main branch
echo 🌿 Setting main branch...
git branch -M main

echo.
echo 🎉 Git repository setup complete!
echo.
echo Next steps:
echo 1. Create a new repository on GitHub
echo 2. Copy the repository URL
echo 3. Run: git remote add origin ^<your-repo-url^>
echo 4. Run: git push -u origin main
echo.
echo Example:
echo git remote add origin https://github.com/yourusername/DewataMotorRent.git
echo git push -u origin main
echo.
echo 📚 Don't forget to:
echo - Update database credentials in app.py for production
echo - Set up environment variables for sensitive data
echo - Configure proper deployment settings
echo.
echo Happy coding! 🚀
pause 
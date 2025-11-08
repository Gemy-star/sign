@echo off
REM Quick development commands for Windows

echo 🚀 Django Development Helper
echo ==============================
echo.

if "%1"=="" goto usage
if "%1"=="run" goto run
if "%1"=="server" goto run
if "%1"=="migrate" goto migrate
if "%1"=="makemigrations" goto makemigrations
if "%1"=="shell" goto shell
if "%1"=="createsuperuser" goto createsuperuser
if "%1"=="test" goto test
if "%1"=="cache" goto cache
if "%1"=="check" goto check
goto usage

:run
echo Starting development server...
poetry run python manage.py runserver
goto end

:migrate
echo Running migrations...
poetry run python manage.py migrate
goto end

:makemigrations
echo Creating migrations...
poetry run python manage.py makemigrations
goto end

:shell
echo Opening Django shell...
poetry run python manage.py shell
goto end

:createsuperuser
echo Creating superuser...
poetry run python manage.py createsuperuser
goto end

:test
echo Running tests...
poetry run python manage.py test
goto end

:cache
echo Checking cache setup...
poetry run python manage.py setup_cache
goto end

:check
echo Checking project...
poetry run python manage.py check
goto end

:usage
echo Usage: dev.bat [command]
echo.
echo Available commands:
echo   run, server       - Start development server
echo   migrate           - Run database migrations
echo   makemigrations    - Create new migrations
echo   shell             - Open Django shell
echo   createsuperuser   - Create admin user
echo   test              - Run tests
echo   cache             - Check cache setup
echo   check             - Check project for issues
echo.
echo Or use directly:
echo   poetry run python manage.py [command]
goto end

:end

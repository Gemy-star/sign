#!/usr/bin/env bash
# Quick development commands

echo "🚀 Django Development Helper"
echo "=============================="
echo ""

case "$1" in
    "run"|"server")
        echo "Starting development server..."
        poetry run python manage.py runserver
        ;;
    "migrate")
        echo "Running migrations..."
        poetry run python manage.py migrate
        ;;
    "makemigrations")
        echo "Creating migrations..."
        poetry run python manage.py makemigrations
        ;;
    "shell")
        echo "Opening Django shell..."
        poetry run python manage.py shell
        ;;
    "createsuperuser")
        echo "Creating superuser..."
        poetry run python manage.py createsuperuser
        ;;
    "test")
        echo "Running tests..."
        poetry run python manage.py test
        ;;
    "cache")
        echo "Checking cache setup..."
        poetry run python manage.py setup_cache
        ;;
    "check")
        echo "Checking project..."
        poetry run python manage.py check
        ;;
    *)
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Available commands:"
        echo "  run, server       - Start development server"
        echo "  migrate           - Run database migrations"
        echo "  makemigrations    - Create new migrations"
        echo "  shell             - Open Django shell"
        echo "  createsuperuser   - Create admin user"
        echo "  test              - Run tests"
        echo "  cache             - Check cache setup"
        echo "  check             - Check project for issues"
        echo ""
        echo "Or use directly:"
        echo "  poetry run python manage.py [command]"
        ;;
esac

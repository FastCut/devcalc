#!/usr/bin/env python3
"""
Punkt wejścia do aplikacji Kalkulator Opłacalności Deweloperskiej.

Uruchom aplikację: python run.py
"""

import os
from app import create_app, db
from app.models import User, Project, Calculation, CostDatabase

# Utwórz instancję aplikacji
app = create_app()

# Shell context - dostęp do modeli w Flask shell
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Project': Project,
        'Calculation': Calculation,
        'CostDatabase': CostDatabase
    }

# Dodatkowe komendy CLI
@app.cli.command()
def init_db():
    """Inicjalizuje bazę danych i dodaje domyślne koszty."""
    db.create_all()
    if CostDatabase.query.count() == 0:
        CostDatabase.init_default_costs()
        print("✓ Baza danych zainicjalizowana z domyślnymi kosztami.")
    else:
        print("✓ Baza danych już istnieje.")

@app.cli.command()
def create_admin():
    """Tworzy testowe konto administratora."""
    username = input("Nazwa użytkownika [admin]: ") or "admin"
    email = input("Email [admin@example.com]: ") or "admin@example.com"
    password = input("Hasło [admin123]: ") or "admin123"

    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"✗ Użytkownik '{username}' już istnieje.")
        return

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    print(f"✓ Utworzono użytkownika: {username} / {email}")

if __name__ == '__main__':
    # Sprawdzenie czy istnieje .env
    if not os.path.exists('.env'):
        print("⚠ Plik .env nie istnieje. Kopiuję z .env.example...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✓ Plik .env utworzony. Możesz edytować konfigurację.")
        else:
            print("⚠ Brak pliku .env.example. Używam domyślnej konfiguracji.")

    # Uruchomienie aplikacji
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

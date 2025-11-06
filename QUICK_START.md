# 🚀 Quick Start - Kalkulator Opłacalności Deweloperskiej

## Szybkie Uruchomienie

```bash
# 1. Instalacja
pip install -r requirements.txt

# 2. Inicjalizacja bazy danych
python3 -c "
from app import create_app, db
from app.models import CostDatabase
app = create_app()
with app.app_context():
    db.create_all()
    if CostDatabase.query.count() == 0:
        CostDatabase.init_default_costs()
"

# 3. Utworzenie użytkownika
python3 -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    user = User(username='admin', email='admin@example.com')
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    print('Użytkownik: admin / admin123')
"

# 4. Uruchomienie
python3 run.py
```

## Dostęp

**URL:** http://localhost:5000  
**Login:** admin  
**Hasło:** admin123

## Główne Funkcje

- ✅ **NPV & IRR** - pełna analiza opłacalności
- ✅ **Cash Flow** - miesięczny harmonogram przepływów
- ✅ **Kredyt** - symulacja kosztów finansowania
- ✅ **Analiza wrażliwości** - testowanie scenariuszy
- ✅ **Baza kosztów** - edytowalne koszty jednostkowe

## Struktura

```
devcalc/
├── app/
│   ├── financial_engine.py    # Logika NPV/IRR
│   ├── models.py               # Modele DB
│   ├── auth/                   # Uwierzytelnianie
│   ├── calculator/             # Kalkulator
│   ├── costs/                  # Baza kosztów
│   └── templates/              # UI
├── run.py                      # Start aplikacji
├── config.py                   # Konfiguracja
└── README.md                   # Pełna dokumentacja
```

## Wsparcie

📖 Pełna dokumentacja: [README.md](README.md)  
🐛 Problemy: Sprawdź sekcję "Rozwiązywanie Problemów" w README

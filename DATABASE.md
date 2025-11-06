# 📊 Baza Danych - Dokumentacja

## Lokalizacja i Typ

**Plik:** `instance/devcalc.db`
**Typ:** SQLite 3
**Status Git:** ✅ **IGNOROWANY** (nie commitowany do repozytorium)

## ⚠️ Ważne Informacje

### Dlaczego baza NIE jest w repozytorium?

Baza danych zawiera:
- **Dane użytkowników** (hashe haseł, emaile)
- **Projekty deweloperskie** (dane finansowe)
- **Sesje użytkowników**

❌ **NIE należy** commitować bazy danych do Git, ponieważ:
1. Zawiera wrażliwe dane
2. Jest unikalna dla każdego wdrożenia
3. Może rosnąć do dużych rozmiarów
4. Może zawierać dane testowe

✅ **Prawidłowa konfiguracja:**
```gitignore
# .gitignore
instance/         # Cały katalog instance
*.db              # Wszystkie pliki .db
*.sqlite          # Wszystkie pliki SQLite
.env              # Konfiguracja środowiska
```

## 📋 Schemat Bazy Danych

### 1. Tabela: `users`
Przechowuje dane użytkowników.

| Kolumna | Typ | Opis |
|---------|-----|------|
| `id` | INTEGER | Klucz główny |
| `username` | VARCHAR(80) | Nazwa użytkownika (unikalna) |
| `email` | VARCHAR(120) | Email (unikalny) |
| `password_hash` | VARCHAR(255) | Zahashowane hasło (PBKDF2) |
| `created_at` | DATETIME | Data utworzenia konta |
| `is_active` | BOOLEAN | Czy konto jest aktywne |

**Relacje:**
- `projects` - jeden użytkownik → wiele projektów

### 2. Tabela: `cost_database`
Edytowalna baza kosztów jednostkowych.

| Kolumna | Typ | Opis |
|---------|-----|------|
| `id` | INTEGER | Klucz główny |
| `category` | VARCHAR(50) | Kategoria (acquisition, construction, etc.) |
| `name` | VARCHAR(100) | Nazwa kosztu |
| `unit` | VARCHAR(20) | Jednostka (PLN/m², PLN, %) |
| `default_value` | FLOAT | Wartość domyślna |
| `min_value` | FLOAT | Wartość minimalna (opcjonalna) |
| `max_value` | FLOAT | Wartość maksymalna (opcjonalna) |
| `description` | TEXT | Opis |
| `created_at` | DATETIME | Data utworzenia |
| `updated_at` | DATETIME | Data ostatniej modyfikacji |

**Kategorie:**
- `acquisition` - Koszty pozyskania
- `construction` - Koszty budowy
- `design` - Koszty projektowe
- `infrastructure` - Infrastruktura
- `overhead` - Zarządzanie i overhead
- `sales` - Marketing i sprzedaż

**Domyślne koszty:** 15 pozycji

### 3. Tabela: `projects`
Projekty deweloperskie użytkowników.

| Kolumna | Typ | Opis |
|---------|-----|------|
| `id` | INTEGER | Klucz główny |
| `user_id` | INTEGER | FK → users.id |
| `name` | VARCHAR(200) | Nazwa projektu |
| `created_at` | DATETIME | Data utworzenia |
| `updated_at` | DATETIME | Data ostatniej modyfikacji |
| **Dane działki** |
| `plot_area` | FLOAT | Powierzchnia działki (m²) |
| `plot_price_per_sqm` | FLOAT | Cena zakupu (PLN/m²) |
| **Dane budynku** |
| `pum_area` | FLOAT | Powierzchnia użytkowa mieszkań (m²) |
| `units_count` | INTEGER | Liczba lokali |
| `sale_price_per_sqm` | FLOAT | Cena sprzedaży (PLN/m²) |
| `parking_revenue` | FLOAT | Przychód z parkingów (PLN) |
| **Harmonogram** |
| `preparation_months` | INTEGER | Faza przygotowania (miesiące) |
| `construction_months` | INTEGER | Faza budowy (miesiące) |
| `sales_months` | INTEGER | Faza sprzedaży (miesiące) |
| **Parametry finansowe** |
| `discount_rate` | FLOAT | Stopa dyskonta (%) |
| `expected_margin` | FLOAT | Oczekiwana marża (%) |
| `tax_rate` | FLOAT | Stawka podatku (%) |
| **Kredyt** |
| `loan_percentage` | FLOAT | Udział kredytu (%) |
| `loan_interest_rate` | FLOAT | Oprocentowanie (%) |
| `loan_provision` | FLOAT | Prowizja (%) |
| `loan_months` | INTEGER | Liczba rat |

**Relacje:**
- `owner` - wiele projektów → jeden użytkownik
- `calculations` - jeden projekt → wiele kalkulacji

### 4. Tabela: `calculations`
Wyniki obliczeń dla projektów.

| Kolumna | Typ | Opis |
|---------|-----|------|
| `id` | INTEGER | Klucz główny |
| `project_id` | INTEGER | FK → projects.id |
| `created_at` | DATETIME | Data kalkulacji |
| `scenario` | VARCHAR(50) | Scenariusz (base, optimistic, pessimistic) |
| **Wyniki finansowe** |
| `total_revenue` | FLOAT | Całkowite przychody (PLN) |
| `total_costs` | FLOAT | Całkowite koszty (PLN) |
| `gross_margin` | FLOAT | Marża brutto (PLN) |
| `npv` | FLOAT | Net Present Value (PLN) |
| `irr` | FLOAT | Internal Rate of Return (%) |
| `required_price_per_sqm` | FLOAT | Wymagana cena sprzedaży (PLN/m²) |
| **Cash Flow (JSON)** |
| `cash_flow_data` | TEXT | JSON z miesięcznym cash flow |

**Relacje:**
- `project` - wiele kalkulacji → jeden projekt

## 📝 Format JSON - Cash Flow

Pole `cash_flow_data` przechowuje JSON z miesięcznym harmonogramem:

```json
[
  {
    "month": 0,
    "phase": "preparation",
    "revenues": 0.0,
    "costs": 150000.0,
    "net_cash_flow": -150000.0,
    "cumulative_cash_flow": -150000.0
  },
  {
    "month": 1,
    "phase": "preparation",
    "revenues": 0.0,
    "costs": 120000.0,
    "net_cash_flow": -120000.0,
    "cumulative_cash_flow": -270000.0
  },
  ...
]
```

**Fazy:**
- `preparation` - Przygotowanie (żółty na wykresach)
- `construction` - Budowa (niebieski)
- `sales` - Sprzedaż (zielony)

## 🔧 Operacje na Bazie Danych

### Inicjalizacja (pierwsze uruchomienie)

```bash
python3 -c "
from app import create_app, db
from app.models import CostDatabase

app = create_app()
with app.app_context():
    db.create_all()
    if CostDatabase.query.count() == 0:
        CostDatabase.init_default_costs()
        print('✓ Baza zainicjalizowana')
"
```

### Utworzenie użytkownika

```bash
python3 -c "
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User(username='admin', email='admin@example.com')
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    print('✓ Użytkownik utworzony')
"
```

### Backup bazy danych

```bash
# Kopia zapasowa
cp instance/devcalc.db instance/devcalc_backup_$(date +%Y%m%d).db

# Przywracanie
cp instance/devcalc_backup_20250106.db instance/devcalc.db
```

### Reset bazy danych (UWAGA: Usuwa wszystkie dane!)

```bash
rm instance/devcalc.db
python3 -c "
from app import create_app, db
from app.models import CostDatabase

app = create_app()
with app.app_context():
    db.create_all()
    CostDatabase.init_default_costs()
    print('✓ Baza zresetowana')
"
```

## 📊 Statystyki

Sprawdzenie zawartości bazy:

```bash
python3 -c "
from app import create_app, db
from app.models import User, CostDatabase, Project, Calculation

app = create_app()
with app.app_context():
    print(f'Użytkownicy: {User.query.count()}')
    print(f'Koszty: {CostDatabase.query.count()}')
    print(f'Projekty: {Project.query.count()}')
    print(f'Kalkulacje: {Calculation.query.count()}')
"
```

## 🚀 Migracja do PostgreSQL (Produkcja)

### 1. Instalacja PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Instalacja adaptera Python
pip install psycopg2-binary
```

### 2. Utworzenie bazy danych

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE devcalc;
CREATE USER devcalc_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE devcalc TO devcalc_user;
\q
```

### 3. Aktualizacja konfiguracji

W pliku `.env`:

```
DATABASE_URL=postgresql://devcalc_user:secure_password@localhost/devcalc
```

### 4. Migracja danych (opcjonalnie)

Jeśli chcesz przenieść dane z SQLite do PostgreSQL:

```bash
pip install sqlalchemy-migrate

# Export z SQLite
python3 -c "
from app import create_app, db
from app.models import User, CostDatabase, Project, Calculation
import json

app = create_app()
with app.app_context():
    # Export użytkowników
    users = User.query.all()
    # ... kod exportu
"

# Import do PostgreSQL
# ... analogiczny kod z DATABASE_URL wskazującym na PostgreSQL
```

## 🔐 Bezpieczeństwo

### Hasła
- Algorytm: **PBKDF2** (Werkzeug)
- Salt: Automatyczny, unikalny dla każdego hasła
- Iteracje: Domyślnie wysokie (bezpieczne)

### Przykład hashowania

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hashowanie
hashed = generate_password_hash('mypassword')
# Zwraca: pbkdf2:sha256:260000$abc123...$def456...

# Weryfikacja
is_valid = check_password_hash(hashed, 'mypassword')  # True
```

### Sesje
- Flask-Login zarządza sesjami
- Cookie session - podpisany SECRET_KEY
- Remember Me - opcjonalny persistent cookie (7 dni)

## 📖 Dodatkowe Informacje

### Indeksy
Automatyczne indeksy na:
- `users.username` (UNIQUE)
- `users.email` (UNIQUE)
- `cost_database.category`
- `projects.user_id` (FK)
- `calculations.project_id` (FK)

### Kaskadowe usuwanie
- Usunięcie użytkownika → usuwa wszystkie jego projekty
- Usunięcie projektu → usuwa wszystkie jego kalkulacje

### Limity
SQLite:
- Max rozmiar bazy: 281 TB (praktycznie bez limitu)
- Max liczba kolumn: 2000
- Max rozmiar wiersza: 1 GB

---

**Ostatnia aktualizacja:** 2025-11-06

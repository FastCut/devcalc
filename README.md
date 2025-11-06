# Kalkulator Opłacalności Deweloperskiej

Profesjonalna aplikacja webowa do analizy opłacalności projektów deweloperskich, wykorzystująca metodologie **NPV** (Net Present Value) i **IRR** (Internal Rate of Return).

## 🎯 Funkcje

### ✓ Kompleksowa Analiza Finansowa
- **NPV (Wartość Bieżąca Netto)** - zdyskontowana wartość przepływów pieniężnych
- **IRR (Wewnętrzna Stopa Zwrotu)** - rentowność projektu w skali procentowej
- **Analiza Cash Flow** - miesięczne przepływy pieniężne z podziałem na fazy
- **Szczegółowy rozkład kosztów** - wszystkie kategorie kosztów deweloperskich

### ✓ Zaawansowane Możliwości
- **Analiza wrażliwości** - wpływ zmian kluczowych parametrów na opłacalność
- **Scenariusze opłacalności** - testowanie różnych wariantów projektu
- **Kalkulacja kredytu** - pełna symulacja kosztów finansowania zewnętrznego
- **Edytowalna baza kosztów** - dostosowanie jednostkowych kosztów do rynku

### ✓ Interfejs Użytkownika
- **Bezpieczne logowanie** - system uwierzytelniania użytkowników
- **Responsywny design** - działa na PC, tablecie i smartfonie (Bootstrap 5)
- **Interaktywne wykresy** - wizualizacja cash flow i analiz (Chart.js)
- **Wyróżnione pola wejściowe** - żółte tło dla kluczowych danych

## 🏗️ Architektura

### Stos Technologiczny

**Backend:**
- **Python 3.8+** - język programowania
- **Flask 3.0** - framework webowy
- **SQLAlchemy** - ORM do bazy danych
- **NumPy-Financial** - precyzyjne obliczenia finansowe (NPV, IRR, PMT)

**Frontend:**
- **HTML5 + Bootstrap 5** - responsywny interfejs
- **Chart.js 4.4** - wykresy i wizualizacje
- **JavaScript (Vanilla)** - interaktywność

**Baza Danych:**
- **SQLite** (development) - zero konfiguracji
- **PostgreSQL** (production ready) - skalowalna baza danych

## 📦 Instalacja

### Wymagania Wstępne
- Python 3.8 lub nowszy
- pip (menedżer pakietów Python)
- Opcjonalnie: virtualenv

### Krok 1: Klonowanie Repozytorium
```bash
git clone <repository-url>
cd devcalc
```

### Krok 2: Utworzenie Środowiska Wirtualnego (Zalecane)
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Krok 3: Instalacja Zależności
```bash
pip install -r requirements.txt
```

### Krok 4: Konfiguracja Środowiska
```bash
# Kopiuj plik konfiguracyjny
cp .env.example .env

# Edytuj .env i ustaw:
# - SECRET_KEY (wygeneruj losowy klucz dla produkcji)
# - DATABASE_URL (opcjonalnie PostgreSQL)
```

### Krok 5: Inicjalizacja Bazy Danych
```bash
python run.py init_db
```

### Krok 6: Utworzenie Pierwszego Użytkownika
```bash
python run.py create_admin
# Postępuj zgodnie z instrukcjami (domyślnie: admin/admin123)
```

## 🚀 Uruchomienie Aplikacji

### Development (Lokalnie)
```bash
python run.py
```

Aplikacja będzie dostępna pod adresem: **http://localhost:5000**

### Production (Serwer)

#### Opcja 1: Gunicorn (Zalecane dla Linux)
```bash
# Instalacja
pip install gunicorn

# Uruchomienie
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

#### Opcja 2: Docker
```dockerfile
# Dockerfile (przykład)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]
```

```bash
docker build -t devcalc .
docker run -p 8000:8000 -e SECRET_KEY=your-secret-key devcalc
```

#### Opcja 3: Nginx + Gunicorn (Production)
```nginx
# /etc/nginx/sites-available/devcalc
server {
    listen 80;
    server_name twoja-domena.pl;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /home/user/devcalc/app/static;
    }
}
```

## 📊 Metodologia Obliczeń

### Model Cash Flow

Projekt dzieli się na 3 fazy:

1. **Faza Przygotowania** (6-12 miesięcy)
   - Zakup działki (100% w miesiącu 0)
   - Koszty pozyskania (notariusz, PCC)
   - Projekty architektoniczne i techniczne

2. **Faza Budowy** (18-24 miesiące)
   - Koszty budowy (równomiernie miesięcznie)
   - Infrastruktura towarzysząca
   - Overhead i zarządzanie projektem

3. **Faza Sprzedaży** (18-30 miesięcy)
   - Przychody ze sprzedaży lokali (stopniowo)
   - Marketing i prowizje
   - **Uwaga:** Sprzedaż nakłada się na budowę (start po ~60% budowy)

### Obliczenia NPV i IRR

#### NPV (Net Present Value)
```
NPV = Σ [CFt / (1 + r)^t]

gdzie:
- CFt = przepływ pieniężny w okresie t (miesiąc)
- r = miesięczna stopa dyskontowa
- t = numer okresu
```

**Warunek opłacalności:** NPV ≥ 0

#### IRR (Internal Rate of Return)
```
IRR to wartość r, dla której NPV = 0
```

**Warunek opłacalności:** IRR ≥ 15% (typowo)

### Kalkulacja Kredytu

Miesięczna rata (annuity):
```
PMT = P × [r(1+r)^n] / [(1+r)^n - 1]

gdzie:
- P = kwota kredytu
- r = miesięczna stopa oprocentowania
- n = liczba rat
```

Całkowity koszt kredytu = Odsetki + Prowizja

## 📁 Struktura Projektu

```
devcalc/
├── app/
│   ├── __init__.py           # Factory aplikacji Flask
│   ├── models.py             # Modele bazy danych (User, Project, etc.)
│   ├── financial_engine.py  # Logika finansowa (NPV, IRR, Cash Flow)
│   ├── auth/                 # Moduł uwierzytelniania
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── calculator/           # Moduł kalkulatora
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── costs/                # Moduł bazy kosztów
│   │   ├── __init__.py
│   │   └── routes.py
│   └── templates/            # Szablony HTML (Jinja2)
│       ├── base.html
│       ├── auth/
│       ├── calculator/
│       └── costs/
├── config.py                 # Konfiguracja aplikacji
├── requirements.txt          # Zależności Python
├── run.py                    # Punkt wejścia aplikacji
├── .env.example              # Przykładowa konfiguracja
├── .gitignore
└── README.md
```

## 🎓 Przykład Użycia

### 1. Utworzenie Projektu

Po zalogowaniu:
1. Kliknij **"Nowy Projekt"**
2. Wypełnij formularz:
   - **Dane działki:** powierzchnia, cena zakupu
   - **PUM:** powierzchnia użytkowa mieszkań
   - **Cena sprzedaży:** pesymistyczna wycena rynkowa
   - **Harmonogram:** czasy trwania faz (miesięce)
   - **Koszty jednostkowe:** z edytowalnej bazy lub własne wartości
3. Kliknij **"Oblicz opłacalność"**

### 2. Analiza Wyników

Ekran wyników pokazuje:
- **NPV i IRR** - kluczowe wskaźniki opłacalności
- **Marżę brutto** - różnica między przychodami a kosztami
- **Wymaganą cenę sprzedaży** - dla osiągnięcia docelowej marży
- **Wykres Cash Flow** - miesięczne przepływy i kumulacja
- **Szczegółową tabelę** - rozbicie kosztów i przychodów

### 3. Analiza Wrażliwości

Sprawdź wpływ zmian parametrów:
1. Z widoku projektu kliknij **"Analiza Wrażliwości"**
2. Wybierz zmienną (np. cena działki, czas sprzedaży)
3. Ustaw zakres zmian (+/- %)
4. Zobacz jak NPV i IRR reagują na zmiany

### 4. Zarządzanie Bazą Kosztów

Dostosuj koszty jednostkowe do rynku:
1. Przejdź do **"Baza Kosztów"**
2. Edytuj istniejące pozycje lub dodaj nowe
3. Nowe projekty będą używać zaktualizowanych wartości

## 🔒 Bezpieczeństwo

### Wbudowane Zabezpieczenia
- **Flask-Login** - bezpieczne sesje użytkowników
- **Werkzeug** - hashowanie haseł (PBKDF2)
- **Flask-WTF** - ochrona CSRF dla formularzy
- **SQL Injection** - parametryzowane zapytania (SQLAlchemy ORM)

### Zalecenia dla Produkcji
1. **Zmień SECRET_KEY** na losowy ciąg znaków:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. **Ustaw FLASK_ENV=production** w .env
3. **Użyj HTTPS** (certyfikat SSL/TLS)
4. **PostgreSQL** zamiast SQLite
5. **Backup bazy danych** regularnie
6. **Firewall** - ogranicz dostęp do portu aplikacji

## 📝 Konfiguracja Domyślna

Plik `config.py` zawiera:
```python
DEFAULT_DISCOUNT_RATE = 3.5      # Stopa dyskonta (%)
DEFAULT_EXPECTED_IRR = 15.0      # Minimalna oczekiwana IRR (%)
DEFAULT_TAX_RATE = 8.0           # Podatek (%)
DEFAULT_LOAN_INTEREST = 7.5      # Oprocentowanie kredytu (%)

DEFAULT_PREPARATION_PHASE = 9    # Przygotowanie (miesiące)
DEFAULT_CONSTRUCTION_PHASE = 21  # Budowa (miesiące)
DEFAULT_SALES_PHASE = 24         # Sprzedaż (miesiące)
```

## 🐛 Rozwiązywanie Problemów

### Problem: Aplikacja nie startuje
```bash
# Sprawdź instalację zależności
pip install -r requirements.txt --upgrade

# Sprawdź wersję Python
python --version  # Minimum 3.8
```

### Problem: Błąd bazy danych
```bash
# Usuń starą bazę i zainicjuj na nowo
rm devcalc.db
python run.py init_db
```

### Problem: Błędy importu modułów
```bash
# Aktywuj środowisko wirtualne
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

## 🤝 Wkład i Rozwój

Sugestie funkcji do dodania:
- [ ] Export wyników do PDF/Excel
- [ ] API REST dla integracji zewnętrznych
- [ ] Porównywanie wielu projektów
- [ ] Harmonogram Gantta dla faz projektu
- [ ] Multi-currency support (PLN, EUR, USD)
- [ ] Raporty dla inwestorów

## 📄 Licencja

Projekt prywatny - zastrzeżone wszystkie prawa.

## 📞 Wsparcie

W przypadku pytań lub problemów:
- Email: [twój-email@example.com]
- Issues: [GitHub Issues]

---

**Kalkulator Opłacalności Deweloperskiej** © 2025 | Metodologie: NPV & IRR

import os
from datetime import timedelta

class Config:
    """Konfiguracja aplikacji Flask"""

    # Podstawowa konfiguracja
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'

    # Baza danych
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///devcalc.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_PROTECTION = 'strong'

    # Domyślne wartości dla kalkulatora
    DEFAULT_DISCOUNT_RATE = 3.5  # %
    DEFAULT_EXPECTED_IRR = 15.0  # %
    DEFAULT_TAX_RATE = 8.0  # %
    DEFAULT_LOAN_INTEREST = 7.5  # %
    DEFAULT_LOAN_PROVISION = 2.0  # %

    # Czasookresy domyślne (w miesiącach)
    DEFAULT_PREPARATION_PHASE = 9  # 6-12 miesięcy
    DEFAULT_CONSTRUCTION_PHASE = 21  # 18-24 miesiące
    DEFAULT_SALES_PHASE = 24  # 18-30 miesięcy (pesymistycznie)

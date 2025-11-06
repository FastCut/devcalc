from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """Model użytkownika z systemem uwierzytelniania"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relacje
    projects = db.relationship('Project', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashowanie hasła"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Weryfikacja hasła"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class CostDatabase(db.Model):
    """Edytowalna baza kosztów jednostkowych"""
    __tablename__ = 'cost_database'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # np. PLN/m², PLN, %
    default_value = db.Column(db.Float, nullable=False)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def init_default_costs():
        """Inicjalizacja domyślnych kosztów jednostkowych"""
        default_costs = [
            # Koszty pozyskania
            {'category': 'acquisition', 'name': 'Opłata notarialna', 'unit': '%', 'default_value': 0.5, 'min_value': 0.3, 'max_value': 1.0, 'description': 'Procent od wartości transakcji'},
            {'category': 'acquisition', 'name': 'PCC', 'unit': '%', 'default_value': 2.0, 'min_value': 2.0, 'max_value': 2.0, 'description': 'Podatek od czynności cywilnoprawnych'},
            {'category': 'acquisition', 'name': 'Wpis do księgi wieczystej', 'unit': 'PLN', 'default_value': 200, 'min_value': 200, 'max_value': 500, 'description': 'Stała opłata'},

            # Koszty budowy
            {'category': 'construction', 'name': 'Budowa - stan deweloperski', 'unit': 'PLN/m²', 'default_value': 4500, 'min_value': 3500, 'max_value': 6000, 'description': 'Koszt budowy za m² PUM'},
            {'category': 'construction', 'name': 'Budowa - stan surowy', 'unit': 'PLN/m²', 'default_value': 3000, 'min_value': 2500, 'max_value': 4000, 'description': 'Koszt budowy stan surowy'},

            # Koszty projektowe
            {'category': 'design', 'name': 'Projekt architektoniczny', 'unit': 'PLN/m²', 'default_value': 120, 'min_value': 70, 'max_value': 200, 'description': 'Koszt projektu na m² nowej powierzchni'},
            {'category': 'design', 'name': 'Projekty techniczne', 'unit': 'PLN/m²', 'default_value': 50, 'min_value': 30, 'max_value': 100, 'description': 'Instalacje, konstrukcja'},

            # Infrastruktura
            {'category': 'infrastructure', 'name': 'Drogi i parkingi', 'unit': 'PLN/m²', 'default_value': 300, 'min_value': 200, 'max_value': 500, 'description': 'Koszt infrastruktury drogowej'},
            {'category': 'infrastructure', 'name': 'Sieci i media', 'unit': 'PLN/m²', 'default_value': 200, 'min_value': 100, 'max_value': 400, 'description': 'Przyłącza, sieci'},
            {'category': 'infrastructure', 'name': 'Tereny zielone', 'unit': 'PLN/m²', 'default_value': 150, 'min_value': 50, 'max_value': 300, 'description': 'Parki, zieleń'},

            # Overhead
            {'category': 'overhead', 'name': 'Zarządzanie projektem', 'unit': 'PLN/m²', 'default_value': 400, 'min_value': 300, 'max_value': 500, 'description': 'Koszty osobowe, biuro'},
            {'category': 'overhead', 'name': 'Rezerwa gotówkowa', 'unit': 'PLN/m²', 'default_value': 150, 'min_value': 100, 'max_value': 300, 'description': 'Bufor na nieprzewidziane'},

            # Marketing i sprzedaż
            {'category': 'sales', 'name': 'Marketing', 'unit': 'PLN/m²', 'default_value': 100, 'min_value': 50, 'max_value': 200, 'description': 'Reklama, materiały'},
            {'category': 'sales', 'name': 'Prowizja pośrednika', 'unit': '%', 'default_value': 3.0, 'min_value': 2.0, 'max_value': 5.0, 'description': 'Procent od wartości sprzedaży'},
            {'category': 'sales', 'name': 'Biuro sprzedaży', 'unit': 'PLN/miesiąc', 'default_value': 5000, 'min_value': 3000, 'max_value': 10000, 'description': 'Miesięczny koszt biura'},
        ]

        for cost_data in default_costs:
            cost = CostDatabase(**cost_data)
            db.session.add(cost)

        db.session.commit()

    def __repr__(self):
        return f'<Cost {self.category}/{self.name}>'


class Project(db.Model):
    """Model projektu deweloperskiego"""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Dane działki
    plot_area = db.Column(db.Float)  # m²
    plot_price_per_sqm = db.Column(db.Float)  # PLN/m²

    # Dane budynku
    pum_area = db.Column(db.Float)  # m² powierzchni użytkowej mieszkań
    units_count = db.Column(db.Integer)  # liczba lokali
    sale_price_per_sqm = db.Column(db.Float)  # PLN/m² PUM (pesymistyczna)
    parking_revenue = db.Column(db.Float, default=0)  # PLN

    # Harmonogram (w miesiącach)
    preparation_months = db.Column(db.Integer, default=9)
    construction_months = db.Column(db.Integer, default=21)
    sales_months = db.Column(db.Integer, default=24)

    # Parametry finansowe
    discount_rate = db.Column(db.Float, default=3.5)  # %
    expected_margin = db.Column(db.Float, default=20.0)  # %
    tax_rate = db.Column(db.Float, default=8.0)  # %

    # Kredyt
    loan_percentage = db.Column(db.Float, default=0)  # % finansowania kredytem
    loan_interest_rate = db.Column(db.Float, default=7.5)  # %
    loan_provision = db.Column(db.Float, default=2.0)  # %
    loan_months = db.Column(db.Integer, default=240)  # liczba rat (20 lat)

    # Relacje
    calculations = db.relationship('Calculation', backref='project', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.name}>'


class Calculation(db.Model):
    """Wyniki obliczeń dla projektu"""
    __tablename__ = 'calculations'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scenario = db.Column(db.String(50), default='base')  # base, optimistic, pessimistic

    # Wyniki
    total_revenue = db.Column(db.Float)
    total_costs = db.Column(db.Float)
    gross_margin = db.Column(db.Float)
    npv = db.Column(db.Float)
    irr = db.Column(db.Float)
    required_price_per_sqm = db.Column(db.Float)

    # Cash Flow (JSON)
    cash_flow_data = db.Column(db.Text)  # JSON string z miesięcznymi przepływami

    def __repr__(self):
        return f'<Calculation {self.scenario} for Project {self.project_id}>'

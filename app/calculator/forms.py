from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional


class ProjectForm(FlaskForm):
    """Formularz danych projektu deweloperskiego"""

    # Nazwa projektu
    name = StringField('Nazwa projektu', validators=[DataRequired()])

    # --- A. DANE DZIAŁKI I PRZYCHODY ---
    plot_area = FloatField(
        'Powierzchnia działki (m²)',
        validators=[DataRequired(), NumberRange(min=0.1)],
        render_kw={"class": "form-control input-highlight"}
    )
    plot_price_per_sqm = FloatField(
        'Cena zakupu działki (PLN/m²)',
        validators=[DataRequired(), NumberRange(min=0)],
        render_kw={"class": "form-control input-highlight"}
    )

    pum_area = FloatField(
        'PUM - Powierzchnia Użytkowa Mieszkań (m²)',
        validators=[DataRequired(), NumberRange(min=0.1)],
        render_kw={"class": "form-control input-highlight"}
    )
    units_count = IntegerField(
        'Liczba lokali/jednostek',
        validators=[DataRequired(), NumberRange(min=1)],
        render_kw={"class": "form-control input-highlight"}
    )
    sale_price_per_sqm = FloatField(
        'Pesymistyczna cena sprzedaży (PLN/m² PUM)',
        validators=[DataRequired(), NumberRange(min=0)],
        render_kw={"class": "form-control input-highlight"}
    )
    parking_revenue = FloatField(
        'Przychód z miejsc garażowych (PLN)',
        validators=[Optional(), NumberRange(min=0)],
        default=0,
        render_kw={"class": "form-control"}
    )

    # --- B. HARMONOGRAM (MIESIĄCE) ---
    preparation_months = IntegerField(
        'Faza przygotowania (miesiące)',
        validators=[DataRequired(), NumberRange(min=1, max=60)],
        default=9,
        render_kw={"class": "form-control"}
    )
    construction_months = IntegerField(
        'Faza budowy (miesiące)',
        validators=[DataRequired(), NumberRange(min=1, max=60)],
        default=21,
        render_kw={"class": "form-control"}
    )
    sales_months = IntegerField(
        'Faza sprzedaży (miesiące)',
        validators=[DataRequired(), NumberRange(min=1, max=60)],
        default=24,
        render_kw={"class": "form-control"}
    )

    # --- C. PARAMETRY FINANSOWE ---
    discount_rate = FloatField(
        'Stopa dyskonta (% roczna)',
        validators=[DataRequired(), NumberRange(min=0, max=100)],
        default=3.5,
        render_kw={"class": "form-control"}
    )
    expected_margin = FloatField(
        'Oczekiwana marża dewelopera (%)',
        validators=[DataRequired(), NumberRange(min=0, max=200)],
        default=20.0,
        render_kw={"class": "form-control"}
    )
    tax_rate = FloatField(
        'Stawka podatku (%)',
        validators=[DataRequired(), NumberRange(min=0, max=100)],
        default=8.0,
        render_kw={"class": "form-control"}
    )

    # --- D. KREDYT ---
    loan_percentage = FloatField(
        'Udział kredytu w finansowaniu (%)',
        validators=[Optional(), NumberRange(min=0, max=100)],
        default=0,
        render_kw={"class": "form-control"}
    )
    loan_interest_rate = FloatField(
        'Oprocentowanie kredytu (% roczna)',
        validators=[Optional(), NumberRange(min=0, max=100)],
        default=7.5,
        render_kw={"class": "form-control"}
    )
    loan_provision = FloatField(
        'Prowizja kredytowa (%)',
        validators=[Optional(), NumberRange(min=0, max=10)],
        default=2.0,
        render_kw={"class": "form-control"}
    )
    loan_months = IntegerField(
        'Liczba rat kredytu (miesiące)',
        validators=[Optional(), NumberRange(min=1, max=600)],
        default=240,
        render_kw={"class": "form-control"}
    )

    # --- E. KOSZTY JEDNOSTKOWE ---
    # Można ustawić z bazy danych lub ręcznie
    acquisition_costs_pct = FloatField(
        'Koszty pozyskania (% od wartości zakupu)',
        validators=[DataRequired(), NumberRange(min=0, max=10)],
        default=2.7,
        render_kw={"class": "form-control"}
    )
    construction_cost_per_sqm = FloatField(
        'Koszt budowy (PLN/m² PUM)',
        validators=[DataRequired(), NumberRange(min=0)],
        default=4500,
        render_kw={"class": "form-control"}
    )
    design_cost_per_sqm = FloatField(
        'Koszty projektowe (PLN/m² PUM)',
        validators=[DataRequired(), NumberRange(min=0)],
        default=120,
        render_kw={"class": "form-control"}
    )
    infrastructure_cost_per_sqm = FloatField(
        'Infrastruktura (PLN/m² PUM)',
        validators=[DataRequired(), NumberRange(min=0)],
        default=200,
        render_kw={"class": "form-control"}
    )
    overhead_cost_per_sqm = FloatField(
        'Zarządzanie/Overhead (PLN/m² PUM)',
        validators=[DataRequired(), NumberRange(min=0)],
        default=400,
        render_kw={"class": "form-control"}
    )
    reserve_cost_per_sqm = FloatField(
        'Rezerwa gotówkowa (PLN/m² PUM)',
        validators=[DataRequired(), NumberRange(min=0)],
        default=150,
        render_kw={"class": "form-control"}
    )
    marketing_cost_per_sqm = FloatField(
        'Marketing (PLN/m² PUM)',
        validators=[DataRequired(), NumberRange(min=0)],
        default=100,
        render_kw={"class": "form-control"}
    )
    sales_commission_pct = FloatField(
        'Prowizja sprzedażowa (% od przychodu)',
        validators=[DataRequired(), NumberRange(min=0, max=10)],
        default=3.0,
        render_kw={"class": "form-control"}
    )

    submit = SubmitField('Oblicz opłacalność')


class SensitivityAnalysisForm(FlaskForm):
    """Formularz analizy wrażliwości"""

    variable = SelectField(
        'Zmienna do analizy',
        choices=[
            ('plot_price_per_sqm', 'Cena działki (PLN/m²)'),
            ('sale_price_per_sqm', 'Cena sprzedaży (PLN/m²)'),
            ('construction_cost_per_sqm', 'Koszt budowy (PLN/m²)'),
            ('sales_months', 'Czas sprzedaży (miesiące)'),
            ('discount_rate', 'Stopa dyskonta (%)'),
        ],
        validators=[DataRequired()]
    )

    range_pct = FloatField(
        'Zakres zmian (+/- %)',
        validators=[DataRequired(), NumberRange(min=1, max=100)],
        default=20,
        render_kw={"class": "form-control"}
    )

    submit = SubmitField('Przeprowadź analizę')

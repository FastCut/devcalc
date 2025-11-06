from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.calculator import bp
from app.calculator.forms import ProjectForm, SensitivityAnalysisForm
from app.models import Project, Calculation
from app.financial_engine import (
    FinancialEngine, ProjectInputs, run_sensitivity_analysis
)
from dataclasses import asdict
import json


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """Strona główna - lista projektów użytkownika"""
    projects = current_user.projects.order_by(Project.updated_at.desc()).all()
    return render_template('calculator/index.html', title='Moje Projekty', projects=projects)


@bp.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """Tworzenie nowego projektu"""
    form = ProjectForm()

    if form.validate_on_submit():
        # Utworzenie projektu
        project = Project(
            user_id=current_user.id,
            name=form.name.data,
            plot_area=form.plot_area.data,
            plot_price_per_sqm=form.plot_price_per_sqm.data,
            pum_area=form.pum_area.data,
            units_count=form.units_count.data,
            sale_price_per_sqm=form.sale_price_per_sqm.data,
            parking_revenue=form.parking_revenue.data or 0,
            preparation_months=form.preparation_months.data,
            construction_months=form.construction_months.data,
            sales_months=form.sales_months.data,
            discount_rate=form.discount_rate.data,
            expected_margin=form.expected_margin.data,
            tax_rate=form.tax_rate.data,
            loan_percentage=form.loan_percentage.data or 0,
            loan_interest_rate=form.loan_interest_rate.data or 7.5,
            loan_provision=form.loan_provision.data or 2.0,
            loan_months=form.loan_months.data or 240
        )

        db.session.add(project)
        db.session.commit()

        # Uruchomienie kalkulacji
        result = calculate_project(project, form)

        # Zapisanie wyników
        save_calculation(project, result, 'base', form)

        flash(f'Projekt "{project.name}" został utworzony i obliczony!', 'success')
        return redirect(url_for('calculator.view_project', project_id=project.id))

    return render_template('calculator/project_form.html', title='Nowy Projekt', form=form, mode='new')


@bp.route('/project/<int:project_id>')
@login_required
def view_project(project_id):
    """Podgląd wyników projektu"""
    project = Project.query.get_or_404(project_id)

    # Sprawdzenie uprawnień
    if project.user_id != current_user.id:
        flash('Nie masz dostępu do tego projektu.', 'danger')
        return redirect(url_for('calculator.index'))

    # Pobranie ostatniej kalkulacji
    calculation = project.calculations.order_by(Calculation.created_at.desc()).first()

    if not calculation:
        flash('Brak wyników obliczeń dla tego projektu.', 'warning')
        return redirect(url_for('calculator.edit_project', project_id=project_id))

    # Parsowanie cash flow
    cash_flow_data = json.loads(calculation.cash_flow_data) if calculation.cash_flow_data else []

    return render_template(
        'calculator/view_project.html',
        title=project.name,
        project=project,
        calculation=calculation,
        cash_flow_data=cash_flow_data
    )


@bp.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edycja projektu"""
    project = Project.query.get_or_404(project_id)

    if project.user_id != current_user.id:
        flash('Nie masz dostępu do tego projektu.', 'danger')
        return redirect(url_for('calculator.index'))

    form = ProjectForm(obj=project)

    # Wypełnienie formularza danymi z ostatniej kalkulacji
    if request.method == 'GET':
        # Dane z projektu są już załadowane przez obj=project
        # Dodatkowo możemy ustawić koszty jednostkowe z poprzedniej kalkulacji
        pass

    if form.validate_on_submit():
        # Aktualizacja projektu
        project.name = form.name.data
        project.plot_area = form.plot_area.data
        project.plot_price_per_sqm = form.plot_price_per_sqm.data
        project.pum_area = form.pum_area.data
        project.units_count = form.units_count.data
        project.sale_price_per_sqm = form.sale_price_per_sqm.data
        project.parking_revenue = form.parking_revenue.data or 0
        project.preparation_months = form.preparation_months.data
        project.construction_months = form.construction_months.data
        project.sales_months = form.sales_months.data
        project.discount_rate = form.discount_rate.data
        project.expected_margin = form.expected_margin.data
        project.tax_rate = form.tax_rate.data
        project.loan_percentage = form.loan_percentage.data or 0
        project.loan_interest_rate = form.loan_interest_rate.data or 7.5
        project.loan_provision = form.loan_provision.data or 2.0
        project.loan_months = form.loan_months.data or 240

        db.session.commit()

        # Przeliczenie
        result = calculate_project(project, form)
        save_calculation(project, result, 'base', form)

        flash(f'Projekt "{project.name}" został zaktualizowany!', 'success')
        return redirect(url_for('calculator.view_project', project_id=project.id))

    return render_template('calculator/project_form.html', title='Edytuj Projekt', form=form, project=project, mode='edit')


@bp.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Usunięcie projektu"""
    project = Project.query.get_or_404(project_id)

    if project.user_id != current_user.id:
        flash('Nie masz dostępu do tego projektu.', 'danger')
        return redirect(url_for('calculator.index'))

    name = project.name
    db.session.delete(project)
    db.session.commit()

    flash(f'Projekt "{name}" został usunięty.', 'info')
    return redirect(url_for('calculator.index'))


@bp.route('/project/<int:project_id>/sensitivity', methods=['GET', 'POST'])
@login_required
def sensitivity_analysis(project_id):
    """Analiza wrażliwości projektu"""
    project = Project.query.get_or_404(project_id)

    if project.user_id != current_user.id:
        flash('Nie masz dostępu do tego projektu.', 'danger')
        return redirect(url_for('calculator.index'))

    form = SensitivityAnalysisForm()

    if form.validate_on_submit():
        # Pobierz dane projektu
        calculation = project.calculations.order_by(Calculation.created_at.desc()).first()
        if not calculation:
            flash('Najpierw oblicz projekt bazowy.', 'warning')
            return redirect(url_for('calculator.edit_project', project_id=project_id))

        # Przygotuj inputs
        inputs = project_to_inputs(project, calculation)

        # Uruchom analizę wrażliwości
        variable_name = form.variable.data
        range_pct = form.range_pct.data

        results = run_sensitivity_analysis(inputs, variable_name, range_pct, steps=10)

        # Formatuj dla wykresu
        chart_data = {
            'labels': [f"{r['variable_value']:.2f}" for r in results],
            'npv': [r['npv'] for r in results],
            'irr': [r['irr'] for r in results],
            'margin': [r['margin'] for r in results]
        }

        return render_template(
            'calculator/sensitivity_analysis.html',
            title=f'Analiza Wrażliwości - {project.name}',
            project=project,
            form=form,
            variable_name=variable_name,
            chart_data=chart_data,
            results=results
        )

    return render_template(
        'calculator/sensitivity_analysis.html',
        title=f'Analiza Wrażliwości - {project.name}',
        project=project,
        form=form
    )


def calculate_project(project: Project, form: ProjectForm):
    """Wykonuje kalkulację projektu"""
    inputs = ProjectInputs(
        plot_area=project.plot_area,
        plot_price_per_sqm=project.plot_price_per_sqm,
        pum_area=project.pum_area,
        units_count=project.units_count,
        sale_price_per_sqm=project.sale_price_per_sqm,
        parking_revenue=project.parking_revenue,
        preparation_months=project.preparation_months,
        construction_months=project.construction_months,
        sales_months=project.sales_months,
        discount_rate=project.discount_rate,
        expected_margin=project.expected_margin,
        tax_rate=project.tax_rate,
        loan_percentage=project.loan_percentage,
        loan_interest_rate=project.loan_interest_rate,
        loan_provision=project.loan_provision,
        loan_months=project.loan_months,
        acquisition_costs_pct=form.acquisition_costs_pct.data,
        construction_cost_per_sqm=form.construction_cost_per_sqm.data,
        design_cost_per_sqm=form.design_cost_per_sqm.data,
        infrastructure_cost_per_sqm=form.infrastructure_cost_per_sqm.data,
        overhead_cost_per_sqm=form.overhead_cost_per_sqm.data,
        reserve_cost_per_sqm=form.reserve_cost_per_sqm.data,
        marketing_cost_per_sqm=form.marketing_cost_per_sqm.data,
        sales_commission_pct=form.sales_commission_pct.data
    )

    engine = FinancialEngine(inputs)
    result = engine.run_calculation()

    return result


def project_to_inputs(project: Project, calculation: Calculation) -> ProjectInputs:
    """Konwertuje projekt i kalkulację do ProjectInputs (dla analizy wrażliwości)"""
    # Tutaj zakładamy, że koszty jednostkowe są stałe lub używamy domyślnych
    # W pełnej implementacji można je przechowywać w Calculation
    return ProjectInputs(
        plot_area=project.plot_area,
        plot_price_per_sqm=project.plot_price_per_sqm,
        pum_area=project.pum_area,
        units_count=project.units_count,
        sale_price_per_sqm=project.sale_price_per_sqm,
        parking_revenue=project.parking_revenue,
        preparation_months=project.preparation_months,
        construction_months=project.construction_months,
        sales_months=project.sales_months,
        discount_rate=project.discount_rate,
        expected_margin=project.expected_margin,
        tax_rate=project.tax_rate,
        loan_percentage=project.loan_percentage,
        loan_interest_rate=project.loan_interest_rate,
        loan_provision=project.loan_provision,
        loan_months=project.loan_months,
        acquisition_costs_pct=2.7,
        construction_cost_per_sqm=4500,
        design_cost_per_sqm=120,
        infrastructure_cost_per_sqm=200,
        overhead_cost_per_sqm=400,
        reserve_cost_per_sqm=150,
        marketing_cost_per_sqm=100,
        sales_commission_pct=3.0
    )


def save_calculation(project: Project, result, scenario: str, form: ProjectForm):
    """Zapisuje wyniki kalkulacji do bazy"""
    # Konwertuj cash_flow do JSON
    cash_flow_json = json.dumps([
        {
            'month': cf.month,
            'phase': cf.phase,
            'revenues': cf.revenues,
            'costs': cf.costs,
            'net_cash_flow': cf.net_cash_flow,
            'cumulative_cash_flow': cf.cumulative_cash_flow
        }
        for cf in result.cash_flow
    ])

    calculation = Calculation(
        project_id=project.id,
        scenario=scenario,
        total_revenue=result.total_revenue,
        total_costs=result.total_costs,
        gross_margin=result.gross_margin,
        npv=result.npv,
        irr=result.irr,
        required_price_per_sqm=result.required_price_per_sqm,
        cash_flow_data=cash_flow_json
    )

    db.session.add(calculation)
    db.session.commit()

    return calculation

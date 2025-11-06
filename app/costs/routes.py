from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.costs import bp
from app.models import CostDatabase


@bp.route('/')
@login_required
def index():
    """Lista kosztów jednostkowych"""
    costs = CostDatabase.query.order_by(CostDatabase.category, CostDatabase.name).all()

    # Grupowanie po kategoriach
    categories = {}
    for cost in costs:
        if cost.category not in categories:
            categories[cost.category] = []
        categories[cost.category].append(cost)

    category_names = {
        'acquisition': 'Koszty pozyskania',
        'construction': 'Koszty budowy',
        'design': 'Koszty projektowe',
        'infrastructure': 'Infrastruktura',
        'overhead': 'Zarządzanie i overhead',
        'sales': 'Marketing i sprzedaż'
    }

    return render_template(
        'costs/index.html',
        title='Baza Kosztów Jednostkowych',
        categories=categories,
        category_names=category_names
    )


@bp.route('/edit/<int:cost_id>', methods=['GET', 'POST'])
@login_required
def edit_cost(cost_id):
    """Edycja kosztu jednostkowego"""
    cost = CostDatabase.query.get_or_404(cost_id)

    if request.method == 'POST':
        cost.default_value = float(request.form.get('default_value'))
        cost.min_value = float(request.form.get('min_value')) if request.form.get('min_value') else None
        cost.max_value = float(request.form.get('max_value')) if request.form.get('max_value') else None
        cost.description = request.form.get('description')

        db.session.commit()

        flash(f'Koszt "{cost.name}" został zaktualizowany.', 'success')
        return redirect(url_for('costs.index'))

    return render_template('costs/edit.html', title='Edytuj Koszt', cost=cost)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_cost():
    """Dodawanie nowego kosztu"""
    if request.method == 'POST':
        cost = CostDatabase(
            category=request.form.get('category'),
            name=request.form.get('name'),
            unit=request.form.get('unit'),
            default_value=float(request.form.get('default_value')),
            min_value=float(request.form.get('min_value')) if request.form.get('min_value') else None,
            max_value=float(request.form.get('max_value')) if request.form.get('max_value') else None,
            description=request.form.get('description')
        )

        db.session.add(cost)
        db.session.commit()

        flash(f'Koszt "{cost.name}" został dodany.', 'success')
        return redirect(url_for('costs.index'))

    categories = ['acquisition', 'construction', 'design', 'infrastructure', 'overhead', 'sales']
    return render_template('costs/add.html', title='Dodaj Koszt', categories=categories)


@bp.route('/delete/<int:cost_id>', methods=['POST'])
@login_required
def delete_cost(cost_id):
    """Usunięcie kosztu"""
    cost = CostDatabase.query.get_or_404(cost_id)
    name = cost.name

    db.session.delete(cost)
    db.session.commit()

    flash(f'Koszt "{name}" został usunięty.', 'info')
    return redirect(url_for('costs.index'))

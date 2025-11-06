from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Strona logowania"""
    if current_user.is_authenticated:
        return redirect(url_for('calculator.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Nieprawidłowa nazwa użytkownika lub hasło', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('calculator.index')

        flash(f'Witaj, {user.username}!', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', title='Logowanie', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Strona rejestracji"""
    if current_user.is_authenticated:
        return redirect(url_for('calculator.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Gratulacje! Twoje konto zostało utworzone. Możesz się teraz zalogować.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Rejestracja', form=form)


@bp.route('/logout')
def logout():
    """Wylogowanie użytkownika"""
    logout_user()
    flash('Zostałeś wylogowany.', 'info')
    return redirect(url_for('auth.login'))

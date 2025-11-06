from flask import Blueprint

bp = Blueprint('calculator', __name__)

from app.calculator import routes

from flask import Blueprint

bp = Blueprint('costs', __name__)

from app.costs import routes

from flask import Blueprint

fintech_bp = Blueprint('fintech', __name__)

from app.routes.fintech.routes import *

from flask import Blueprint

accessibility_bp = Blueprint('accessibility', __name__)

from app.routes.accessibility.routes import *

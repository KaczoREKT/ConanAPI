from app.models.main import Model
from app.views.main import View

class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view


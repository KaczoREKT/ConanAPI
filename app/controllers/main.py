from app.controllers.photo import PhotoController
from app.models.main import Model
from app.views.main import View

class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        self.photo_controller = PhotoController(model, view)

    def start(self):
        self.view.start_mainloop()


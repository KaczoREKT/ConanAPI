from app.controllers.photo import PhotoController
from app.models.main import Model
from app.views.main import View

class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        self.photo_controller = PhotoController(model, view)


    def photo_combobox_listener(self, data):
        self.model.get_photo(data)
        self.view.frames['main_frame'].photo_image.configure(file=self.view.frames['main_frame'].get_chosen_photo)


    def start(self):
        self.view.start_mainloop()


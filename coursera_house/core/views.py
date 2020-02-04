from django.urls import reverse_lazy
from django.views.generic import FormView
import requests
from .models import Setting
from .form import ControllerForm


def get_data():
    headers = {
        'Authorization': 'Bearer 3ccb919055ef8023a007930dfe9aac244fc98526a5924ca4d086f88f72bd6455',
    }

    response = requests.get('https://smarthome.webpython.graders.eldf.ru/api/user.controller', headers=headers)
    return {item['name']: item['value'] for item in response.json()['data']}


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = {}
        return context

    def get_initial(self):
        """Define default values"""
        default_controller_value = super(ControllerView, self).get_initial()
        current_controlers_values = get_data()
        controlers_names = {'bedroom_target_temperature': 'bedroom_temperature',
                            'hot_water_target_temperature': 'boiler_temperature',
                            'bedroom_light': 'bedroom_light',
                            'bathroom_light': 'bathroom_light'}
        for controler_name in controlers_names:
            if current_controlers_values[controlers_names[controler_name]]:
                new_value = current_controlers_values.get(controlers_names.get(controler_name))
                default_controller_value[controler_name] = new_value
        return default_controller_value

    def form_valid(self, form):
        return super(ControllerView, self).form_valid(form)

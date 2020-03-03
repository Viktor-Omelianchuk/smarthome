from django.urls import reverse_lazy
from django.views.generic import FormView
import requests
from django.conf import settings
from .models import Setting
from .form import ControllerForm
from django.http import HttpResponse, JsonResponse
import json


TOKEN = settings.SMART_HOME_ACCESS_TOKEN
url = settings.SMART_HOME_API_URL
headers = {"Authorization": f"Bearer {TOKEN}"}


def get_current_controlers_values():
    """The function allows to get the current values ​​of controllers
    from a remote server of a smart home"""
    try:
        response = requests.get(url, headers=headers)
    except:
        return JsonResponse(status=502, data={})
    return {item["name"]: item["value"] for item in response.json()["data"]}


def send_values_to_controlers(data):
    """The function sends data to a remote smart home server"""
    return requests.post(url, headers=headers, data=data)


def get_or_update(controller_name, label, value):
    """The function updates the values of the settings database"""
    try:
        entry = Setting.objects.get(controller_name=controller_name)
    except Setting.DoesNotExist:
        Setting.objects.create(
            controller_name=controller_name, label=label, value=value
        )
    else:
        entry.value = value
        entry.save()


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = "core/control.html"
    success_url = reverse_lazy("form")

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        try:
            context["data"] = get_current_controlers_values()
        except:
            context["data"] = {}
        return context

    def get_initial(self):
        """Define default values"""
        default_controller_value = super(ControllerView, self).get_initial()
        current_controlers_values = get_current_controlers_values()
        try:
            bedroom_target_temperature = Setting.objects.get(
                controller_name="bedroom_target_temperature"
            ).value
            default_controller_value[
                "bedroom_target_temperature"
            ] = bedroom_target_temperature
            hot_water_target_temperature = Setting.objects.get(
                controller_name="hot_water_target_temperature"
            ).value
            default_controller_value[
                "hot_water_target_temperature"
            ] = hot_water_target_temperature
        except Setting.DoesNotExist:
            pass

        controlers_names = {
            "bedroom_light": "bedroom_light",
            "bathroom_light": "bathroom_light",
        }
        for controler_name in controlers_names:
            if current_controlers_values[controlers_names[controler_name]]:
                new_value = current_controlers_values.get(
                    controlers_names.get(controler_name)
                )
                default_controller_value[controler_name] = new_value
        return default_controller_value

    def form_valid(self, form):
        values_for_saving_in_db = [
            [
                "bedroom_target_temperature",
                "Bedroom target temperature",
                form.cleaned_data["bedroom_target_temperature"],
            ],
            [
                "hot_water_target_temperature",
                "Hot water target temperature value",
                form.cleaned_data["hot_water_target_temperature"],
            ],
        ]
        for value in values_for_saving_in_db:
            get_or_update(*value)

        current_controlers_values = get_current_controlers_values()
        if current_controlers_values:
            controller_bedroom_light = current_controlers_values["bedroom_light"]
            controller_bathroom_light = current_controlers_values["bathroom_light"]
            smoke_detector = current_controlers_values["smoke_detector"]
            payload = {"controllers": []}
            if not smoke_detector:
                if form.cleaned_data["bedroom_light"] != controller_bedroom_light:
                    payload["controllers"].append(
                        {
                            "name": "bedroom_light",
                            "value": form.cleaned_data["bedroom_light"],
                        }
                    )
                if form.cleaned_data["bathroom_light"] != controller_bathroom_light:
                    payload["controllers"].append(
                        {
                            "name": "bathroom_light",
                            "value": form.cleaned_data["bathroom_light"],
                        }
                    )
                data = json.dumps(payload)
                send_values_to_controlers(data)
        return super(ControllerView, self).form_valid(form)

from django import forms
from django.utils.translation import ugettext_lazy, ugettext as _
from crispy_forms.helper import FormHelper
from crispy_forms import layout as crispy
from crispy_forms import bootstrap as twbscrispy
from corehq.apps.style import crispy as hqcrispy

from .models import Notification

class NotificationCreationForm(forms.Form):
    content = forms.CharField(
        label=ugettext_lazy('Content')
    )
    url = forms.URLField(
        label=ugettext_lazy('URL')
    )
    type = forms.ChoiceField(
        label=ugettext_lazy("Type"),
        choices=(
            ('info', 'info'),
            ('alert', 'alert'),
        ),
    )

    def __init__(self, *args, **kwargs):
        super(NotificationCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = '#'

        self.helper.label_class = 'col-sm-3 col-md-2'
        self.helper.field_class = 'col-sm-9 col-md-8 col-lg-6'

        self.helper.layout = crispy.Layout(
            crispy.Field('content'),
            crispy.Field('url'),
            crispy.Field('type'),
            hqcrispy.FormActions(
                twbscrispy.StrictButton(
                    _("Submit Information"),
                    type="submit",
                    css_class="btn btn-primary",
                    name="submit",
                ),
                hqcrispy.LinkButton(
                    _("Cancel"),
                    '#',
                    css_class="btn btn-default",
                    name="cancel",
                ),
            ),
        )

    def save(self):
        data = self.data
        Notification(content=data.get('content'), url=data.get('url'), type=data.get('type')).save()

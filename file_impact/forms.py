from django import forms


class FileImpactForm(forms.Form):
    def __init__(self, files, *args, **kwargs):
        super(FileImpactForm, self).__init__(*args, **kwargs)
        self.fields["files"] = forms.ChoiceField(
            choices=[(f, f) for f in files]
        )
from django import forms


class FileImpactForm(forms.Form):
    SELECTION_TYPE = [
        ("1", "File"),
        ("2", "Commit")
    ]
    selection_type = forms.ChoiceField(widget=forms.RadioSelect,
                                       choices=SELECTION_TYPE,
                                       initial="1")
    commit = forms.CharField(required=False)

    def __init__(self, files, *args, **kwargs):
        super(FileImpactForm, self).__init__(*args, **kwargs)
        self.fields["files"] = forms.ChoiceField(required=False,
            choices=[(f, f) for f in files]
        )


class FileUNDImpactForm(forms.Form):
    SELECTION_TYPE = [
        ("1", "File"),
        ("2", "Commit")
    ]
    selection_type = forms.ChoiceField(widget=forms.RadioSelect,
                                       choices=SELECTION_TYPE,
                                       initial="2")
    commit = forms.CharField(required=False)
    func_name = forms.CharField(required=False)

    def __init__(self, files, *args, **kwargs):
        super(FileUNDImpactForm, self).__init__(*args, **kwargs)
        self.fields["files"] = forms.ChoiceField(required=False,
            choices=[(f, f) for f in files]
        )
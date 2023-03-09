from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

# from betterforms.multiform import MultiForm, MultiModelForm
from .models import SnapshotMetaData


def validate_digits_letters(word):
    for char in word:
        if not char.isdigit() and not char.isalpha() and not char.isspace():
            return False
    return True


class CreateSnapshotForm(forms.ModelForm):

    snapshotName = forms.CharField(max_length=25, label="Baseline name")
    testvar = ""

    class Meta:
        model = SnapshotMetaData
        fields = (
            # first tab fields
            "snapshotName",
        )

        labels = {
            'snapshotName': 'Baseline Freeze Name',
        }

        widgets = {
            'snapshotName': forms.Textarea(attrs={
                'maxlength': '25',
            }),
        }

    def __init__(self, user, *args, **kwargs):
        try:
            self.request = kwargs.pop('request')
            print("current request user", self.request.user)
        except:
            pass
        self.testvar = "asd123"
        self.user = user
        super(CreateSnapshotForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        snapshotName = cleaned_data.get("snapshotName")
        user = self.user
        print("checking snapshot name", snapshotName)
        filteredName = snapshotName.replace(' ', '_')

        query = SnapshotMetaData.objects.filter(
            snapshotName=filteredName, user=user)
        print("query ", query)

        if query.count() > 0:
            print("raising validation error!!!")
            raise ValidationError(
                "You already created a baseline freeze with this name!")

        if not validate_digits_letters(snapshotName):
            raise forms.ValidationError(
                "Usernames contains characters that are not numbers nor letters")

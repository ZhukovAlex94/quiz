from django import forms
from django.core.exceptions import ValidationError

from .models import Choice


class QuestionInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        questions = [form for form in self.forms if form['DELETE'].value() is False]

        if not (self.instance.QUESTION_MIN_LIMIT <= len(questions) <= self.instance.QUESTION_MAX_LIMIT):
            raise ValidationError(
                f'Questions count must be range '
                f'from {self.instance.QUESTION_MIN_LIMIT} '
                f'to {self.instance.QUESTION_MAX_LIMIT} inclusive'
            )

        order_nums = {int(form['order_num'].value()) for form in questions}
        if len(order_nums) != len(questions):
            raise ValidationError(
                f'Found duplication of order num.'
            )
        max_order_num = max(order_nums)
        min_order_num = min(order_nums)
        if max_order_num > self.instance.QUESTION_MAX_LIMIT:
            raise ValidationError(
                f'Max order_num should be less than or equal {self.instance.QUESTION_MAX_LIMIT}'
            )
        if min_order_num != 1 or order_nums != {value for value in range(min_order_num, max_order_num + 1)}:
            raise ValidationError(
                f'All order_nums should be in sequential order (1, 2, 3, 4, ...)'
            )


class ChoiceInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        # lst = []
        # for form in self.forms:
        #     if form.cleaned_data['is_correct']:
        #         lst.append(1)
        #     else:
        #         lst.append(0)
        #
        # num_correct_answers = sum(lst)

        # num_correct_answers = sum(1 for form in self.forms if form.cleaned_data['is_correct'])

        num_correct_answers = sum(form.cleaned_data['is_correct'] for form in self.forms)

        if num_correct_answers == 0:
            raise ValidationError('Need to choose one option minimum')

        if num_correct_answers == len(self.forms):
            raise ValidationError('It is not allowed to select all options')


class ChoiceForm(forms.ModelForm):
    is_selected = forms.BooleanField(required=False)

    class Meta:
        model = Choice
        fields = ('text',)


ChoicesFormSet = forms.modelformset_factory(
    model=Choice,
    form=ChoiceForm,
    extra=0
)

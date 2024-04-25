from django import forms
from .models import Product, Category
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import FormActions

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        categories = Category.objects.all()
        category_choices = [(c.id, c.name) for c in categories]

        self.fields['category'].choices = category_choices
        self.fields['stripe_price_id'].label += ' | User must get this from stripe'

        # Apply general styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control border-2 rounded'

        # Apply specific styling to the image field
        self.fields['image'].widget.attrs.update({
            'class': 'file-upload',  # Add a specific class for further styling with CSS
            'onchange': "readURL(this);"  # Optional JavaScript function to preview image
        })

        # Define form layout using Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form mb-4'
        self.helper.label_class = 'control-label'
        self.helper.field_class = 'mb-3'
        self.helper.layout = Layout(
            Field('category'),
            Field('name'),
            Field('description'),
            Field('stripe_price_id'),
            Field('price'),
            'image',  # Use a string here if you don't need additional arguments
            FormActions(
                Submit('save', 'Update Product', css_class="btn btn-primary mt-4"),
                css_class='d-grid gap-2'  # Adjust this as needed for your layout
            )
        )

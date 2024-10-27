from django import forms

from apps.tenant.models import Employees, StoreInformation
from apps.user.models import CustomUser
from apps.ecommerce.models import Products, ProductImages, ProductCategory
from apps.ecommerce.models import (
    RelatedProductsUI,
    FooterUI,
    TopBarUI,
    ImageWithTextUI,
    CategoryUI,
    FeaturedProductsUI,
)


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employees
        exclude = ("user", "is_owner")


class EmployeeRegisterForm(forms.ModelForm):
    class Meta:
        model = Employees
        exclude = ("user", "is_owner", "tenant")


# class CustomUserEditForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ['first_name',"last_name","email"]

# class EmployeeEditForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         exclude = ("tenant",)
#         fields = ['first_name',"last_name","email"]


class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]


class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = Employees
        exclude = ("tenant",)


class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        exclude = (
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
            "groups",
            "user_permissions",
            "last_login",
        )


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )
    # tenant = forms.CharField(
    #     max_length=50, widget=forms.TextInput(attrs={"placeholder": "Tenant"})
    # )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email or not password:
            raise forms.ValidationError("All fields must be filled out.")


# forms.py


class RelatedProductsUIForm(forms.ModelForm):
    class Meta:
        model = RelatedProductsUI
        fields = "__all__"
        exclude = ("tenant",)


class FooterUIForm(forms.ModelForm):
    class Meta:
        model = FooterUI
        fields = "__all__"
        exclude = ("tenant",)


class TopBarUIForm(forms.ModelForm):
    class Meta:
        model = TopBarUI
        fields = "__all__"
        exclude = ("tenant",)


class ImageWithTextUIForm(forms.ModelForm):
    class Meta:
        model = ImageWithTextUI
        fields = "__all__"
        exclude = ("tenant",)


class CategoryUIForm(forms.ModelForm):
    class Meta:
        model = CategoryUI
        fields = "__all__"
        exclude = ("tenant",)


class FeaturedProductsUIForm(forms.ModelForm):
    class Meta:
        model = FeaturedProductsUI
        fields = "__all__"
        exclude = ("tenant",)

    def __init__(self, *args, **kwargs):
        current_tenant = kwargs.pop("current_tenant", None)

        super(FeaturedProductsUIForm, self).__init__(*args, **kwargs)
        if current_tenant:
            self.fields["products"].queryset = Products.objects.filter(
                tenant=current_tenant
            )
        else:
            self.fields["products"].queryset = Products.objects.filter()

        self.fields["products"].widget.attrs.update(
            {
                "class": "js-example-basic-single",
                "id": "id_products",
            }
        )


class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = "__all__"
        exclude = ("tenant", "slug")

    def __init__(self, *args, **kwargs):
        current_tenant = kwargs.pop("current_tenant", None)
        super(CreateProductForm, self).__init__(*args, **kwargs)
        if current_tenant:
            self.fields["category"].queryset = ProductCategory.objects.filter(
                tenant=current_tenant
            )
            self.fields["images"].queryset = ProductImages.objects.filter(
                tenant=current_tenant
            )
        else:
            self.fields["category"].queryset = ProductCategory.objects.filter()
            self.fields["images"].queryset = ProductImages.objects.all()


class CreateProductImage(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = "__all__"
        exclude = ("tenant",)

    def __init__(self, *args, **kwargs):
        current_tenant = kwargs.pop("current_tenant", None)
        super(CreateProductImage, self).__init__(*args, **kwargs)


class CreateCategory(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = "__all__"
        exclude = ("tenant",)


class EditProduct(forms.ModelForm):
    class Meta:
        model = Products
        fields = "__all__"
        exclude = ("tenant",)

    # def __init__(self, *args, **kwargs):
    #     current_tenant = kwargs.pop("current_tenant", None)

    #     super(CreateProductForm, self).__init__(*args, **kwargs)
    #     if current_tenant:
    #         self.fields["products"].queryset = Products.objects.filter(
    #             tenant=current_tenant
    #         )
    #     else:
    #         self.fields["products"].queryset = Products.objects.filter()

    #     self.fields["products"].widget.attrs.update(
    #         {
    #             "class": "js-example-basic-single",
    #             "id": "id_products",
    #         }
    # )


class AddStoreInformation(forms.ModelForm):
    class Meta:
        model = StoreInformation
        fields = "__all__"
        exclude = ("tenant",)

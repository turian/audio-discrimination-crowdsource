from django.shortcuts import redirect
from django.urls import reverse


class CheckUserLockMixin:
    """
    Custom mixin that checks a test case and redirects the user to a
    URL named "thank-you"
    if the test case is true.
    """

    def test_case(self):
        return (
            self.request.user.is_locked if self.request.user.is_authenticated else False
        )

    def dispatch(self, request, *args, **kwargs):
        print("CheckUserLockMixin is being executed")
        if self.test_case():
            return redirect(reverse("thank-you"))
        return super().dispatch(request, *args, **kwargs)

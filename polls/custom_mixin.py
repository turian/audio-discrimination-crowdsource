from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect


class CheckUserLockMixin:
    """evaluates 'check_user_is_locked'
    if 'check_user_is_locked' returns True redirects to 'thank-you' page
    """

    redirect_url = "thank-you"

    def get_redirect_url(self):
        """
        Override this method to override the redirect_url attribute.
        """
        redirect_url = self.redirect_url
        if not redirect_url:
            raise ImproperlyConfigured(
                "{0} is missing the redirect_url attribute. "
                "Define {0}.redirect_url or override "
                "{0}.get_redirect_url().".format(self.__class__.__name__)
            )
        return str(redirect_url)

    def check_user_is_locked(self):
        raise NotImplementedError(
            "{0} is missing the implementation of the test_func() method.".format(
                self.__class__.__name__
            )
        )

    def get_test_func(self):
        """
        Override this method to use a different test_func method.
        """
        return self.check_user_is_locked

    def dispatch(self, request, *args, **kwargs):
        test_result = self.get_test_func()()
        if test_result:
            return redirect(self.get_redirect_url())
        return super().dispatch(request, *args, **kwargs)

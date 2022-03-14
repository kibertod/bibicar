"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'carsharing.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'carsharing.dashboard.CustomAppIndexDashboard'

"""

from jwt_auth.models import *
from api.models import *

try:
    # we use django.urls import as version detection as it will fail on django 1.11 and thus we are safe to use
    # gettext_lazy instead of ugettext_lazy instead
    from django.urls import reverse
    from django.utils.translation import gettext_lazy as _
except ImportError:
    from django.core.urlresolvers import reverse
    from django.utils.translation import ugettext_lazy as _
from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name

class MyModule(modules.DashboardModule):
    def __init__(self, title, model, base_url, **kwargs):
        super(MyModule, self).__init__(**kwargs)
        self.template = 'last_records.html'
        self.base_url = base_url
        self.title = title
        self.records = model.objects.all()[:10]

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for carsharing.
    """
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('django.contrib.*',),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('Администраторы'),
            models=('django.contrib.*',),
        ))

        self.children.append(modules.LinkList(
            layout='stacked',
            title="Новые пользователи",
            children=[[str(record) + "\t" + str(record.created), f"jwt_auth/profile/{record.id}/change/"] for record in list(sorted(Profile.objects.all(), key=lambda record: record.created, reverse=True))[:10]]
        ))

        self.children.append(modules.LinkList(
            layout='stacked',
            title="Последние отзывы",
            children=[[str(record) + "\t" + str(record.created), f"api/review/{record.id}/change/"] for record in list(sorted(Review.objects.all(), key=lambda record: record.created, reverse=True))[:10]]
        ))

        self.children.append(modules.LinkList(
            layout='stacked',
            title="Последние обьявления",
            children=[[str(record) + "\t" + str(record.created), f"api/car/{record.id}/change/"] for record in list(sorted(Car.objects.all(), key=lambda record: record.created, reverse=True))[:10]]
        ))

class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for carsharing.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)

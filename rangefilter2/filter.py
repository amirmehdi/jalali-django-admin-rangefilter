# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import django

try:
    import pytz
except ImportError:
    pytz = None

try:
    import csp
except ImportError:
    csp = None

from collections import OrderedDict

from persiantools.jdatetime import JalaliDate

from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.templatetags.static import StaticNode
from django.utils.encoding import force_str
from jalali_date.widgets import AdminJalaliDateWidget, AdminSplitJalaliDateTime
from jalali_date.fields import JalaliDateField, SplitJalaliDateTimeField

if django.VERSION >= (2, 0, 0):
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _


class DateRangeFilter(admin.filters.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_gte = '{0}__gte'.format(field_path)
        self.lookup_kwarg_lte = '{0}__lte'.format(field_path)
        if 'fa' in request.LANGUAGE_CODE.lower():
            self.locale = 'persian'
        else:
            self.locale = 'gregorian'

        super().__init__(
            field, request, params, model, model_admin, field_path)
        self.request = request

        temp = self.used_parameters.copy()
        self.value1 = ''
        self.value2 = ''
        for key, value in temp.items():
            if value and key in [self.lookup_kwarg_gte, self.lookup_kwarg_lte]:
                try:
                    ret = int(value)/1000
                    # if self.local
                    date = datetime.datetime.fromtimestamp(ret)
                    self.used_parameters[key] = str(date)
                    if key == self.lookup_kwarg_gte:
                        if self.locale is 'persian':
                            self.value1 = JalaliDate.fromtimestamp(
                                ret).strftime("%Y-%m-%d")
                        else:
                            self.value1 = date.strftime("%Y-%m-%d")
                    else:
                        if self.locale is 'persian':
                            self.value2 = JalaliDate.fromtimestamp(
                                ret).strftime("%Y-%m-%d")
                        else:
                            self.value2 = date.strftime("%Y-%m-%d")
                except Exception as e:
                    continue
            else:
                self.used_parameters.pop(key, None)

    def get_timezone(self, request):
        return timezone.get_default_timezone()

    @staticmethod
    def make_dt_aware(value, timezone):
        if settings.USE_TZ and pytz is not None:
            default_tz = timezone
            if value.tzinfo is not None:
                value = default_tz.normalize(value)
            else:
                value = default_tz.localize(value)
        return value

    def choices(self, cl):
        yield {
            # slugify converts any non-unicode characters to empty characters
            # but system_name is required, if title converts to empty string use id
            # https://github.com/silentsokolov/django-admin-rangefilter/issues/18
            'date_start': self.value1 or '',
            'date_end': self.value2 or '',
            'system_name': force_str(slugify(self.title) if slugify(self.title) else id(self.title)),
            'query_string': cl.get_query_string(
                {}, remove=self.expected_parameters()
            )
        }

    def expected_parameters(self):
        return [self.lookup_kwarg_gte, self.lookup_kwarg_lte]

    def get_template(self):
        if django.VERSION[:2] <= (1, 8):
            return 'rangefilter2/date_filter_1_8.html'
        else:
            # if csp:
            #    return 'rangefilter2/date_filter_csp.html'
            return 'rangefilter2/date_filter.html'

    template = property(get_template)

    @property
    def media(self):
        debug = settings.DEBUG
        if debug:
            extension = '.min'
        else:
            extension = ''
        js = (
            'rangefilter2/persian-date{}.js'.format(extension),
            'rangefilter2/persian-datepicker{}.js'.format(extension),
        )
        css = {
            'all': (
                'rangefilter2/persian-datepicker{}.css'.format(extension)
            )
        }
        return forms.Media(js=js, css=css)

    def queryset(self, request, queryset):
        try:
            params = {}
            if self.value1:
                params[self.lookup_kwarg_gte] = self.value1
            if self.value2:
                params[self.lookup_kwarg_lte] = self.value2
            return queryset.filter(**params)
        except (ValueError, ValidationError) as e:
            # Fields may raise a ValueError or ValidationError when converting
            # the parameters to the correct type.
            raise IncorrectLookupParameters(e)


class DateTimeRangeFilter(DateRangeFilter):

    def _get_expected_fields(self):
        expected_fields = []
        for field in [self.lookup_kwarg_gte, self.lookup_kwarg_lte]:
            for i in range(2):
                expected_fields.append('{}_{}'.format(field, i))

        return expected_fields

    def _get_form_fields(self):
        return OrderedDict(
            (
                (self.lookup_kwarg_gte, SplitJalaliDateTimeField(
                    label='',
                    widget=AdminSplitJalaliDateTime(
                        attrs={'placeholder': _('From date')}),
                    localize=True,
                    required=False
                )),
                (self.lookup_kwarg_lte, SplitJalaliDateTimeField(
                    label='',
                    widget=AdminSplitJalaliDateTime(
                        attrs={'placeholder': _('To date')}),
                    localize=True,
                    required=False
                )),
            )
        )

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            date_value_gte = self.JalaliToGregorian(date_value_gte)
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                date_value_gte, self.get_timezone(request)
            )
        if date_value_lte:
            date_value_lte = self.JalaliToGregorian(date_value_lte)
            query_params['{0}__lte'.format(self.field_path)] = self.make_dt_aware(
                date_value_lte, self.get_timezone(request)
            )

        return query_params

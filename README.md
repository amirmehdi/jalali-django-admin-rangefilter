jalali-django-admin-rangefilter
========================

jalali-django-admin-rangefilter app, add the filter by a custom date / datetime range on the admin UI. This is a multilingual daterange filter for django admin and it is inspired by django-admin-rangefilter.
To see the jalali calendar, make sure request's LANGUAGE_CODE contains 'fa' ('fa' for Farsi).


Requirements
------------

* Python 3.5+
* Django 3.0+


Installation
------------

Use your favorite Python package manager to install the app from PyPI, e.g.

Example:

``pip install jalali-django-admin-rangefilter``


Add ``rangefilter`` to ``INSTALLED_APPS``:

Example:

```python

    INSTALLED_APPS = (
        ...
        'rangefilter',
        ...
    )
```


Example usage
-------------

In admin
-------------

```python

    from django.contrib import admin
    from rangefilter.filter import DateRangeFilter

    from .models import Post


    @admin.register(Post)
    class PostAdmin(admin.ModelAdmin):
        list_filter = (
            ('created_at', DateRangeFilter),
        )
```

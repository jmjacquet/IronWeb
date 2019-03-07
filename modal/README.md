# django-modal
modal windows for django / bootstrap3


Requires jQuery and Bootstrap. Depends on django-crispy-forms on server side.
This app allows to make responsive AJAX modal forms for displaying, creating, editing, deleting objects in Django.

This is a more generic approach to adding modal windows, based on https://github.com/FZambia/django-fm


###Install.###

Add the files to your app folder.
install crispy_forms.

Add crispy_forms and modal to INSTALLED_APPS:
```
INSTALLED_APPS = (
    ...
    'crispy_forms',
    'modal',
)
```
Also in settings.py set crispy template pack to bootstrap3:

CRISPY_TEMPLATE_PACK = 'bootstrap3'

Include modal template into your project template and initialize jQuery plugin:
```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css"/>
        <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
        <script type="text/javascript" src="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
    </head>
    <body>
        {% block content %}{% endblock %}
        {% include "modal/modal.html" %}
        
        <script src="{% static 'modal/js/modal.js' %}"></script>
        <script type="text/javascript">
            $(function() {
                $.modal({debug: false});
            });
        </script>
    </body>
</html>
```

There are 4 class-based views in django-modal to inherit from when you want AJAX forms:

-    AjaxCreateView
-    AjaxUpdateView
-    AjaxDeleteView
-    Detailview (generic.detail)

Example: 
```
    class BookDelete(AjaxDeleteView):
        model   = Location
        template_name   = "template/book_delete.html"
        slug_field      = 'id'
        slug_url_kwarg  = 'book_id'
        success_url     = reverse_lazy('books_list')
```



In templates  create links to create, update, delete resources with special class
 - modal-detail
 - modal-create
 - modal-update
 - modal-delete


Examples: 
```html
    <a href="{% url 'book_detail' book.id %}" class="modal-detail" data-modal-head="" data-modal-callback="reload" >show detail </a>
    <a href="{% url 'book_delete' book.id  %}" class="btn btn-default modal-delete" data-modal-head="" data-modal-callback="reload"
                           role="button"> <span class="glyphicon glyphicon-remove-sign" aria-hidden="true"></span></a>
```

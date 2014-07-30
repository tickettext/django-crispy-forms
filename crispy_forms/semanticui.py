from random import randint

from django.template import Context, Template
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify

from .compatibility import text_type
from .layout import LayoutObject, Field, Div, Button
from .utils import render_field, flatatt, TEMPLATE_PACK



class TwoFields(LayoutObject):
    """
    Semantic UI form object. It wraps 2 form fields in a <div class="two fields">

    Example::

        TwoFields(
            HTML(<span style="display: hidden;">Information Saved</span>),
            Submit('Save', 'Save', css_class='ui button')
        )
    """
    template = "%s/layout/twofields.html"

    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)
        self.template = kwargs.pop('template', self.template)
        self.attrs = kwargs
        if 'css_class' in self.attrs:
            self.attrs['class'] = self.attrs.pop('css_class')

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        html = u''
        for field in self.fields:
            html += render_field(field, form, form_style, context, template_pack=template_pack, **kwargs)
        extra_context = {
            'twofields': self,
            'fields_output': html
        }
        template = self.template % template_pack
        return render_to_string(template, extra_context, context)

    def flat_attrs(self):
        return flatatt(self.attrs)

class ButtonAppendedIcon(Div):
    template = "%s/appended_icon.html"

    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)

        if hasattr(self, 'css_class') and 'css_class' in kwargs or hasattr(self, 'icon_class') and 'icon_class' in kwargs:
            self.css_class += ' %s' % kwargs.pop('css_class')
            self.icon_class += ' %s' % kwargs.pop('icon_class')
        if not hasattr(self, 'css_class'):
            self.css_class = kwargs.pop('css_class', None)
            self.icon_class = kwargs.pop('icon_class', None)

        self.css_id = kwargs.pop('css_id', '')
        self.button_text = kwargs.pop('button_text', '')
        self.template = kwargs.pop('template', self.template)
        self.flat_attrs = flatatt(kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        fields = ''
        for field in self.fields:
            fields += render_field(
                field, form, form_style, context, template_pack=template_pack, **kwargs
            )

        template = self.template % template_pack
        return render_to_string(template, {'icon_appended': self, 'fields': fields})



class PrependedAppendedText(Field):
    template = "%s/layout/prepended_appended_text.html"

    def __init__(self, field, prepended_text=None, appended_text=None, *args, **kwargs):
        self.field = field
        self.appended_text = appended_text
        self.prepended_text = prepended_text
        if 'active' in kwargs:
            self.active = kwargs.pop('active')
            
        #SO FAR IT ONLY APPENDS ASTERISK    
        #self.input_size = None
        #css_class = kwargs.get('css_class', '')
        #if css_class.find('input-lg') != -1: self.input_size = 'input-lg'
        #if css_class.find('input-sm') != -1: self.input_size = 'input-sm'

        super(PrependedAppendedText, self).__init__(field, *args, **kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
        # THIS EXTRA CONTEXT IS DISABLED FOR NOW
        #extra_context = {
        #    'crispy_appended_text': self.appended_text,
        #    'crispy_prepended_text': self.prepended_text,
        #    'input_size' : self.input_size,
        #    'active': getattr(self, "active", False)
        #}
        template = self.template % template_pack
        return render_field(
            self.field, form, form_style, context,
            template=template, attrs=self.attrs,
            #template_pack=template_pack, extra_context=extra_context, **kwargs
            template_pack=template_pack, **kwargs
        )
    
class AppendedText(PrependedAppendedText):
    def __init__(self, field, text, *args, **kwargs):
        kwargs.pop('appended_text', None)
        kwargs.pop('prepended_text', None)
        self.text = text
        super(AppendedText, self).__init__(field, appended_text=text, **kwargs)



class FormActions(LayoutObject):
    """
    Bootstrap layout object. It wraps fields in a <div class="form-actions">

    Example::

        FormActions(
            HTML(<span style="display: hidden;">Information Saved</span>),
            Submit('Save', 'Save', css_class='btn-primary')
        )
    """
    template = "%s/layout/formactions.html"

    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)
        self.template = kwargs.pop('template', self.template)
        self.attrs = kwargs
        if 'css_class' in self.attrs:
            self.attrs['class'] = self.attrs.pop('css_class')

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        html = u''
        for field in self.fields:
            html += render_field(field, form, form_style, context, template_pack=template_pack, **kwargs)
        extra_context = {
            'formactions': self,
            'fields_output': html
        }
        template = self.template % template_pack
        return render_to_string(template, extra_context, context)

    def flat_attrs(self):
        return flatatt(self.attrs)



class Segment(Div):
    """
    Base class used for `Tab` and `AccordionGroup`, represents a basic container concept
    """
    css_class = ""

    def __init__(self, name, *fields, **kwargs):
        super(Container, self).__init__(*fields, **kwargs)
        self.template = kwargs.pop('template', self.template)
        self.name = name
        self._active_originally_included = "active" in kwargs
        self.active = kwargs.pop("active", False)
        if not self.css_id:
            self.css_id = slugify(self.name)

    def __contains__(self, field_name):
        """
        check if field_name is contained within tab.
        """
        return field_name in map(lambda pointer: pointer[1], self.get_field_names())

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        if self.active:
            if not 'active' in self.css_class:
                self.css_class += ' active'
        else:
            self.css_class = self.css_class.replace('active', '')
        return super(Container, self).render(form, form_style, context, template_pack)


class Modal(Div):
    """
    `Alert` generates markup in the form of an alert dialog

        Alert(content='<strong>Warning!</strong> Best check yo self, you're not looking too good.')
    """
    template = "%s/layout/alert.html"
    css_class = "alert"

    def __init__(self, content, dismiss=True, block=False, **kwargs):
        fields = []
        if block:
            self.css_class += ' alert-block'
        Div.__init__(self, *fields, **kwargs)
        self.template = kwargs.pop('template', self.template)
        self.content = content
        self.dismiss = dismiss

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        template = self.template % template_pack
        return render_to_string(
            template,
            {'alert': self, 'content': self.content, 'dismiss': self.dismiss},
            context
        )


class Dimmer(Div):
    """
    `Alert` generates markup in the form of an alert dialog

        Alert(content='<strong>Warning!</strong> Best check yo self, you're not looking too good.')
    """
    template = "%s/layout/alert.html"
    css_class = "alert"

    def __init__(self, content, dismiss=True, block=False, **kwargs):
        fields = []
        if block:
            self.css_class += ' alert-block'
        Div.__init__(self, *fields, **kwargs)
        self.template = kwargs.pop('template', self.template)
        self.content = content
        self.dismiss = dismiss

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        template = self.template % template_pack
        return render_to_string(
            template,
            {'alert': self, 'content': self.content, 'dismiss': self.dismiss},
            context
        )

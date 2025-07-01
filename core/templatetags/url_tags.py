from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag
def namespaced_url(viewname, *args, **kwargs):
    """
    Tries to resolve a URL with the 'core:' namespace first, and falls back to without namespace if that fails.
    This helps during the transition period when templates might still reference non-namespaced URLs.
    """
    try:
        # Try with the core namespace first
        return reverse(f'core:{viewname}', args=args, kwargs=kwargs)
    except NoReverseMatch:
        # If that fails, try without namespace (for URLs in other apps)
        try:
            return reverse(viewname, args=args, kwargs=kwargs)
        except NoReverseMatch:
            # If that also fails, try with other common namespaces
            for namespace in ['appointments', 'treatments', 'telemedicine']:
                try:
                    return reverse(f'{namespace}:{viewname}', args=args, kwargs=kwargs)
                except NoReverseMatch:
                    continue
            # If all attempts fail, raise the original error
            raise

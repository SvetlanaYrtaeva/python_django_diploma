from .models import Category


def global_context(request):
    categories = (
        Category.objects.active()
        .filter(is_active=True, parent__isnull=True)
        .prefetch_related("children")
    )

    return {
        "menu_categories": categories,
    }

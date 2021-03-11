from django import template


def set_admin_wrapper_template(context):
    try:
        extra_template = "userservice/user_override_extra_info.html"
        template.loader.get_template(extra_template)
        context['has_extra_template'] = True
        context['extra_template'] = 'userservice/user_override_extra_info.html'
    except template.TemplateDoesNotExist:
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass

    try:
        template.loader.get_template("userservice/user_override_wrapper.html")
        context['wrapper_template'] = 'userservice/user_override_wrapper.html'
    except template.TemplateDoesNotExist:
        context['wrapper_template'] = 'support_wrapper.html'
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass

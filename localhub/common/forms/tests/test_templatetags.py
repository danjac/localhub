# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.forms import Form

from localhub.common.forms.templatetags import simple_ajax_form


class TestSimpleAjaxForm:
    def test_simple_ajax_form(self, rf):
        class MyForm(Form):
            ...

        form = MyForm()
        req = rf.get("/some-action/")
        context = simple_ajax_form({"request": req}, form)
        assert context["action"] == "/some-action/"
        assert context["form"] == form

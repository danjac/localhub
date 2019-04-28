from communikit.content.forms import PostForm


class TestPostForm:
    def test_url_missing(self):

        form = PostForm(
            {"title": "something", "url": "", "description": "test"}
        )

        assert form.is_valid()

    def test_description_missing(self):

        form = PostForm(
            {
                "title": "something",
                "url": "http://google.com",
                "description": "",
            }
        )

        assert form.is_valid()

    def test_description_and_url_both_missing(self):

        form = PostForm({"title": "something", "url": "", "description": ""})

        assert not form.is_valid()

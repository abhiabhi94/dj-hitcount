from blog.models import Post
from hitcount.conf import settings
from hitcount.models import HitCount
from hitcount.utils import _get_model_from_string
from hitcount.utils import get_hitcount_model
from hitcount.utils import get_ip


class TestGetIP:
    def test_x_forwared_not_set(self, rf):
        ip = get_ip(rf.get('/'))

        assert ip == '127.0.0.1'

    def test_x_forwarded_set(self, rf):
        rf.defaults['HTTP_X_FORWARDED_FOR'] = '203.0.113.195'

        ip = get_ip(rf.get('/'))

        assert ip == '203.0.113.195'

    def test_neither_remote_addr_nor_x_forwarded_set(self, rf):
        rf.defaults['REMOTE_ADDR'] = ''

        ip = get_ip(rf.get('/'))

        assert ip == ''

    def test_bogus_ip_format(self, rf):
        rf.defaults['REMOTE_ADDR'] = '22.A2.22.22'

        ip = get_ip(rf.get('/'))

        assert ip == '10.0.0.1'


class TestGetModelFromString:
    def test(self):
        assert _get_model_from_string('hitcount.HitCount') == HitCount


class TestGetHitCountModel:

    def test(self, monkeypatch):
        monkeypatch.setattr(settings, 'HITCOUNT_HITCOUNT_MODEL', 'blog.Post')

        assert get_hitcount_model() == Post

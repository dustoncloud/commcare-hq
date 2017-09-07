# coding: utf-8
import contextlib

from django.test import TestCase

from corehq.apps.users.models import WebUser
from corehq.apps.domain.shortcuts import create_domain
from django.test.client import Client
from django.urls import reverse
import os

from corehq.const import OPENROSA_VERSION_2, OPENROSA_VERSION_3
from corehq.form_processor.interfaces.dbaccessors import FormAccessors
from corehq.form_processor.tests.utils import use_sql_backend, FormProcessorTestUtils
from corehq.middleware import OPENROSA_VERSION_HEADER
from corehq.util.test_utils import flag_enabled, TestFileMixin
from couchforms.models import UnfinishedSubmissionStub
from dimagi.utils.post import tmpfile
from couchforms.signals import successful_form_received


class SubmissionErrorTest(TestCase, TestFileMixin):
    file_path = ('data',)
    root = os.path.dirname(__file__)

    def setUp(self):
        self.domain = create_domain("submit-errors")
        self.couch_user = WebUser.create(None, "test", "foobar")
        self.couch_user.add_domain_membership(self.domain.name, is_admin=True)
        self.couch_user.save()
        self.client = Client()
        self.client.login(**{'username': 'test', 'password': 'foobar'})
        self.url = reverse("receiver_post", args=[self.domain])
        FormProcessorTestUtils.delete_all_xforms(self.domain.name)

    def tearDown(self):
        self.couch_user.delete()
        self.domain.delete()
        FormProcessorTestUtils.delete_all_cases_forms_ledgers(self.domain.name)
        UnfinishedSubmissionStub.objects.all().delete()

    def _submit(self, formname, open_rosa_header=None):
        open_rosa_header = open_rosa_header or OPENROSA_VERSION_2
        file_path = self.get_path(formname, '')
        with open(file_path, "rb") as f:
            res = self.client.post(
                self.url,
                {"xml_submission_file": f},
                ** {OPENROSA_VERSION_HEADER: open_rosa_header}
            )
            return file_path, res

    def testSubmitBadAttachmentType(self):
        res = self.client.post(self.url, {
                "xml_submission_file": "this isn't a file"
        })
        self.assertEqual(400, res.status_code)
        #self.assertIn("xml_submission_file", res.content)

    def testSubmitDuplicate(self):
        file, res = self._submit('simple_form.xml')
        self.assertEqual(201, res.status_code)
        self.assertIn(u"   √   ".encode('utf-8'), res.content)

        file, res = self._submit('simple_form.xml')
        self.assertEqual(201, res.status_code)

        _, res_openrosa3 = self._submit('simple_form.xml', open_rosa_header=OPENROSA_VERSION_3)
        self.assertEqual(201, res_openrosa3.status_code)

        self.assertIn("Form is a duplicate", res.content)

        # make sure we logged it
        [log] = FormAccessors(self.domain.name).get_forms_by_type('XFormDuplicate', limit=1)

        self.assertIsNotNone(log)
        self.assertIn("Form is a duplicate", log.problem)
        with open(file) as f:
            self.assertEqual(f.read(), log.get_xml())

    def _test_submission_error_post_save(self, open_rosa_version, expected_response_code):
        evil_laugh = "mwa ha ha!"
        with failing_signal_handler(evil_laugh):
            file, res = self._submit("simple_form.xml", open_rosa_version)
            self.assertEqual(expected_response_code, res.status_code)

            form_id = 'ad38211be256653bceac8e2156475664'
            form = FormAccessors(self.domain.name).get_form(form_id)
            self.assertTrue(form.is_normal)
            self.assertTrue(form.initial_processing_complete)
            stubs = UnfinishedSubmissionStub.objects.filter(domain=self.domain).all()
            self.assertEqual(1, len(stubs))
            self.assertEqual(form_id, stubs[0].xform_id)
            self.assertEqual(True, stubs[0].saved)

    def test_submission_error_post_save_2_0(self):
        self._test_submission_error_post_save(OPENROSA_VERSION_2, 201)

    def test_submission_error_post_save_3_0(self):
        self._test_submission_error_post_save(OPENROSA_VERSION_3, 422)

    def testSubmitBadXML(self):
        f, path = tmpfile()
        with f:
            f.write("this isn't even close to xml")
        with open(path) as f:
            res = self.client.post(self.url, {
                    "xml_submission_file": f
            })
            self.assertEqual(500, res.status_code)
            self.assertIn('Invalid XML', res.content)

        # make sure we logged it
        [log] = FormAccessors(self.domain.name).get_forms_by_type('SubmissionErrorLog', limit=1)

        self.assertIsNotNone(log)
        self.assertIn('Invalid XML', log.problem)
        self.assertEqual("this isn't even close to xml", log.get_xml())
        self.assertEqual(log.form_data, {})

    def test_missing_xmlns(self):
        file, res = self._submit('missing_xmlns.xml')
        self.assertEqual(500, res.status_code)
        message = "Form is missing a required field: XMLNS"
        self.assertIn(message, res.content)

        # make sure we logged it
        [log] = FormAccessors(self.domain.name).get_forms_by_type('SubmissionErrorLog', limit=1)

        self.assertIsNotNone(log)
        self.assertIn(message, log.problem)
        with open(file) as f:
            self.assertEqual(f.read(), log.get_xml())

    @flag_enabled('DATA_MIGRATION')
    def test_data_migration(self):
        file, res = self._submit('simple_form.xml')
        self.assertEqual(503, res.status_code)
        message = "Service Temporarily Unavailable"
        self.assertIn(message, res.content)


@use_sql_backend
class SubmissionErrorTestSQL(SubmissionErrorTest):
    pass


@contextlib.contextmanager
def failing_signal_handler(error_message):
    def fail(sender, xform, **kwargs):
        raise Exception(error_message)

    successful_form_received.connect(fail)

    try:
        yield
    finally:
        successful_form_received.disconnect(fail)

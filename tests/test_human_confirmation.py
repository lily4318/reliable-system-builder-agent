import unittest
from src import human_confirmation as h


class HumanConfirmationRegression(unittest.TestCase):
    def setUp(self):
        self.items=[{'id':'A','label':'A','proposed_text':'First draft'},
                    {'id':'B','label':'B','proposed_text':'Second draft'}]
        self.draft=h.select(h.new_review(self.items),'A')

    def test_confirmation_requires_literal_boolean_true(self):
        for value in (False, None, 'false', 'true', 1, [True], {'click':True}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                h.confirm(self.draft,value)
        confirmed=h.confirm(h.edit(self.draft,'Edited draft'),True)
        self.assertEqual(confirmed['confirmed_text'],'Edited draft')
        self.assertTrue(confirmed['explicit_confirmation_received'])
        self.assertFalse(confirmed['sent'])
        self.assertFalse(confirmed['approval_granted'])

    def test_reselect_invalidates_old_confirmation(self):
        confirmed=h.confirm(self.draft,True)
        second=h.select(confirmed,'B')
        self.assertNotIn('confirmed_text',second)
        self.assertFalse(second['explicit_confirmation_received'])
        self.assertEqual(second['editable_text'],'Second draft')
        self.assertEqual(h.confirm(second,True)['confirmed_text'],'Second draft')
        self.assertEqual(confirmed['confirmed_text'],'First draft')

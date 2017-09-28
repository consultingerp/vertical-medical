# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tests.common import SingleTransactionCase


class MedicalTestLuhn(models.Model):
    _name = 'medical.test.luhn'
    _inherit = 'medical.abstract.luhn'
    ref = fields.Char()
    country_id = fields.Many2one('res.country')

    @api.multi
    @api.constrains('ref')
    def _check_ref(self):
        self._luhn_constrains_helper('ref')


class MedicalLuhnAbstractTestMixer(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(MedicalLuhnAbstractTestMixer, cls).setUpClass()

        cls.registry.enter_test_mode()
        cls.old_cursor = cls.cr
        cls.cr = cls.registry.cursor()
        cls.env = api.Environment(cls.cr, cls.uid, {})

        MedicalTestLuhn._build_model(cls.registry, cls.cr)
        cls.model_obj = cls.env[MedicalTestLuhn._name].with_context(todo=[])
        cls.model_obj._prepare_setup()
        cls.model_obj._setup_base(partial=False)
        cls.model_obj._setup_fields(partial=False)
        cls.model_obj._setup_complete()
        cls.model_obj._auto_init()
        cls.model_obj.init()
        cls.model_obj._auto_end()

        cls.valid = [
            4532015112830366,
            6011514433546201,
            6771549495586802,
        ]
        cls.invalid = [
            4531015112830366,
            6011514438546201,
            1771549495586802,
        ]
        cls.country_us = cls.env['res.country'].search([
            ('code', '=', 'US'),
        ],
            limit=1,
        )

    @classmethod
    def tearDownClass(cls):
        del cls.registry.models[MedicalTestLuhn._name]
        cls.registry.leave_test_mode()
        cls.cr = cls.old_cursor
        cls.env = api.Environment(cls.cr, cls.uid, {})

        super(MedicalLuhnAbstractTestMixer, cls).tearDownClass()


class TestMedicalLuhnAbstract(MedicalLuhnAbstractTestMixer):

    def test_valid_int(self):
        """ Test _luhn_is_valid returns True if valid int input """
        for i in self.valid:
            self.assertTrue(
                self.model_obj._luhn_is_valid(i),
                'Luhn validity check on int %s did not pass for valid' % i,
            )

    def test_valid_str(self):
        """ Test _luhn_is_valid returns True if valid str input """
        for i in self.valid:
            self.assertTrue(
                self.model_obj._luhn_is_valid(str(i)),
                'Luhn validity check on str %s did not pass for valid' % i,
            )

    def test_invalid_int(self):
        """ Test _luhn_is_valid returns False if invalid int input """
        for i in self.invalid:
            self.assertFalse(
                self.model_obj._luhn_is_valid(i),
                'Luhn validity check on int %s did not fail for invalid' % i,
            )

    def test_invalid_str(self):
        """ Test _luhn_is_valid returns False if invalid str input """
        for i in self.invalid:
            self.assertFalse(
                self.model_obj._luhn_is_valid(str(i)),
                'Luhn validity check on str %s did not fail for invalid' % i,
            )

    def test_false(self):
        """ Test _luhn_is_valid fails greacefully if given no/Falsey input """
        self.assertFalse(
            self.model_obj._luhn_is_valid(False),
            'Luhn validity check on False did not fail gracefully',
        )

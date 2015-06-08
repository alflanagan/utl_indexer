#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lex`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

from testplus import unittest_plus

from utl_lib.utl_lex import UTLLexer


class LexerTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~utl_lex.Lexer`."""

    _MACRO_DEF = '''
    [%-

    call cms.component.load('core_base_editorial');
    call cms.component.load("core_base_user");

    /**
     * Subscription assets list
     */
    macro core_base_library_subscriptionAssetsList();
        /* get asset types for subscription from standard */
        something = 5 * 3;
        subscriptionAssets = core_base_library_getCustomProperty('varName':'subscription_assets',
                                'varDefault':'article,edition,page');

        /* array w/multiple types */
        fred = [1, 2.3, 'hello', false, "goodbye", null]
    %]
    OK, it's weird to put text in the middle of a macro def
    but you COULD if you wanted to
    and, of course, you can embed [% something %] on one line
    on the other hand, it could just [ be a left bracket
    [%
         /* manage mobile asset subscription types (list, none, or defer to standard) */
         if cms.system.mobile || cms.request.param('mode') == 'jqm';
             something = 5 * 7/(8+2)-23
            /* gather the list for mobile */
            subscriptionAssetsMobile = core_base_library_getCustomProperty(
                 'varName':'subscription_assets_mobile');

            /* if the list exists and is not defer */
            if subscriptionAssetsMobile != null && subscriptionAssetsMobile != 'defer';
                /* use the mobile list */
                subscriptionAssets = subscriptionAssetsMobile;
            end;
        end;
        return subscriptionAssets;
    end;

    %]'''

    _EXPECTED = [('DOCUMENT', '\n    '),
                 ('START_UTL', '[%-'),
                 ('CALL', 'call'),
                 ('CMS', 'cms'),
                 ('OP', '.'),
                 ('ID', 'component'),
                 ('OP', '.'),
                 ('ID', 'load'),
                 ('RPAREN', '('),
                 ('STRING', 'core_base_editorial'),
                 ('LPAREN', ')'),
                 ('SEMI', ';'),
                 ('CALL', 'call'),
                 ('CMS', 'cms'),
                 ('OP', '.'),
                 ('ID', 'component'),
                 ('OP', '.'),
                 ('ID', 'load'),
                 ('RPAREN', '('),
                 ('STRING', 'core_base_user'),
                 ('LPAREN', ')'),
                 ('SEMI', ';'),
                 ('MACRO', 'macro'),
                 ('ID', 'core_base_library_subscriptionAssetsList'),
                 ('RPAREN', '('),
                 ('LPAREN', ')'),
                 ('SEMI', ';'),
                 ('ID', 'something'),
                 ('ASSIGN', '='),
                 ('NUMBER', 5.0),
                 ('TIMES', '*'),
                 ('NUMBER', 3.0),
                 ('SEMI', ';'),
                 ('ID', 'subscriptionAssets'),
                 ('ASSIGN', '='),
                 ('ID', 'core_base_library_getCustomProperty'),
                 ('RPAREN', '('),
                 ('STRING', 'varName'),
                 ('OP', ':'),
                 ('STRING', 'subscription_assets'),
                 ('COMMA', ','),
                 ('STRING', 'varDefault'),
                 ('OP', ':'),
                 ('STRING', 'article,edition,page'),
                 ('LPAREN', ')'),
                 ('SEMI', ';'),
                 ('ID', 'fred'),
                 ('ASSIGN', '='),
                 ('OP', '['),
                 ('NUMBER', 1.0),
                 ('COMMA', ','),
                 ('NUMBER', 2.3),
                 ('COMMA', ','),
                 ('STRING', 'hello'),
                 ('COMMA', ','),
                 ('FALSE', 'false'),
                 ('COMMA', ','),
                 ('STRING', 'goodbye'),
                 ('COMMA', ','),
                 ('NULL', 'null'),
                 ('RBRACKET', ']'),
                 ('END_UTL', '%]'),
                 ('DOCUMENT', ("\n    OK, it's weird to put text in the middle of a macro def\n"
                               "    but you COULD if you wanted to\n    and, of course, you"
                               " can embed ")),
                 ('START_UTL', '[%'),
                 ('ID', 'something'),
                 ('END_UTL', '%]'),
                 ('DOCUMENT', 'on one line\n    on the other hand, it could just '),
                 ('DOCUMENT', '['),
                 ('DOCUMENT', 'be a left bracket\n    '),
                 ('START_UTL', '[%'),
                 ('IF', 'if'),
                 ('CMS', 'cms'),
                 ('OP', '.'),
                 ('ID', 'system'),
                 ('OP', '.'),
                 ('ID', 'mobile'),
                 ('OP', '||'),
                 ('CMS', 'cms'),
                 ('OP', '.'),
                 ('ID', 'request'),
                 ('OP', '.'),
                 ('ID', 'param'),
                 ('RPAREN', '('),
                 ('STRING', 'mode'),
                 ('LPAREN', ')'),
                 ('OP', '=='),
                 ('STRING', 'jqm'),
                 ('SEMI', ';'),
                 ('ID', 'something'),
                 ('ASSIGN', '='),
                 ('NUMBER', 5.0),
                 ('TIMES', '*'),
                 ('NUMBER', 7.0),
                 ('DIV', '/'),
                 ('RPAREN', '('),
                 ('NUMBER', 8.0),
                 ('PLUS', '+'),
                 ('NUMBER', 2.0),
                 ('LPAREN', ')'),
                 ('MINUS', '-'),
                 ('NUMBER', 23.0),
                 ('ID', 'subscriptionAssetsMobile'),
                 ('ASSIGN', '='),
                 ('ID', 'core_base_library_getCustomProperty'),
                 ('RPAREN', '('),
                 ('STRING', 'varName'),
                 ('OP', ':'),
                 ('STRING', 'subscription_assets_mobile'),
                 ('LPAREN', ')'),
                 ('SEMI', ';'),
                 ('IF', 'if'),
                 ('ID', 'subscriptionAssetsMobile'),
                 ('OP', '!'),
                 ('ASSIGN', '='),
                 ('NULL', 'null'),
                 ('OP', '&&'),
                 ('ID', 'subscriptionAssetsMobile'),
                 ('OP', '!'),
                 ('ASSIGN', '='),
                 ('STRING', 'defer'),
                 ('SEMI', ';'),
                 ('ID', 'subscriptionAssets'),
                 ('ASSIGN', '='),
                 ('ID', 'subscriptionAssetsMobile'),
                 ('SEMI', ';'),
                 ('END', 'end'),
                 ('SEMI', ';'),
                 ('END', 'end'),
                 ('SEMI', ';'),
                 ('RETURN', 'return'),
                 ('ID', 'subscriptionAssets'),
                 ('SEMI', ';'),
                 ('END', 'end'),
                 ('SEMI', ';'),
                 ('END_UTL', '%]')]

    def test_create(self):
        """Unit test for :py:meth:`utl_lex.Lexer`."""
        lexer = UTLLexer()
        lexer.input(self._MACRO_DEF)

        index = 0
        tok = lexer.token()
        while tok:
            self.assertEqual(tok.type, self._EXPECTED[index][0])
            self.assertEqual(tok.value, self._EXPECTED[index][1])
            index += 1
            tok = lexer.token()


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:

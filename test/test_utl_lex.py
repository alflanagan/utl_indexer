#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lex`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

from testplus import unittest_plus

from utl_lib.utl_lex import UTLLexer, UTLLexerError


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
             something += 5 * 7/(8+2)-23
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
    for 1..10;
        echo 'fred';
    end;

    %]'''

    _EXPECTED = [('DOCUMENT', '\n    ', 1),  # token, text, line
                 ('START_UTL', '[%-', 2),
                 ('CALL', 'call', 4),
                 ('ID', 'cms', 4),
                 ('OP', '.', 4),
                 ('ID', 'component', 4),
                 ('OP', '.', 4),
                 ('ID', 'load', 4),
                 ('LPAREN', '(', 4),
                 ('STRING', 'core_base_editorial', 4),
                 ('RPAREN', ')', 4),
                 ('SEMI', ';', 4),
                 ('CALL', 'call', 5),
                 ('ID', 'cms', 5),
                 ('OP', '.', 5),
                 ('ID', 'component', 5),
                 ('OP', '.', 5),
                 ('ID', 'load', 5),
                 ('LPAREN', '(', 5),
                 ('STRING', 'core_base_user', 5),
                 ('RPAREN', ')', 5),
                 ('SEMI', ';', 5),
                 ('MACRO', 'macro', 10),
                 ('ID', 'core_base_library_subscriptionAssetsList', 10),
                 ('LPAREN', '(', 10),
                 ('RPAREN', ')', 10),
                 ('SEMI', ';', 10),
                 ('ID', 'something', 11),
                 ('ASSIGN', '=', 11),
                 ('NUMBER', 5.0, 11),
                 ('TIMES', '*', 11),
                 ('NUMBER', 3.0, 11),
                 ('SEMI', ';', 11),
                 ('ID', 'subscriptionAssets', 12),
                 ('ASSIGN', '=', 12),
                 ('ID', 'core_base_library_getCustomProperty', 12),
                 ('LPAREN', '(', 12),
                 ('STRING', 'varName', 12),
                 ('COLON', ':', 12),
                 ('STRING', 'subscription_assets', 12),
                 ('COMMA', ',', 12),
                 ('STRING', 'varDefault', 13),
                 ('COLON', ':'),
                 ('STRING', 'article,edition,page'),
                 ('RPAREN', ')'),
                 ('SEMI', ';'),
                 ('ID', 'fred'),
                 ('ASSIGN', '='),
                 ('LBRACKET', '['),
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
                 ('ID', 'cms'),
                 ('OP', '.'),
                 ('ID', 'system'),
                 ('OP', '.'),
                 ('ID', 'mobile'),
                 ('OP', '||'),
                 ('ID', 'cms'),
                 ('OP', '.'),
                 ('ID', 'request'),
                 ('OP', '.'),
                 ('ID', 'param'),
                 ('LPAREN', '('),
                 ('STRING', 'mode'),
                 ('RPAREN', ')'),
                 ('OP', '=='),
                 ('STRING', 'jqm'),
                 ('SEMI', ';'),
                 ('ID', 'something'),
                 ('ASSIGNOP', '+='),
                 ('NUMBER', 5.0),
                 ('TIMES', '*'),
                 ('NUMBER', 7.0),
                 ('DIV', '/'),
                 ('LPAREN', '('),
                 ('NUMBER', 8.0),
                 ('PLUS', '+'),
                 ('NUMBER', 2.0),
                 ('RPAREN', ')'),
                 ('MINUS', '-'),
                 ('NUMBER', 23.0),
                 ('ID', 'subscriptionAssetsMobile'),
                 ('ASSIGN', '='),
                 ('ID', 'core_base_library_getCustomProperty'),
                 ('LPAREN', '('),
                 ('STRING', 'varName'),
                 ('COLON', ':'),
                 ('STRING', 'subscription_assets_mobile'),
                 ('RPAREN', ')'),
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
                 ('FOR', 'for'),
                 ('NUMBER', 1.0),
                 ('OP', '..'),
                 ('NUMBER', 10.0),
                 ('SEMI', ';'),
                 ('ECHO', 'echo'),
                 ('STRING', 'fred'),
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

    def test_skip(self):
        '''Unit test for :py:meth:`utl_lex.Lexer.skip`.'''
        lexer = UTLLexer()
        lexer.input(self._MACRO_DEF)

        tok = lexer.token()
        self.assertEqual(repr(tok), "LexToken(DOCUMENT,'\\n    ',1,0)")
        tok = lexer.token()
        self.assertEqual(tok.type, 'START_UTL')
        tok = lexer.token()
        self.assertEqual(tok.type, 'CALL')
        lexer.skip(4)  # ' cms'
        tok = lexer.token()
        self.assertEqual(tok.type, 'OP')
        self.assertEqual(tok.value, '.')
        lexer.skip(10)  # 'component.'
        self.assertEqual(repr(lexer.token()), "LexToken(ID,'load',3,33)")

    def test_lineno(self):
        '''Unit test for :py:meth:`utl_lex.Lexer.lineno`.'''
        lexer = UTLLexer()
        lexer.input(self._MACRO_DEF)
        self.assertEqual(lexer.lineno(), 1)

        index = 0
        tok = lexer.token()
        while tok:
            self.assertEqual(lexer.lineno(), self._EXPECTED[index][2])
            tok = lexer.token()
            index += 1
        self.assertEqual(index, len(self._EXPECTED))  # make sure we didn't miss any

    def test_lexpos(self):
        """Unit tests for :py:meth:`utl_lex.lexer.lexpos`."""

        expected = [5, 8, 18, 22, 23, 32, 33, 37, 38, 59, 60, 61, 70, 74, 75, 84, 85, 89, 90, 106,
                    107, 108, 167, 208, 209, 210, 211, 290, 292, 294, 296, 298, 299, 326, 328, 364,
                    365, 374, 375, 396, 397, 442, 443, 465, 466, 467, 518, 520, 522, 523, 524, 528,
                    529, 537, 538, 544, 545, 555, 556, 561, 562, 569, 699, 701, 711, 714, 764, 765,
                    788, 790, 891, 895, 896, 902, 903, 909, 912, 916, 917, 924, 925, 930, 931, 937,
                    938, 941, 947, 948, 971, 974, 976, 978, 980, 981, 982, 983, 984, 985, 986, 987,
                    989, 1071, 1073, 1109, 1110, 1137, 1138, 1166, 1167, 1168, 1238, 1263, 1265,
                    1266, 1271, 1274, 1299, 1301, 1302, 1310, 1311, 1388, 1390, 1415, 1416, 1432,
                    1433, 1445, 1446, 1461, 1480, 1481, 1489, 1490, 1498, 1500, 1502, 1504, 1505,
                    1518, 1525, 1526, 1534, 1535, 1543]

        lexer = UTLLexer()
        lexer.input(self._MACRO_DEF)
        self.assertEqual(lexer.lexpos(), 0)
        index = 0
        tok = lexer.token()
        while tok:
            self.assertEqual(lexer.lexpos(), expected[index])
            tok = lexer.token()
            index += 1
        self.assertEqual(index, len(expected))  # make sure we checked all positions

    def test_end_utl_error(self):
        """Unit test for :py:meth:`utl_lex.lexer.token` when an extra END_UTL is encountered."""
        lexer = UTLLexer()
        lexer.input('%]')
        self.assertRaises(UTLLexerError, lexer.token)


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:

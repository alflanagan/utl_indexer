#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lex`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""

import os
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
         if !cms.system.mobile || cms.request.param('mode') == 'jqm';
             something += 5 * 7/(8+2)-23
            /* gather the list for mobile */
            subscriptionAssetsMobile = core_base_library_getCustomProperty(
                 'varName':'subscription_assets_mobile');

            /* if the list exists and is not defer */
            if subscriptionAssetsMobile != null && subscriptionAssetsMobile != 'defer';
                /* use the mobile list */
                subscriptionAssets = subscriptionAssetsMobile;
            else if a == b and c;
                do_something_else;
            end;
        end;
        return subscriptionAssets;
    end;
    for 1..10;
        echo 'fred';
    end;
    empty = "";
    %]'''

    #TODO: put rest of test data in external files, see test_operators()
    _EXPECTED = [('DOCUMENT', '\n    ', 2),  # token, text, line
                 ('START_UTL', '[%-', 2),
                 ('CALL', 'call', 4),
                 ('ID', 'cms', 4),
                 ('DOT', '.', 4),
                 ('ID', 'component', 4),
                 ('DOT', '.', 4),
                 ('ID', 'load', 4),
                 ('LPAREN', '(', 4),
                 ('STRING', 'core_base_editorial', 4),
                 ('RPAREN', ')', 4),  # 10
                 ('SEMI', ';', 4),
                 ('CALL', 'call', 5),
                 ('ID', 'cms', 5),
                 ('DOT', '.', 5),
                 ('ID', 'component', 5),
                 ('DOT', '.', 5),
                 ('ID', 'load', 5),
                 ('LPAREN', '(', 5),
                 ('STRING', 'core_base_user', 5),
                 ('RPAREN', ')', 5),  # 20
                 ('SEMI', ';', 5),
                 ('MACRO', 'macro', 10),
                 ('ID', 'core_base_library_subscriptionAssetsList', 10),
                 ('LPAREN', '(', 10),
                 ('RPAREN', ')', 10),
                 ('SEMI', ';', 10),
                 ('ID', 'something', 12),
                 ('ASSIGN', '=', 12),
                 ('NUMBER', 5.0, 12),
                 ('TIMES', '*', 12),  # 30
                 ('NUMBER', 3.0, 12),
                 ('SEMI', ';', 12),
                 ('ID', 'subscriptionAssets', 13),
                 ('ASSIGN', '=', 13),
                 ('ID', 'core_base_library_getCustomProperty', 13),
                 ('LPAREN', '(', 13),
                 ('STRING', 'varName', 13),
                 ('COLON', ':', 13),
                 ('STRING', 'subscription_assets', 13),
                 ('COMMA', ',', 13),
                 ('STRING', 'varDefault', 14),
                 ('COLON', ':', 14),
                 ('STRING', 'article,edition,page', 14),
                 ('RPAREN', ')', 14),
                 ('SEMI', ';', 14),
                 ('ID', 'fred', 17),
                 ('ASSIGN', '=', 17),
                 ('LBRACKET', '[', 17),
                 ('NUMBER', 1.0, 17),
                 ('COMMA', ',', 17),
                 ('NUMBER', 2.3, 17),
                 ('COMMA', ',', 17),
                 ('STRING', 'hello', 17),
                 ('COMMA', ',', 17),
                 ('FALSE', 'false', 17),
                 ('COMMA', ',', 17),
                 ('STRING', 'goodbye', 17),
                 ('COMMA', ',', 17),
                 ('NULL', 'null', 17),
                 ('RBRACKET', ']', 17),
                 ('END_UTL', '%]', 18),
                 ('DOCUMENT', ("\n    OK, it's weird to put text in the middle of a macro def\n"
                               "    but you COULD if you wanted to\n    and, of course, you"
                               " can embed "), 21),
                 ('START_UTL', '[%', 21),
                 ('ID', 'something', 21),
                 ('END_UTL', '%]', 21),
                 ('DOCUMENT', 'on one line\n    on the other hand, it could just ', 22),
                 ('DOCUMENT', '[', 22),
                 ('DOCUMENT', 'be a left bracket\n    ', 23),
                 ('START_UTL', '[%', 23),
                 ('IF', 'if', 25),
                 ('EXCLAMATION', '!', 25),
                 ('ID', 'cms', 25),
                 ('DOT', '.', 25),
                 ('ID', 'system', 25),
                 ('DOT', '.', 25),
                 ('ID', 'mobile', 25),
                 ('DOUBLEBAR', '||', 25),
                 ('ID', 'cms', 25),
                 ('DOT', '.', 25),
                 ('ID', 'request', 25),
                 ('DOT', '.', 25),
                 ('ID', 'param', 25),
                 ('LPAREN', '(', 25),
                 ('STRING', 'mode', 25),
                 ('RPAREN', ')', 25),
                 ('EQ', '==', 25),
                 ('STRING', 'jqm', 25),
                 ('SEMI', ';', 25),
                 ('ID', 'something', 26),
                 ('ASSIGNOP', '+=', 26),
                 ('NUMBER', 5.0, 26),
                 ('TIMES', '*', 26),
                 ('NUMBER', 7.0, 26),
                 ('DIV', '/', 26),
                 ('LPAREN', '(', 26),
                 ('NUMBER', 8.0, 26),
                 ('PLUS', '+', 26),
                 ('NUMBER', 2.0, 26),
                 ('RPAREN', ')', 26),
                 ('MINUS', '-', 26),
                 ('NUMBER', 23.0, 26),  # 100
                 ('ID', 'subscriptionAssetsMobile', 28),
                 ('ASSIGN', '=', 28),
                 ('ID', 'core_base_library_getCustomProperty', 28),
                 ('LPAREN', '(', 28),
                 ('STRING', 'varName', 29),
                 ('COLON', ':', 29),
                 ('STRING', 'subscription_assets_mobile', 29),
                 ('RPAREN', ')', 29),
                 ('SEMI', ';', 29),
                 ('IF', 'if', 32),  # 110
                 ('ID', 'subscriptionAssetsMobile', 32),
                 ('NEQ', '!=', 32),
                 ('NULL', 'null', 32),
                 ('DOUBLEAMP', '&&', 32),
                 ('ID', 'subscriptionAssetsMobile', 32),
                 ('NEQ', '!=', 32),
                 ('STRING', 'defer', 32),
                 ('SEMI', ';', 32),  # 120
                 ('ID', 'subscriptionAssets', 34),
                 ('ASSIGN', '=', 34),
                 ('ID', 'subscriptionAssetsMobile', 34),
                 ('SEMI', ';', 34),
                 ('ELSEIF', 'elseif', 35),
                 ('ID', 'a', 35),
                 ('EQ', '==', 35),
                 ('ID', 'b', 35),
                 ('AND', 'and', 35),
                 ('ID', 'c', 35),
                 ('SEMI', ';', 35),
                 ('ID', 'do_something_else', 36),  # 130
                 ('SEMI', ';', 36),
                 ('END', 'end', 37),
                 ('SEMI', ';', 37),
                 ('END', 'end', 38),
                 ('SEMI', ';', 38),
                 ('RETURN', 'return', 39),
                 ('ID', 'subscriptionAssets', 39),
                 ('SEMI', ';', 39),  # 140
                 ('END', 'end', 40),
                 ('SEMI', ';', 40),
                 ('FOR', 'for', 41),
                 ('NUMBER', 1.0, 41),
                 ('RANGE', '..', 41),
                 ('NUMBER', 10.0, 41),
                 ('SEMI', ';', 41),
                 ('ECHO', 'echo', 42),
                 ('STRING', 'fred', 42),
                 ('SEMI', ';', 42),  # 150
                 ('END', 'end', 43),
                 ('SEMI', ';', 43),
                 ('ID', 'empty', 44),
                 ('ASSIGN', '=', 44),
                 ('STRING', '', 44),
                 ('SEMI', ';', 44),
                 ('END_UTL', '%]', 45)]  # 153

    def test_create(self):
        """Unit test for :py:meth:`utl_lex.Lexer`."""
        lexer = UTLLexer()
        lexer.input(self._MACRO_DEF)
        self.assertEqual(lexer.lexdata, self._MACRO_DEF.replace('else if', 'elseif'))
        index = 0
        tok = lexer.token()
        while tok:
            try:
                self.assertEqual(tok.type, self._EXPECTED[index][0])
                self.assertEqual(tok.value, self._EXPECTED[index][1])
            except AssertionError as ase:
                ase.args = (ase.args[0] + "at token index " + str(index) + '\n', )
                raise
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
        self.assertEqual(tok.type, 'DOT')
        self.assertEqual(tok.value, '.')
        lexer.skip(10)  # 'component.'
        self.assertEqual(repr(lexer.token()), "LexToken(ID,'load',4,33)")

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

        expected = [5, 8, 18, 22, 23, 32, 33, 37, 38, 59, 60, 61, 70, 74, 75, 84, 85, 89, 90,
                    106, 107, 108, 167, 208, 209, 210, 211, 290, 292, 294, 296, 298, 299, 326, 328, 364,
                    365, 374, 375, 396, 397, 442, 443, 465, 466, 467, 518, 520, 522, 523, 524, 528, 529,
                    537, 538, 544, 545, 555, 556, 561, 562, 569, 699, 701, 711, 714, 764, 765, 788, 790,
                    891, 893, 896, 897, 903, 904, 910, 913, 917, 918, 925, 926, 931, 932, 938, 939, 942,
                    948, 949, 972, 975, 977, 979, 981, 982, 983, 984, 985, 986, 987, 988, 990, 1072, 1074,
                    1110, 1111, 1138, 1139, 1167, 1168, 1169, 1239, 1264, 1267, 1272, 1275, 1300, 1303,
                    1311, 1312, 1389, 1391, 1416, 1417, 1436, 1438, 1441, 1443, 1447, 1449, 1450,
                    1484, 1485, 1501, 1502, 1514, 1515, 1530, 1549, 1550, 1558, 1559, 1567, 1569,
                    1571, 1573, 1574, 1587, 1594, 1595, 1603, 1604, 1614, 1616, 1619, 1620, 1627]

        lexer = UTLLexer()
        lexer.input(self._MACRO_DEF)
        self.assertEqual(lexer.lexpos, 0)
        index = 0
        tok = lexer.token()
        while tok:
            self.assertEqual(lexer.lexpos, expected[index])
            tok = lexer.token()
            index += 1
        self.assertEqual(index, len(expected))  # make sure we checked all positions

    def test_end_utl_error(self):
        """Unit test for :py:meth:`utl_lex.lexer.token` when an extra END_UTL is encountered."""
        lexer = UTLLexer()
        lexer.input('%]')
        self.assertRaises(UTLLexerError, lexer.token)

    def test_keyword_in_id(self):
        """Unit tests to verify that IDs which start with a keyword are analysed as IDs."""
        problem1 = '[% sally.isfine = 3; %]'
        lexer = UTLLexer()
        lexer.input(problem1)
        expected1 = [('START_UTL', '[%'), ('ID', 'sally'), ('DOT', '.'), ('ID', 'isfine'),
                     ('ASSIGN', '='), ('NUMBER', 3), ('SEMI', ';'), ('END_UTL', '%]')]
        observed1 = []
        tok = lexer.token()
        while tok:
            observed1.append((tok.type, tok.value))
            tok = lexer.token()
        self.assertSequenceEqual(observed1, expected1)

    def test_operators(self):
        """Unit test of ability to lex operators."""
        lexer = UTLLexer()
        with open(os.path.join('test_data', 'operators.utl'), 'r') as operin:
            lexer.input(operin.read())
        toks = []
        tok = lexer.token()
        while tok:
            toks.append(tok)
            tok = lexer.token()
        index = 0
        with open(os.path.join('test_data', 'operators.lex'), 'r') as lexin:
            for line in lexin:
                parts = line[:-1].split(',')
                self.assertSequenceEqual(parts,
                                         [str(x) for x in [toks[index].type,
                                                           repr(toks[index].value),
                                                           toks[index].lineno,
                                                           toks[index].lexpos]])
                index += 1
        self.assertEqual(len(toks), index)


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:

#!/usr/bin/env python3

from utl_lex import lexer

# Test it out
# pylint: disable=E501
data = '''
[%-

call cms.component.load('core_base_editorial');
call cms.component.load("core_base_user");

/**
 * Subscription assets list
 */
macro core_base_library_subscriptionAssetsList();
    /* get asset types for subscription from standard */
    something = 5 * 3;
    subscriptionAssets = core_base_library_getCustomProperty('varName':'subscription_assets','varDefault':'article,edition,page');

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
-%]'''
#         /* gather the list for mobile */
#         subscriptionAssetsMobile = core_base_library_getCustomProperty('varName':'subscription_assets_mobile');

#         /* if the list exists and is not defer */
#         if subscriptionAssetsMobile != null && subscriptionAssetsMobile != 'defer';
#             /* use the mobile list */
#             subscriptionAssets = subscriptionAssetsMobile;
#         end;
#     end;
#     return subscriptionAssets;
# end;

# %]'''

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    print(tok)

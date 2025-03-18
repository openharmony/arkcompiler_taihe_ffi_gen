grammar Taihe;

/////////////
// Grammar //
/////////////

spec
    : (UseLst_uses += use)* (SpecFieldLst_fields += specField)*
      (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      EOF
    ;

use
    : KW_USE PkgName_pkg_name = pkgName (KW_AS tokenOpt_pkg_alias = ID)? SEMICOLON # usePackage
    | KW_FROM PkgName_pkg_name = pkgName KW_USE DeclAliasPairLst_decl_alias_pairs += declAliasPair (COMMA DeclAliasPairLst_decl_alias_pairs += declAliasPair)* SEMICOLON # useSymbol
    ;

pkgName
    : (tokenLst_parts += ID DOT)* tokenLst_parts += ID
    ;

declAliasPair
    : token_decl_name = ID (KW_AS tokenOpt_decl_alias = ID)?
    ;

specField
    : (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      KW_STRUCT token_name = ID
      LEFT_BRACE (StructFieldLst_fields += structField)* RIGHT_BRACE # struct
    | (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      KW_ENUM token_name = ID
      LEFT_BRACE (EnumFieldLst_fields += enumField)* RIGHT_BRACE # enum
    | (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      KW_INTERFACE token_name = ID
      (COLON InterfaceParentLst_extends += interfaceParent (COMMA InterfaceParentLst_extends += interfaceParent)*)?
      LEFT_BRACE (InterfaceFieldLst_fields += interfaceField)* RIGHT_BRACE # interface
    | (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      KW_FUNCTION token_name = ID
      LEFT_PARENTHESIS (ParameterLst_parameters += parameter (COMMA ParameterLst_parameters += parameter)*)? RIGHT_PARENTHESIS (COLON (TypeOpt_return_ty = type | KW_VOID))? SEMICOLON # globalFunction
    ;

structField
    : (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      token_name = ID
      COLON Type_ty = type SEMICOLON # structProperty
    ;

enumField
    : (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      token_name = ID
      (COLON TypeOpt_ty = type)? (ASSIGN_TO IntExprOpt_expr = intExpr)? SEMICOLON # enumProperty
    ;

interfaceField
    : (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      token_name = ID
      LEFT_PARENTHESIS (ParameterLst_parameters += parameter (COMMA ParameterLst_parameters += parameter)*)? RIGHT_PARENTHESIS (COLON (TypeOpt_return_ty = type | KW_VOID))? SEMICOLON # interfaceFunction
    ;

interfaceParent
    : (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      Type_ty = type
    ;

parameter
    : (DocstringItemLst_docstrings += docstringItem)* (LEFT_BRACKET (AttrItemLst_attrs += attrItem (COMMA AttrItemLst_attrs += attrItem)*)? RIGHT_BRACKET)?
      token_name = ID COLON Type_ty = type
    ;

///////////////
// Attribute //
///////////////

docstringItem
    : token_name = ID StringExpr_expr = stringExpr
    ;

attrItem
    : token_name = ID # emptyAttrItem
    | token_name = ID ASSIGN_TO AttrVal_val = attrVal # simpleAttrItem
    | token_name = ID LEFT_PARENTHESIS (AttrValLst_vals += attrVal (COMMA AttrValLst_vals += attrVal)*)? RIGHT_PARENTHESIS # tupleAttrItem
    ;

attrVal
    : StringExpr_expr = stringExpr # stringAttrVal
    | IntExpr_expr = intExpr # intAttrVal
    | BoolExpr_expr = boolExpr # boolAttrVal
    ;

//////////
// Type //
//////////

type
    : PkgName_pkg_name = pkgName DOT token_decl_name = ID # longType
    | token_decl_name = ID # shortType
    | token_decl_name = ID LESS_THAN (TypeLst_args += type (COMMA TypeLst_args += type)*)? GREATER_THAN # genericType
    | <assoc = right>
      LEFT_PARENTHESIS (ParameterLst_parameters += parameter (COMMA ParameterLst_parameters += parameter)*)? RIGHT_PARENTHESIS ARROW (TypeOpt_return_ty = type | KW_VOID) # callbackType
    ;

////////////////
// Expression //
////////////////

intExpr
    : token_val = (DEC_LITERAL | OCT_LITERAL | HEX_LITERAL | BIN_LITERAL) # literalIntExpr
    | LEFT_PARENTHESIS IntExpr_expr = intExpr RIGHT_PARENTHESIS # parenthesisIntExpr
    | token_op = (PLUS | MINUS | TILDE) IntExpr_expr = intExpr # unaryIntExpr
    | IntExpr_left = intExpr token_op = (STAR | SLASH | PERCENT) IntExpr_right = intExpr # binaryIntExpr
    | IntExpr_left = intExpr token_op = (PLUS | MINUS) IntExpr_right = intExpr # binaryIntExpr
    | IntExpr_left = intExpr (token_ch = LESS_THAN LESS_THAN | token_ch = GREATER_THAN GREATER_THAN) IntExpr_right = intExpr # binaryIntShiftExpr
    | IntExpr_left = intExpr token_op = AMPERSAND IntExpr_right = intExpr # binaryIntExpr
    | IntExpr_left = intExpr token_op = CARET IntExpr_right = intExpr # binaryIntExpr
    | IntExpr_left = intExpr token_op = PIPE IntExpr_right = intExpr # binaryIntExpr
    | KW_IF BoolExpr_cond = boolExpr KW_THEN IntExpr_then_expr = intExpr KW_ELSE IntExpr_else_expr = intExpr # conditionalIntExpr
    ;

boolExpr
    : token_val = (KW_TRUE | KW_FALSE) # literalBoolExpr
    | LEFT_PARENTHESIS BoolExpr_expr = boolExpr RIGHT_PARENTHESIS # parenthesisBoolExpr
    | token_op = EXCLAMATION BoolExpr_expr = boolExpr # unaryBoolExpr
    | IntExpr_left = intExpr token_op = (EQUAL_TO | NOT_EQUAL_TO | LESS_EQUAL_TO | GREATER_EQUAL_TO | LESS_THAN | GREATER_THAN) IntExpr_right = intExpr # comparisonBoolExpr
    | BoolExpr_left = boolExpr token_op = (AND | OR) BoolExpr_right = boolExpr # binaryBoolExpr
    | KW_IF BoolExpr_cond = boolExpr KW_THEN BoolExpr_then_expr = boolExpr KW_ELSE BoolExpr_else_expr = boolExpr # conditionalBoolExpr
    ;

stringExpr
    : tokenLst_vals += STRING_LITERAL+ # literalStringExpr
    ;

///////////
// Token //
///////////

SEMICOLON
    : ';'
    ;

COLON
    : ':'
    ;

DOT
    : '.'
    ;

ARROW
    : '=>'
    ;

COMMA
    : ','
    ;

LEFT_BRACE
    : '{'
    ;

RIGHT_BRACE
    : '}'
    ;

LEFT_PARENTHESIS
    : '('
    ;

RIGHT_PARENTHESIS
    : ')'
    ;

LEFT_BRACKET
    : '['
    ;

RIGHT_BRACKET
    : ']'
    ;

ASSIGN_TO
    : '='
    ;

PLUS
    : '+'
    ;

MINUS
    : '-'
    ;

STAR
    : '*'
    ;

SLASH
    : '/'
    ;

PERCENT
    : '%'
    ;

AT
    : '@'
    ;

DOLLAR
    : '$'
    ;

QUESTION_MARK
    : '?'
    ;

TILDE
    : '~'
    ;

AMPERSAND
    : '&'
    ;

PIPE
    : '|'
    ;

CARET
    : '^'
    ;

EXCLAMATION
    : '!'
    ;

AND
    : '&&'
    ;

OR
    : '||'
    ;

LESS_THAN
    : '<'
    ;

GREATER_THAN
    : '>'
    ;

LESS_EQUAL_TO
    : '<='
    ;

GREATER_EQUAL_TO
    : '>='
    ;

EQUAL_TO
    : '=='
    ;

NOT_EQUAL_TO
    : '!='
    ;

KW_IF
    : 'if'
    ;

KW_THEN
    : 'then'
    ;

KW_ELSE
    : 'else'
    ;

KW_USE
    : 'use'
    ;

KW_AS
    : 'as'
    ;

KW_FROM
    : 'from'
    ;

KW_STATIC
    : 'static'
    ;

KW_CONST
    : 'const'
    ;

KW_TYPE
    : 'type'
    ;

KW_ENUM
    : 'enum'
    ;

KW_STRUCT
    : 'struct'
    ;

KW_INTERFACE
    : 'interface'
    ;

KW_CONSTRUCTOR
    : 'constructor'
    ;

KW_FUNCTION
    : 'function'
    ;

KW_TRUE
    : 'TRUE'
    ;

KW_FALSE
    : 'FALSE'
    ;

KW_VOID
    : 'void'
    ;

STRING_LITERAL
    : '"' (ESCAPE_SEQUENCE | ~ ('\\' | '"'))* '"'
    | '"""' .*? '"""'
    ;

fragment ESCAPE_SEQUENCE
    : '\\' ('b' | 't' | 'n' | 'f' | 'r' | '"' | '\'' | '\\')
    | UNICODE_ESCAPE
    | OCTAL_ESCAPE
    ;

fragment OCTAL_ESCAPE
    : '\\' 'x' HEX_DIGIT HEX_DIGIT
    ;

fragment UNICODE_ESCAPE
    : '\\' 'u' HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT
    ;

fragment HEX_DIGIT
    : '0' .. '9'
    | 'a' .. 'f'
    | 'A' .. 'F'
    ;

fragment OCT_DIGIT
    : '0' .. '7'
    ;

fragment BIN_DIGIT
    : '0'
    | '1'
    ;

DEC_LITERAL
    : DIGIT+
    ;

HEX_LITERAL
    : '0x' HEX_DIGIT+
    ;

OCT_LITERAL
    : '0o' OCT_DIGIT+
    ;

BIN_LITERAL
    : '0b' HEX_DIGIT+
    ;

ID
    : (UNDERLINE | LETTER) (UNDERLINE | LETTER | DIGIT)*
    ;

fragment LETTER
    : 'A' .. 'Z'
    | 'a' .. 'z'
    ;

fragment UNDERLINE
    : '_'
    ;

fragment DIGIT
    : '0' .. '9'
    ;

WS
    : (' ' | '\r' | '\t' | '\u000C' | '\n') -> channel (HIDDEN)
    ;

MULTI_LINE_COMMENT
    : '/*' .*? '*/' -> channel (HIDDEN)
    ;

SINGLE_LINE_COMMENT
    : '//' ~ ('\n' | '\r')* '\r'? '\n' -> channel (HIDDEN)
    ;

ERROR_CHAR
    : .
    ;

grammar Taihe;

/////////////
// Grammar //
/////////////

spec
    : (UseLst_uses += use)* (SpecFieldLst_fields += specField)* EOF
    ;

use
    : KW_USE (tokenLst_pkg_name += ID DOT)* tokenLst_pkg_name += ID (KW_AS tokenOpt_pkg_alias = ID)? SEMICOLON # usePackage
    | KW_FROM (tokenLst_pkg_name += ID DOT)* tokenLst_pkg_name += ID* KW_USE (DeclAliasPairLst_decl_alias_pairs += declAliasPair COMMA)* DeclAliasPairLst_decl_alias_pairs += declAliasPair SEMICOLON # useSymbol
    ;

declAliasPair
    : token_decl_name = ID (KW_AS tokenOpt_decl_alias = ID)?
    ;

specField
    : KW_STRUCT token_name = ID LEFT_BRACE (StructFieldLst_fields += structField)* RIGHT_BRACE # struct
    | KW_ENUM token_name = ID LEFT_BRACE (EnumFieldLst_fields += enumField)+ RIGHT_BRACE # enum
    | KW_INTERFACE token_name = ID (COLON InterfaceParentLst_extends += interfaceParent (COMMA InterfaceParentLst_extends += interfaceParent)*)? LEFT_BRACE (InterfaceFieldLst_fields += interfaceField)* RIGHT_BRACE # interface
    | KW_FUNCTION token_name = ID LEFT_PARENTHESIS (ParameterLst_parameters += parameter (COMMA ParameterLst_parameters += parameter)*)? RIGHT_PARENTHESIS COLON
        (LEFT_PARENTHESIS (RetvalLst_retvals += retval (COMMA RetvalLst_retvals += retval)*)? RIGHT_PARENTHESIS | RetvalLst_retvals += retval) SEMICOLON # function
    | KW_TYPE token_name = ID ASSIGN_TO Type_ty = type SEMICOLON # typeAlias
    ;

structField
    : token_name = ID COLON Type_ty = type SEMICOLON # structProperty
    ;

enumField
    : token_name = ID (ASSIGN_TO IntExprOpt_expr = intExpr)? SEMICOLON # enumProperty
    ;

interfaceParent
    : Type_ty = type
    ;

interfaceField
    : KW_FUNCTION token_name = ID LEFT_PARENTHESIS (ParameterLst_parameters += parameter (COMMA ParameterLst_parameters += parameter)*)? RIGHT_PARENTHESIS COLON
        (LEFT_PARENTHESIS (RetvalLst_retvals += retval (COMMA RetvalLst_retvals += retval)*)? RIGHT_PARENTHESIS | RetvalLst_retvals += retval) SEMICOLON # interfaceFunction
    ;

parameter
    : token_name = ID COLON Type_ty = type
    ;

retval
    : Type_ty = type
    ;

//////////
// Type //
//////////

type
    : token_name = (KW_I8 | KW_I16 | KW_I32 | KW_I64 | KW_U8 | KW_U16 | KW_U32 | KW_U64 | KW_F32 | KW_F64 | KW_BOOL | KW_STRING) # primitiveType
    | (tokenLst_pkg_name += ID DOT)* token_decl_name = ID # userType
    | token_name = ID LEFT_PARENTHESIS (TypeLst_args += type (COMMA TypeLst_args += type)*)? RIGHT_PARENTHESIS # genericType
    | <assoc = right> LEFT_PARENTHESIS (ParameterLst_parameters += parameter (COMMA ParameterLst_parameters += parameter)*)? RIGHT_PARENTHESIS ARROW
        (LEFT_BRACKET (RetvalLst_retvals += retval (COMMA RetvalLst_retvals += retval)*)? RIGHT_BRACKET | RetvalLst_retvals += retval) # functionType
    ;

////////////////
// Expression //
////////////////

intExpr
    : token_val = (DEC_LITERAL | OCT_LITERAL | HEX_LITERAL | BIN_LITERAL) # intLiteralExpr
    | LEFT_PARENTHESIS IntExpr_expr = intExpr RIGHT_PARENTHESIS # intParenthesisExpr
    | token_op = (PLUS | MINUS | TILDE) IntExpr_expr = intExpr # intUnaryExpr
    | IntExpr_left = intExpr token_op = (STAR | SLASH | PERCENT) IntExpr_right = intExpr # intBinaryExpr
    | IntExpr_left = intExpr token_op = (PLUS | MINUS) IntExpr_right = intExpr # intBinaryExpr
    | IntExpr_left = intExpr token_op = (LEFT_SHIFT | RIGHT_SHIFT) IntExpr_right = intExpr # intBinaryExpr
    | IntExpr_left = intExpr token_op = AMPERSAND IntExpr_right = intExpr # intBinaryExpr
    | IntExpr_left = intExpr token_op = CARET IntExpr_right = intExpr # intBinaryExpr
    | IntExpr_left = intExpr token_op = PIPE IntExpr_right = intExpr # intBinaryExpr
    | KW_IF BoolExpr_cond = boolExpr KW_THEN IntExpr_then_expr = intExpr KW_ELSE IntExpr_else_expr = intExpr # intConditionalExpr
    ;

boolExpr
    : LEFT_PARENTHESIS BoolExpr_expr = boolExpr RIGHT_PARENTHESIS # boolParenthesisExpr
    | token_op = EXCLAMATION BoolExpr_expr = boolExpr # boolUnaryExpr
    | IntExpr_left = intExpr token_op = (EQUAL_TO | NOT_EQUAL_TO | LESS_EQUAL_TO | GREATER_EQUAL_TO | LESS_THAN | GREATER_THAN) IntExpr_right = intExpr # intComparisonExpr
    | BoolExpr_left = boolExpr token_op = (AND | OR) BoolExpr_right = boolExpr # boolBinaryExpr
    | KW_IF BoolExpr_cond = boolExpr KW_THEN BoolExpr_then_expr = boolExpr KW_ELSE BoolExpr_else_expr = boolExpr # boolConditionalExpr
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

LEFT_SHIFT
    : '<<'
    ;

RIGHT_SHIFT
    : '>>'
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

KW_I8
    : 'i8'
    ;

KW_I16
    : 'i16'
    ;

KW_I32
    : 'i32'
    ;

KW_I64
    : 'i64'
    ;

KW_U8
    : 'u8'
    ;

KW_U16
    : 'u16'
    ;

KW_U32
    : 'u32'
    ;

KW_U64
    : 'u64'
    ;

KW_F32
    : 'f32'
    ;

KW_F64
    : 'f64'
    ;

KW_BOOL
    : 'bool'
    ;

KW_STRING
    : 'String'
    ;

STRING_LITERAL
    : '"' (ESCAPE_SEQUENCE | ~ ('\\' | '"'))* '"'
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

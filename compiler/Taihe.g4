grammar Taihe;

specification
    : imports* field_attr = specificationField_opt* EOF
    ;

specificationField_opt
	: namespace
	;

imports
    : KW_IMPORT file_attr = STRING_LITERAL SEMICOLON
    ;

namespace
    : KW_NAMESPACE (name_attr += ID DOT)* name_attr += ID LEFT_BRACE field_attr = namespaceField_opt* RIGHT_BRACE
    ;

namespaceField_opt
	: namespace
    | struct
    | enumClass
    | interface
    | class
    | constant
    | function
    ;

struct
    : KW_STRUCT name_attr = ID LEFT_BRACE structField_opt* RIGHT_BRACE
    ;

structField_opt
	: structProperty
	;

structProperty
    : name_attr = ID COLON type_opt SEMICOLON
    ;

enumClass
    : KW_ENUM name_attr = ID LEFT_BRACE field_attr = enumField_opt RIGHT_BRACE
    ;

enumField_opt
	: enumValue
    | enumProperty
    | enumStruct
    ;

enumValue
    : name_attr = ID SEMICOLON
    ;

enumProperty
    : name_attr = ID COLON type_attr = type_opt SEMICOLON
    ;

enumStruct
    : name_attr = ID LEFT_BRACE field_attr = structField_opt* RIGHT_BRACE
    ;

interface
    : KW_INTERFACE name_attr = ID (KW_EXTENDS extends_attr += ID (COMMA extends_attr += ID)*)? LEFT_BRACE field_attr = interfaceField_opt* RIGHT_BRACE
    ;

interfaceField_opt
	: memberFunction
	| memberConst
	;

class
    : KW_CLASS name_attr = ID (KW_INHERITS inherits_attr += ID)? (KW_IMPLEMENTS implements_attr += ID (COMMA implements_attr += ID)*)? LEFT_BRACE field_attr = classField_opt* RIGHT_BRACE
    ;

classField_opt
	: constructor
	| memberFunction
	| memberConst
	;

constructor
    : KW_CONSTRUCTOR LEFT_BRACKET (parameters_attr += parameter (COMMA parameters_attr += parameter)*)? RIGHT_BRACKET SEMICOLON
    ;

memberFunction
    : (static_attr = KW_STATIC)? KW_FUNCTION name_attr = ID LEFT_BRACKET (parameters_attr += parameter (COMMA parameters_attr += parameter)*)? RIGHT_BRACKET COLON
        (LEFT_BRACKET (returnValueTypes_attr += type_opt (COMMA returnValueTypes_attr += type_opt)*)? RIGHT_BRACKET | returnValueTypes_attr += type_opt) SEMICOLON
    ;

memberConst
    : (static_attr = KW_STATIC)? KW_CONST name_attr = ID COLON type_attr = type_opt SEMICOLON
    ;

function
    : KW_FUNCTION name_attr = ID LEFT_BRACKET (parameters_attr += parameter (COMMA parameters_attr += parameter)*)? RIGHT_BRACKET COLON
        (LEFT_BRACKET (returnValueTypes_attr += type_opt (COMMA returnValueTypes_attr += type_opt)*)? RIGHT_BRACKET | returnValueTypes_attr += type_opt) SEMICOLON
    ;

constant
    : KW_CONST name_attr = ID COLON type_attr = type_opt SEMICOLON
    ;

parameter
    : name_attr = ID COLON type_attr = typeWithSpecifier
    ;

type_opt
	: basicType
	| userType
	| parameterizedType
	| functionType
	;

typeWithSpecifier
	: ((const_attr = KW_CONST)? ref_attr = KW_REF)? type_attr = type_opt
	;

basicType
    : name_attr = (KW_I8 | KW_I16 | KW_I32 | KW_I64 | KW_U8 | KW_U16 | KW_U32 | KW_U64 | KW_F32 | KW_F64 | KW_BOOL)
    ;

userType
    : (global = KW_GLOBAL)? (name_attr += ID DOT)* name_attr += ID
    ;

functionType
    : <assoc_attr = right> LEFT_BRACKET ((parameterTypes_attr += typeWithSpecifier) (COMMA parameterTypes_attr += typeWithSpecifier)*)? RIGHT_BRACKET ARROW
        (LEFT_BRACKET (returnValueTypes_attr += type_opt (COMMA returnValueTypes_attr += type_opt)*)? RIGHT_BRACKET | returnValueTypes_attr += type_opt) SEMICOLON
    ;

parameterizedType
    : name_attr = ID LEFT_ANG_BRACKET (parameters_attr += type_opt (COMMA parameters_attr += type_opt)*)? RIGHT_ANG_BRACKET
    ;

SEMICOLON
    : ';'
    ;

COLON
    : ':'
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

LEFT_BRACKET
    : '('
    ;

RIGHT_BRACKET
    : ')'
    ;

LEFT_SQUARE_BRACKET
    : '['
    ;

RIGHT_SQUARE_BRACKET
    : ']'
    ;

TILDE
    : '~'
    ;

SLASH
    : '/'
    ;

LEFT_ANG_BRACKET
    : '<'
    ;

RIGHT_ANG_BRACKET
    : '>'
    ;

STAR
    : '*'
    ;

PLUS
    : '+'
    ;

MINUS
    : '-'
    ;

CARET
    : '^'
    ;

AMPERSAND
    : '&'
    ;

PIPE
    : '|'
    ;

EQUAL
    : '='
    ;

PERCENT
    : '%'
    ;

DOT
    : '.'
    ;

KW_IMPORT
    : 'import'
    ;

KW_IMPLEMENTS
    : 'implements'
    ;

KW_EXTENDS
    : 'extends'
    ;

KW_INHERITS
    : 'inherits'
    ;

KW_STATIC
    : 'static'
    ;

KW_CONST
    : 'const'
    ;

KW_REF
    : 'ref'
    ;

KW_ENUM
    : 'enum'
    ;

KW_STRUCT
    : 'struct'
    ;

KW_NAMESPACE
    : 'namespace'
    ;

KW_CLASS
    : 'class'
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

KW_GLOBAL
    : 'global'
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

ID
    : LETTER (LETTER | DIGIT)*
    ;

fragment LETTER
    : '_'
    | 'A' .. 'Z'
    | 'a' .. 'z'
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

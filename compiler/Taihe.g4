grammar Taihe;

specification
    : (Use_uses += use)* (SpecificationFieldOpt_fields += specificationFieldOpt)* EOF
    ;

use
    : KW_USE (Bool_glob = AT)? (Str_ns += ID DOT)* (LEFT_BRACE (Str_names += ID (COMMA Str_names += ID)*)? RIGHT_BRACE | Str_names += ID | Bool_all = STAR) SEMICOLON
    ;

specificationFieldOpt
	: Struct = struct
    | EnumClass = enumClass
    | Interface = interface
    | Class = class
    | Const = const
    | Function = function
    ;

struct
    : KW_STRUCT Str_name = ID LEFT_BRACE (StructFieldOpt_fields += structFieldOpt)* RIGHT_BRACE
    ;

structFieldOpt
	: StructProperty = structProperty
	;

structProperty
    : Str_name = ID COLON typeOpt SEMICOLON
    ;

enumClass
    : KW_ENUM Str_name = ID LEFT_BRACE (EnumFieldOpt_fields += enumFieldOpt)+ RIGHT_BRACE
    ;

enumFieldOpt
	: EnumProperty = enumProperty
    ;

enumProperty
    : Str_name = ID (COLON TypeOpt_type = typeOpt)? SEMICOLON
    ;

interface
    : KW_INTERFACE Str_name = ID (KW_EXTENDS Str_extends += ID (COMMA Str_extends += ID)*)? LEFT_BRACE (InterfaceFieldOpt_fields += interfaceFieldOpt)* RIGHT_BRACE
    ;

interfaceFieldOpt
	: MemberFunction = memberFunction
	| MemberConst = memberConst
	;

class
    : KW_CLASS Str_name = ID (KW_INHERITS Str_inherits += ID)? (KW_IMPLEMENTS Str_implements += ID (COMMA Str_implements += ID)*)? LEFT_BRACE (ClassFieldOpt_fields += classFieldOpt)* RIGHT_BRACE
    ;

classFieldOpt
	: Constructor = constructor
	| MemberFunction = memberFunction
	| MemberConst = memberConst
	;

constructor
    : KW_CONSTRUCTOR LEFT_BRACKET (Parameter_parameters += parameter (COMMA Parameter_parameters += parameter)*)? RIGHT_BRACKET SEMICOLON
    ;

memberFunction
    : (Bool_static = KW_STATIC)? KW_FUNCTION Str_name = ID LEFT_BRACKET (Parameter_parameters += parameter (COMMA Parameter_parameters += parameter)*)? RIGHT_BRACKET COLON
        (LEFT_BRACKET (TypeOpt_returnValueTypes += typeOpt (COMMA TypeOpt_returnValueTypes += typeOpt)*)? RIGHT_BRACKET | TypeOpt_returnValueTypes += typeOpt) SEMICOLON
    ;

memberConst
    : (Bool_static = KW_STATIC)? KW_CONST Str_name = ID COLON TypeOpt_type = typeOpt SEMICOLON
    ;

function
    : KW_FUNCTION Str_name = ID LEFT_BRACKET (Parameter_parameters += parameter (COMMA Parameter_parameters += parameter)*)? RIGHT_BRACKET COLON
        (LEFT_BRACKET (TypeOpt_returnValueTypes += typeOpt (COMMA TypeOpt_returnValueTypes += typeOpt)*)? RIGHT_BRACKET | TypeOpt_returnValueTypes += typeOpt) SEMICOLON
    ;

const
    : KW_CONST Str_name = ID COLON TypeOpt_type = typeOpt SEMICOLON
    ;

parameter
    : Str_name = ID COLON ParameterType_parameterType = parameterType
    ;

typeOpt
	: BasicType = basicType
	| UserType = userType
	| ParameterizedType = parameterizedType
	| FunctionType = functionType
	;

parameterType
	: ((Bool_const = KW_CONST)? Bool_ref = KW_REF)? TypeOpt_type = typeOpt
	;

basicType
    : Str_name = (KW_I8 | KW_I16 | KW_I32 | KW_I64 | KW_U8 | KW_U16 | KW_U32 | KW_U64 | KW_F32 | KW_F64 | KW_BOOL)
    ;

userType
    : (Bool_glob = AT)? (Str_ns += ID DOT)* Str_name += ID
    ;

functionType
    : <assoc = right> LEFT_BRACKET ((ParameterType_parameterTypes += parameterType) (COMMA ParameterType_parameterTypes += parameterType)*)? RIGHT_BRACKET ARROW
        (LEFT_BRACKET (TypeOpt_returnValueTypes += typeOpt (COMMA TypeOpt_returnValueTypes += typeOpt)*)? RIGHT_BRACKET | TypeOpt_returnValueTypes += typeOpt) SEMICOLON
    ;

parameterizedType
    : Str_name = ID LEFT_ANG_BRACKET (TypeOpt_parameters += typeOpt (COMMA TypeOpt_parameters += typeOpt)*)? RIGHT_ANG_BRACKET
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

AT
    : '@'
    ;

KW_USE
    : 'use'
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

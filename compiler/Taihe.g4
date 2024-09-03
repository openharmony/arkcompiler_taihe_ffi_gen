grammar Taihe;

specification
    : imports* specificationField* EOF
    ;

imports
    : KW_IMPORT moduleName SEMICOLON
    ;

moduleName
    : ID (DOT ID)*
    ;

specificationField
    : namespace
    ;

namespace
    : KW_NAMESPACE namespaceName LEFT_BRACE namespaceField* RIGHT_BRACE
    ;

namespaceName
    : ID (DOUBLE_COLON ID)*
    ;

namespaceField
    : namespace
    | struct
    | enumClass
    | interface
    | class
    | const
    | function
    ;

struct
    : KW_STRUCT structName LEFT_BRACE structField* RIGHT_BRACE
    ;

structName
    : ID
    ;

structField
    : structFieldName COLON type SEMICOLON
    ;

structFieldName
    : ID
    ;

enumClass
    : KW_ENUM enumClassName LEFT_BRACE enumField+ RIGHT_BRACE
    ;

enumClassName
    : ID
    ;

enumField
    : enumFieldName SEMICOLON
    | enumFieldName COLON type SEMICOLON
    | structName LEFT_BRACE structField* RIGHT_BRACE
    ;

enumFieldName
    : ID
    ;

interface
    : KW_INTERFACE interfaceName (KW_IMPLEMENTS interfaceName (COMMA interfaceName)*)? LEFT_BRACE interfaceField* RIGHT_BRACE
    ;

interfaceName
    : ID
    ;

interfaceField
    : static
    | nonstatic
    ;

class
    : KW_CLASS className (KW_INHERITS className)? (KW_IMPLEMENTS interfaceName (COMMA interfaceName)*)? LEFT_BRACE classField* RIGHT_BRACE
    ;

className
    : ID
    ;

classField
    : static
    | nonstatic
    | constructor
    ;

static
    : KW_STATIC function
    | KW_STATIC const
    ;

nonstatic
    : function
    ;

constructor
    : KW_CONSTRUCTOR LEFT_BRACKET (functionParameterPair (COMMA functionParameterPair)*)? RIGHT_BRACKET SEMICOLON
    ;

function
    : KW_FUNCTION functionName LEFT_BRACKET (functionParameterPair (COMMA functionParameterPair)*)? RIGHT_BRACKET COLON
          (LEFT_BRACKET (type (COMMA type)*)? RIGHT_BRACKET | type) SEMICOLON
    ;

functionName
    : ID
    ;

functionParameterPair
    : functionParameterName COLON functionParameterType
    ;

functionParameterName
    : ID
    ;

functionParameterType
    : ((KW_CONST)? KW_REF)? valType
    | refType
    ;

const
    : KW_CONST constName COLON type SEMICOLON
    ;

constName
    : ID
    ;

type
    : valType
    | refType
    ;

refType
    : className
    | interfaceName
    | functionType
    | parameterizedType
    ;

functionType
    : <assoc = right> LEFT_BRACKET (functionParameterType (COMMA functionParameterType)*)? RIGHT_BRACKET ARROW
          (LEFT_BRACKET (type (COMMA type)*)? RIGHT_BRACKET | type) SEMICOLON
    ;

parameterizedType
    : templateName LEFT_ANG_BRACKET (type (COMMA type)*)? RIGHT_ANG_BRACKET
    ;

valType
    : basicType
    | structName
    | enumClassName
    ;

basicType
    : KW_I8
    | KW_I16
    | KW_I32
    | KW_I64
    | KW_U8
    | KW_U16
    | KW_U32
    | KW_U64
    | KW_F32
    | KW_F64
    | KW_BOOL
    ;

templateName
    : ID
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

DOUBLE_COLON
    : '::'
    ;

fragment LETTER
    : '_'
    | 'A' .. 'Z'
    | 'a' .. 'z'
    ;

fragment DIGIT
    : '0' .. '9'
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

ID
    : LETTER (LETTER | DIGIT)*
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

grammar Taihe;

specification
    : (UseUniLst_uses += useUni)* (SpecificationFieldUniLst_fields += specificationFieldUni)* EOF
    ;

useUni
    : UsePackage_ = usePackage
    | UseSymbol_ = useSymbol
    ;

usePackage
    : KW_USE PackageName_old_pkname = packageName (KW_AS PackageAliasOpt_new_pkname = packageAlias)? SEMICOLON
    ;

useSymbol
    : KW_FROM PackageName_pkname = packageName KW_USE (AliasPairLst_alias_pairs += aliasPair COMMA)* AliasPairLst_alias_pairs += aliasPair SEMICOLON
    ;

packageNameUni
    : PackageName_ = packageName
    | PackageAlias_ = packageAlias
    ;

packageName
    : tokenLst_parts += ID (DOT tokenLst_parts += ID)*
    ;

packageAlias
    : tokenLst_parts += ID
    ;

aliasPair
    : token_old_name = ID (KW_AS tokenOpt_new_name = ID)?
    ;

specificationFieldUni
    : Struct_ = struct
    | Enum_ = enum
    | Variant_ = variant
    | Interface_ = interface
    | Runtimeclass_ = runtimeclass
    | Const_ = const
    | Function_ = function
    ;

struct
    : KW_STRUCT token_name = ID LEFT_BRACE (StructFieldUniLst_fields += structFieldUni)* RIGHT_BRACE
    ;

structFieldUni
    : StructProperty_ = structProperty
    ;

structProperty
    : token_name = ID COLON TypeUni_type = typeUni SEMICOLON
    ;

enum
    : KW_ENUM token_name = ID LEFT_BRACE (EnumFieldUniLst_fields += enumFieldUni)+ RIGHT_BRACE
    ;

enumFieldUni
    : EnumProperty_ = enumProperty
    ;

enumProperty
    : token_name = ID (EQUAL ExprUni_expr = exprUni)? SEMICOLON
    ;

exprUni
    : Integer_ = integer
    ;

integer
    : DEC_LITERAL
    | OCT_LITERAL
    | HEX_LITERAL
    | BIN_LITERAL
    ;

variant
    : KW_ENUM token_name = ID LEFT_BRACE (VariantFieldUniLst_fields += variantFieldUni)+ RIGHT_BRACE
    ;

variantFieldUni
    : VariantProperty_ = variantProperty
    ;

variantProperty
    : token_name = ID (COLON TypeUniOpt_type = typeUni)? SEMICOLON
    ;

interface
    : KW_INTERFACE token_name = ID (KW_EXTENDS tokenLst_extends += ID (COMMA tokenLst_extends += ID)*)? LEFT_BRACE (InterfaceFieldUniLst_fields += interfaceFieldUni)* RIGHT_BRACE
    ;

interfaceFieldUni
    : MemberFunction_ = memberFunction
    | MemberConst_ = memberConst
    ;

runtimeclass
    : KW_RUNTIMECLASS token_name = ID (KW_INHERITS tokenLst_inherits += ID)? (KW_IMPLEMENTS tokenLst_implements += ID (COMMA tokenLst_implements += ID)*)? LEFT_BRACE (RuntimeclassFieldUniLst_fields += runtimeclassFieldUni)* RIGHT_BRACE
    ;

runtimeclassFieldUni
    : Constructor_ = constructor
    | MemberFunction_ = memberFunction
    | MemberConst_ = memberConst
    ;

constructor
    : KW_CONSTRUCTOR LEFT_BRACKET (ParameterLst_parameters += parameter (COMMA ParameterLst_parameters += parameter)*)? RIGHT_BRACKET SEMICOLON
    ;

memberFunction
    : (tokenOpt_static = KW_STATIC)? KW_FUNCTION token_name = ID LEFT_BRACKET (ParameterLst_parameters += parameter (COMMA ParameterLst_parameters += parameter)*)? RIGHT_BRACKET COLON
        (LEFT_BRACKET (TypeWithSpecifierLst_return_types += typeWithSpecifier (COMMA TypeWithSpecifierLst_return_types += typeWithSpecifier)*)? RIGHT_BRACKET | TypeWithSpecifierLst_return_types += typeWithSpecifier) SEMICOLON
    ;

memberConst
    : (tokenOpt_static = KW_STATIC)? KW_CONST token_name = ID COLON TypeUni_type = typeUni SEMICOLON
    ;

function
    : KW_FUNCTION token_name = ID LEFT_BRACKET (ParameterLst_parameters += parameter (COMMA ParameterLst_parameters += parameter)*)? RIGHT_BRACKET COLON
        (LEFT_BRACKET (TypeWithSpecifierLst_return_types += typeWithSpecifier (COMMA TypeWithSpecifierLst_return_types += typeWithSpecifier)*)? RIGHT_BRACKET | TypeWithSpecifierLst_return_types += typeWithSpecifier) SEMICOLON
    ;

const
    : KW_CONST token_name = ID COLON TypeUni_type = typeUni SEMICOLON
    ;

parameter
    : token_name = ID COLON TypeWithSpecifier_type_with_specifier = typeWithSpecifier
    ;

typeUni
    : BasicType_ = basicType
    | UserType_ = userType
    | ParameterizedType_ = parameterizedType
    | FunctionType_ = functionType
    ;

typeWithSpecifier
    : ((tokenOpt_const = KW_CONST)? tokenOpt_ref = KW_REF)? TypeUni_type = typeUni
    ;

basicType
    : token_name = (KW_I8 | KW_I16 | KW_I32 | KW_I64 | KW_U8 | KW_U16 | KW_U32 | KW_U64 | KW_F32 | KW_F64 | KW_BOOL | KW_STRING)
    ;

userType
    : (PackageNameUniOpt_pkname = packageNameUni DOT)? token_name = ID
    ;

functionType
    : <assoc = right> LEFT_BRACKET ((TypeWithSpecifierLst_parameter_types += typeWithSpecifier) (COMMA TypeWithSpecifierLst_parameter_types += typeWithSpecifier)*)? RIGHT_BRACKET ARROW
        (LEFT_BRACKET (TypeWithSpecifierLst_return_types += typeWithSpecifier (COMMA TypeWithSpecifierLst_return_types += typeWithSpecifier)*)? RIGHT_BRACKET | TypeWithSpecifierLst_return_types += typeWithSpecifier) SEMICOLON
    ;

parameterizedType
    : token_name = ID LEFT_ANG_BRACKET (TypeUniLst_parameters += typeUni (COMMA TypeUniLst_parameters += typeUni)*)? RIGHT_ANG_BRACKET
    ;

SEMICOLON
    : ';'
    ;

COLON
    : ':'
    ;

DOT
    : '.'
    ;

AT
    : '@'
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

LEFT_ANG_BRACKET
    : '<'
    ;

RIGHT_ANG_BRACKET
    : '>'
    ;

EQUAL
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

CARET
    : '^'
    ;

AMPERSAND
    : '&'
    ;

PIPE
    : '|'
    ;

TILDE
    : '~'
    ;

AND
    : '&&'
    ;

OR
    : '||'
    ;

EXCLAMATION
    : '!'
    ;

LEFT_SHIFT
    : '<<'
    ;

RIGHT_SHIFT
    : '>>'
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

KW_UNION
    : 'union'
    ;

KW_STRUCT
    : 'struct'
    ;

KW_RUNTIMECLASS
    : 'runtimeclass'
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

KW_Array
    : 'Array'
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
    : LETTER (LETTER | DIGIT)* (UNDERLINE (LETTER | DIGIT)+)*
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

# Name: Nafisah Nubah

# Token types
class TokenType:
    LPAREN = 'LPAREN'           # '{'
    RPAREN = 'RPAREN'           # '}'
    LBRACKET = 'LBRACKET'       # '['
    RBRACKET = 'RBRACKET'       # ']'
    COLON = 'COLON'             # ':'
    COMMA = 'COMMA'             # ','
    STRING = 'STRING'           # strings
    NUMBER = 'NUMBER'           # numbers
    TRUE = 'TRUE'               # true
    FALSE = 'FALSE'             # false
    NULL = 'NULL'               # null
    EOF = 'EOF'                 # end of input


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"<{self.type}, {self.value}>"


# Lexer error
class LexerError(Exception):
    def __init__(self, position, character, message=None):
        self.position = position
        self.character = character
        super().__init__(message or f"Invalid character '{character}' at position {position}")


class Lexer:
    def __init__(self, input_text):
        # Input string
        self.input_text = input_text
        # Current position
        self.position = 0
        self.current_char = self.input_text[self.position] if self.input_text else None

    # Input Buffering
    def advance(self):
        self.position += 1
        if self.position >= len(self.input_text):
            # End of input
            self.current_char = None
        else:
            self.current_char = self.input_text[self.position]

    # Skip whitespace
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Recognize string
    def recognize_string(self):
        result = ''
        while self.current_char is not None and self.current_char not in ['”', '"']:
            result += self.current_char
            self.advance()
        self.advance()
        return Token(TokenType.STRING, result)

    # Recognize numbers
    def recognize_number(self):
        start = self.position
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char in ['.', 'e', 'E', '-', '+']):
            result += self.current_char
            self.advance()
        try:
            return Token(TokenType.NUMBER, float(result))
        except ValueError:
            raise LexerError(start, result, f"Invalid number '{result}' at position {start}") from None

    # Recognize true, false and null
    def recognize_keyword(self):
        for word, token_type in (('true', TokenType.TRUE), ('false', TokenType.FALSE), ('null', TokenType.NULL)):
            if self.input_text.startswith(word, self.position):
                self.position += len(word)
                self.current_char = self.input_text[self.position] if self.position < len(self.input_text) else None
                return Token(token_type)
        return None

    # Get next token from input
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # All other tokens
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LPAREN)
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RPAREN)
            if self.current_char == '[':
                self.advance()
                return Token(TokenType.LBRACKET)
            if self.current_char == ']':
                self.advance()
                return Token(TokenType.RBRACKET)
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA)
            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON)
            keyword_token = self.recognize_keyword()
            if keyword_token:
                return keyword_token

            # Strings
            if self.current_char in ['"', '“']:
                self.advance()
                return self.recognize_string()

            # Numbers
            if self.current_char.isdigit() or self.current_char in ['-', '+']:
                return self.recognize_number()

            # Unrecognized characters
            raise LexerError(self.position, self.current_char)

        # Eof
        return Token(TokenType.EOF)

    # Tokenize the input
    def tokenize(self):
        tokens = []
        while True:
            try:
                token = self.get_next_token()
            except LexerError as e:
                print(f"Lexical Error: {e}")
                break
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens

# Obtaining token streams from the Lexer with input JSON strings
if __name__ == "__main__":
    input_string = input('Please enter a valid JSON string: ')
    lexer = Lexer(input_string)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)

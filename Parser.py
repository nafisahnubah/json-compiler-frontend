# Name: Nafisah Nubah
# ID: B00961732

from Scanner import TokenType, Token


# Nodes
class Node:
    def __init__(self, label=None, value=None, is_leaf=False):
        self.label = label
        self.value = value
        self.children = []
        self.is_leaf = is_leaf

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self, depth=0, file_name=None):
        """Writes output abstract syntax tree in a specified .txt file"""
        indent = "  " * depth
        if self.is_leaf:
            if self.label == "String":
                output = f"{indent}'{self.value}'\n"
                file_name.write(output)
            else:
                output = f"{indent}{self.value}\n"
                file_name.write(output)
        else:
            if self.label == "Object":
                file_name.write(f"{indent}Object:\n")

                for child in self.children:
                    child.print_tree(depth + 1, file_name)

            elif self.label == "Array":
                file_name.write(f"{indent}Array:\n")
                for child in self.children:
                    child.print_tree(depth + 1, file_name)
            elif self.label == "Pair":
                value_node = self.children[1]
                file_name.write(f"{indent}{self.children[0].value}: ")
                if value_node.is_leaf:
                    if value_node.label == "String":
                        file_name.write(f"'{value_node.value}'\n")
                    else:
                        file_name.write(f"{value_node.value}\n")
                else:
                    file_name.write("\n")
                    value_node.print_tree(depth + 1, file_name)


class Parser:
    def __init__(self, token_stream):
        self.tokens = token_stream
        self.current_index = 0
        self.current_token = None
        self.semantically_correct = True

    def get_next_token(self):
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
            self.current_index += 1
        else:
            self.current_token = TokenType.EOF

    def eat(self, token_type):
        """Consume a token if it matches the expected type, raise an Error otherwise"""
        if self.current_token.type == token_type:
            self.get_next_token()
        else:
            raise Exception(f"Expected token {token_type}, got {self.current_token.type}")

    def parse(self, output_file):
        """Starts the parsing process by fetching the first token and calling the first grammar rule,
        logs potential semantic errors in output file"""
        try:
            self.get_next_token()
            return self.value()
        except Exception as error:
            with open(output_file, 'w') as output_file:
                output_file.write(str(error))
            self.semantically_correct = False
        return

    def value(self):
        """Parse JSON values"""
        token_type = self.current_token.type
        if token_type == TokenType.STRING:
            return self.string()
        elif token_type == TokenType.NUMBER:
            return self.number()
        elif token_type == TokenType.TRUE:
            return self.true()
        elif token_type == TokenType.FALSE:
            return self.false()
        elif token_type == TokenType.NULL:
            return self.null()
        elif token_type == TokenType.LPAREN:
            return self.dict()
        elif token_type == TokenType.LBRACKET:
            return self.list()
        else:
            raise Exception(f"Unexpected token {token_type} in Value")

    def string(self):
        value = self.current_token.value
        self.eat(TokenType.STRING)
        return Node(label="String", value=value, is_leaf=True)

    def number(self):
        value = self.current_token.value
        if (value.startswith("0") and len(value) > 1 and value[1] != ".") or value.startswith("+"):
            raise Exception(f"Error type 3 at {value}: Invalid Numbers.")
        if value.startswith(".") or value.endswith("."):
            raise Exception(f"Error type 1 at {value}: Invalid Decimal Numbers.")
        self.eat(TokenType.NUMBER)
        return Node(label="Number", value=value, is_leaf=True)

    def true(self):
        self.eat(TokenType.TRUE)
        return Node(label="Boolean", value="True", is_leaf=True)

    def false(self):
        self.eat(TokenType.FALSE)
        return Node(label="Boolean", value="False", is_leaf=True)

    def null(self):
        self.eat(TokenType.NULL)
        return Node(label="Null", is_leaf=True)

    def dict(self):
        """Parses the dict rule: '{' pair (',' pair)∗ '}' """
        self.eat(TokenType.LPAREN)
        dict_node = Node(label="Object")
        keys = set()
        if self.current_token.type != TokenType.RPAREN:
            curr_pair = self.pair()
            self.duplicate_key(curr_pair, keys)
            dict_node.children.append(curr_pair)
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                curr_pair = self.pair()
                self.duplicate_key(curr_pair, keys)
                dict_node.children.append(curr_pair)
        self.eat(TokenType.RPAREN)
        return dict_node

    def duplicate_key(self, curr_pair, keys):
        """Checks whether duplicate keys are present in a dict"""
        key = curr_pair.children[0].value
        if key in keys:
            raise Exception(f"Error type 5 at {key}: No Duplicate Keys in Dictionary.")
        keys.add(key)

    def pair(self):
        """Parses the pair rule: STRING ' : ' value """
        key = self.current_token.value
        if key.strip() == "":
            raise Exception(f"Error type 2 at {key}: Empty Key.")
        elif key in ["true", "false"]:
            raise Exception(f"Error type 4 at {key}: Reserved Words as Dictionary Key.")
        self.eat(TokenType.STRING)
        self.eat(TokenType.COLON)
        value_node = self.value()
        pair_node = Node(label="Pair")
        pair_node.add_child(Node(label="Key", value=key, is_leaf=True))
        pair_node.add_child(value_node)
        return pair_node

    def list(self):
        """Parses the list rule: '[' value (',' value)∗ ']' """
        self.eat(TokenType.LBRACKET)
        list_node = Node(label="Array")
        data_types = set()
        if self.current_token.type != TokenType.RBRACKET:
            curr_node = self.value()
            data_types.add(curr_node.label)
            list_node.children.append(curr_node)
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                curr_node = self.value()
                data_types.add(curr_node.label)
                list_node.children.append(curr_node)
        if len(data_types) != 1:
            raise Exception("Error type 6: Consistent Types for List Elements.")
        self.eat(TokenType.RBRACKET)
        return list_node


def read_tokens(file_name):
    """Reads in token stream from a .txt file, returns a list of Token objects"""
    tokens = []
    with open(file_name, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            line = line.strip()
            if line:
                token = make_token(line)
                tokens.append(token)
    return tokens


def make_token(token_string):
    """Convert string representation of each token into a Token object"""
    if token_string.startswith('<') and token_string.endswith('>'):
        contents = token_string[1:-1].split(', ')
        return Token(contents[0], contents[1])
    else:
        raise ValueError(f"Invalid token: {token_string}")


if __name__ == "__main__":
    print("Please enter the information below, and enter input file as 'done' to quit:")
    input_file = input("Please enter input file name: ")

    while input_file != "done":
        output_file = input("Please enter output file name: ")

        tokens = read_tokens(input_file)
        parser = Parser(tokens)
        try:
            tree = parser.parse(output_file)
            if parser.semantically_correct:
                with open(output_file, 'w') as output_file:
                    tree.print_tree(file_name=output_file)
        except Exception as e:
            print(f"Parse Error: {e}")

        input_file = input("Please enter input file name: ")

import re
import ast
import difflib
import sys

# --- Check availability of parser libraries ---
try:
    import clang.cindex
    # Import and run configuration logic from utils
    from utils import configure_clang
    CLANG_AVAILABLE = configure_clang(clang)
except ImportError:
    CLANG_AVAILABLE = False

try:
    import javalang
    JAVALANG_AVAILABLE = True
except ImportError:
    JAVALANG_AVAILABLE = False

# --- Analyzer Logic ---
def normalize_c_cpp_code(code_text):
    """Normalizes C/C++ code by generalizing identifiers using Clang."""
    if not CLANG_AVAILABLE: return code_text
    try:
        index = clang.cindex.Index.create()
        # Parse the code in memory
        tu = index.parse('tmp.cpp', args=['-std=c++11'], 
                         unsaved_files=[('tmp.cpp', code_text)], 
                         options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
        
        normalized_tokens, name_map, counter = [], {}, 0
        for token in tu.get_tokens(extent=tu.cursor.extent):
            # Process only identifiers, ignore comments
            if token.kind == clang.cindex.TokenKind.IDENTIFIER:
                if token.spelling not in name_map:
                    name_map[token.spelling] = f"ID_{counter}"
                    counter += 1
                normalized_tokens.append(name_map[token.spelling])
            elif token.kind != clang.cindex.TokenKind.COMMENT:
                normalized_tokens.append(token.spelling)
        return " ".join(normalized_tokens)
    except Exception as e:
        print(f"C/C++ parsing error: {e}")
        return code_text

def normalize_java_code(code_text):
    """Normalizes Java code by generalizing identifiers using javalang."""
    if not JAVALANG_AVAILABLE: return code_text
    try:
        tokens = list(javalang.tokenizer.tokenize(code_text))
        normalized_tokens, name_map, counter = [], {}, 0
        for token in tokens:
            if isinstance(token, javalang.tokenizer.Identifier):
                if token.value not in name_map:
                    name_map[token.value] = f"ID_{counter}"
                    counter += 1
                normalized_tokens.append(name_map[token.value])
            # Exclude comments and separators from the token stream
            elif not isinstance(token, (javalang.tokenizer.Comment, javalang.tokenizer.Separator)):
                normalized_tokens.append(token.value)
        return " ".join(normalized_tokens)
    except Exception as e:
        print(f"Java parsing error: {e}")
        return code_text

class AstNormalizer(ast.NodeTransformer):
    """A NodeTransformer to normalize identifiers in a Python AST."""
    def __init__(self):
        self.name_map, self.counter = {}, 0
    def _get_normalized_name(self, name, prefix):
        if name not in self.name_map:
            self.name_map[name] = f"{prefix}_{self.counter}"
            self.counter += 1
        return self.name_map[name]
    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Load, ast.Store)):
            node.id = self._get_normalized_name(node.id, "VAR")
        return node
    def visit_FunctionDef(self, node):
        node.name = self._get_normalized_name(node.name, "FUNC")
        self.generic_visit(node)
        return node
    def visit_arg(self, node):
        node.arg = self._get_normalized_name(node.arg, "ARG")
        return node

def normalize_python_code(code_text):
    """Normalizes Python code using the built-in AST module."""
    try:
        tree = ast.parse(code_text)
        normalizer = AstNormalizer()
        normalized_tree = normalizer.visit(tree)
        return ast.unparse(normalized_tree)
    except (SyntaxError, ValueError):
        # Fallback to text preprocessing if AST parsing fails
        return text_preprocess(code_text)

def text_preprocess(content):
    """Basic text preprocessing: remove comments and all whitespace."""
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL) # C-style block comments
    content = re.sub(r'//.*', '', content) # C++-style line comments
    content = re.sub(r'#.*', '', content) # Python-style line comments
    return "".join(content.split())

def calculate_similarity_fast(text1, text2):
    """Calculates similarity between two texts using difflib for speed."""
    if not text1 and not text2:
        return 1.0
    return difflib.SequenceMatcher(None, text1, text2, autojunk=False).ratio()

def process_content(content1, content2, mode):
    """Processes two code snippets based on the selected analysis mode and calculates their similarity."""
    processed1, processed2 = "", ""
    if mode == "python":
        processed1 = normalize_python_code(content1)
        processed2 = normalize_python_code(content2)
    elif mode == "c":
        processed1 = normalize_c_cpp_code(content1)
        processed2 = normalize_c_cpp_code(content2)
    elif mode == "java":
        processed1 = normalize_java_code(content1)
        processed2 = normalize_java_code(content2)
    else: # Default to basic text analysis
        processed1 = text_preprocess(content1)
        processed2 = text_preprocess(content2)
        
    return calculate_similarity_fast(processed1, processed2)

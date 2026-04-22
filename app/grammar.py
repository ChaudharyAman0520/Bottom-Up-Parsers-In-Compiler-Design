# grammar.py (Modified)

class Grammar:
    def __init__(self, grammar_text: str):
        self.productions = {}          
        self.production_list = []      
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None

        self._parse_grammar(grammar_text)
        self._extract_terminals()
        self._build_production_list()

    def _parse_grammar(self, grammar_text: str):
        lines = [line.strip() for line in grammar_text.strip().split("\n") if line.strip()]

        for line in lines:
            if "->" not in line:
                raise ValueError(f"Invalid production format: {line} [cite: 3]")
            
            left, _ = line.split("->", 1)
            left = left.strip()
            
            # RECTIFICATION: Ensure LHS is exactly one Non-Terminal
            if len(left.split()) > 1:
                raise ValueError(f"LHS '{left}' is invalid. CFG must have exactly one symbol on the left.")
            
            self.non_terminals.add(left)

        for index, line in enumerate(lines):
            left, right = line.split("->", 1)
            left = left.strip()

            if index == 0:
                self.start_symbol = left

            alternatives = right.split("|")
            if left not in self.productions:
                self.productions[left] = []

            for alt in alternatives:
                symbols = alt.strip().split()
                # If the line was "A -> ", symbols becomes an empty list (representing ε)
                self.productions[left].append(symbols if symbols else ['ε'])

    def _extract_terminals(self):
        for left in self.productions:
            for production in self.productions[left]:
                for symbol in production:
                    if symbol not in self.non_terminals and symbol != 'ε':
                        self.terminals.add(symbol) [cite: 6]

    def _build_production_list(self):
        for left in self.productions:
            for production in self.productions[left]:
                self.production_list.append((left, production))

    def augment_grammar(self):
        augmented_start = self.start_symbol + "'"
        self.productions[augmented_start] = [[self.start_symbol]]
        self.non_terminals.add(augmented_start)
        self.start_symbol = augmented_start [cite: 7]
        self.production_list = []
        self._build_production_list()
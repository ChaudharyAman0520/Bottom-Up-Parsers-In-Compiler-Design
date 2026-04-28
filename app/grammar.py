class Grammar:
    def __init__(self, grammar_text: str):
        self.raw_text = grammar_text
        self.productions = {}
        self.production_list = []
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None

        self._parse_grammar(grammar_text)
        self._extract_terminals()
        self._build_production_list()

    # ---------------- VALIDATION FUNCTION ---------------- #
    def validate_cfg(self):
        errors = []
        warnings = []

        lines = [l.strip() for l in self.raw_text.split("\n") if l.strip()]
        if not lines:
            return ["Grammar is empty"], []

        defined_nt = set()
        used_symbols = set()

        for i, line in enumerate(lines):

            if "->" not in line:
                errors.append(f"Line {i+1}: Missing '->'")
                continue

            left, right = line.split("->", 1)
            left = left.strip()

            # LHS validation
            if len(left.split()) != 1 or not left.isupper() or len(left) != 1:
                errors.append(f"Line {i+1}: LHS must be a single uppercase letter")

            defined_nt.add(left)

            # RHS validation
            alternatives = right.split("|")

            if not alternatives:
                errors.append(f"Line {i+1}: RHS empty")

            for alt in alternatives:
                alt = alt.strip()

                if alt == "":
                    errors.append(f"Line {i+1}: Empty production (use ε)")
                    continue

                symbols = alt.split()

                for sym in symbols:
                    used_symbols.add(sym)

                    if sym == "->":
                        errors.append(f"Line {i+1}: Invalid '->' in RHS")

                    if sym == "ε":
                        if len(symbols) > 1:
                            errors.append(f"Line {i+1}: ε must be alone")
                        continue

                    if not sym.isalnum() and sym not in ['+', '-', '*', '/', '(', ')', '=']:
                        errors.append(f"Line {i+1}: Invalid symbol '{sym}'")

                    if sym.isupper() and len(sym) != 1:
                        errors.append(f"Line {i+1}: Invalid non-terminal '{sym}'")

        # Undefined non-terminals
        for sym in used_symbols:
            if sym.isupper() and sym not in defined_nt:
                errors.append(f"Undefined non-terminal: {sym}")

        return errors, warnings

    # ---------------- PARSING ---------------- #
    def _parse_grammar(self, grammar_text: str):
        lines = [l.strip() for l in grammar_text.strip().split("\n") if l.strip()]

        for i, line in enumerate(lines):
            left, right = line.split("->")
            left = left.strip()

            if i == 0:
                self.start_symbol = left

            self.non_terminals.add(left)
            self.productions.setdefault(left, [])

            for alt in right.split("|"):
                symbols = alt.strip().split()
                self.productions[left].append(symbols if symbols else [])

    def _extract_terminals(self):
        for left in self.productions:
            for prod in self.productions[left]:
                for sym in prod:
                    if sym not in self.non_terminals:
                        self.terminals.add(sym)

    def _build_production_list(self):
        self.production_list = []
        for left in self.productions:
            for prod in self.productions[left]:
                self.production_list.append((left, prod))

    def augment_grammar(self):
        new_start = self.start_symbol + "'"
        self.productions[new_start] = [[self.start_symbol]]
        self.non_terminals.add(new_start)
        self.start_symbol = new_start
        self._build_production_list()
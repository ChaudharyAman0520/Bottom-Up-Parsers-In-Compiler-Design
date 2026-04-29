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
        """
        Validates that the given grammar text is a well-formed Context-Free Grammar.

        CFG rules enforced:
          1. Every line must contain exactly one '->' arrow.
          2. LHS must be a single token (no whitespace-separated multi-symbol LHS).
          3. LHS token must start with a letter.
          4. LHS token must be uppercase (non-terminal convention).
          5. Duplicate LHS definitions are flagged as warnings.
          6. RHS of each rule must not be completely empty.
          7. Each '|'-separated alternative must not be blank.
          8. '->' must NOT appear inside the RHS.
          9. 'epsilon' / 'ε' must appear ALONE in an alternative (not mixed with other symbols).
         10. Every uppercase symbol used on the RHS must be defined somewhere as an LHS.
         11. Grammar must not be empty.
        """
        errors = []
        warnings = []

        lines = [l.strip() for l in self.raw_text.split("\n") if l.strip()]

        # ── Rule 11: Grammar must not be empty ───────────────────────────────
        if not lines:
            return ["Grammar is empty."], []

        EPSILON_TOKENS = {"ε", "epsilon"}

        defined_nt = set()      # LHS non-terminals that have been declared
        lhs_order = []          # tracks first-seen order
        all_rhs_symbols = set() # every symbol that appears on any RHS (non-epsilon)

        for i, line in enumerate(lines):
            lineno = i + 1

            # ── Rule 1: Must contain '->' ─────────────────────────────────────
            if "->" not in line:
                errors.append(
                    f"Line {lineno}: Missing '->' arrow. "
                    f"Every production rule must be of the form  A -> α."
                )
                continue

            # Split only on the FIRST '->' so that '->' in RHS is detected separately
            left_raw, right_raw = line.split("->", 1)
            left = left_raw.strip()
            right = right_raw.strip()

            # ── Rule 2: LHS must be a single token ───────────────────────────
            lhs_parts = left.split()
            if len(lhs_parts) == 0:
                errors.append(
                    f"Line {lineno}: LHS is empty — a single non-terminal is required "
                    f"on the left-hand side of a CFG production."
                )
                continue
            if len(lhs_parts) > 1:
                errors.append(
                    f"Line {lineno}: LHS '{left}' contains {len(lhs_parts)} tokens "
                    f"({', '.join(lhs_parts)}). A CFG production must have exactly ONE "
                    f"non-terminal on the left-hand side."
                )
                continue

            lhs_sym = lhs_parts[0]

            # ── Rule 3: LHS must start with a letter ─────────────────────────
            if not lhs_sym[0].isalpha():
                errors.append(
                    f"Line {lineno}: LHS '{lhs_sym}' must start with a letter, "
                    f"not '{lhs_sym[0]}'."
                )
                continue

            # ── Rule 4: LHS must be a non-terminal (uppercase first letter) ──
            if not lhs_sym[0].isupper():
                errors.append(
                    f"Line {lineno}: LHS '{lhs_sym}' starts with a lowercase letter. "
                    f"Non-terminals must begin with an uppercase letter (e.g. S, A, Expr)."
                )

            # ── Rule 5: Duplicate LHS detection ──────────────────────────────
            if lhs_sym in defined_nt:
                warnings.append(
                    f"Line {lineno}: Non-terminal '{lhs_sym}' is defined more than once. "
                    f"Merge all productions into one rule using '|' to separate alternatives."
                )
            else:
                defined_nt.add(lhs_sym)
                lhs_order.append(lhs_sym)

            # ── Rule 6: RHS must not be completely blank ──────────────────────
            if not right:
                errors.append(
                    f"Line {lineno}: RHS of '{lhs_sym}' is empty. "
                    f"Use 'ε' or 'epsilon' to denote an epsilon (empty-string) production."
                )
                continue

            # Split alternatives on '|'
            alternatives = right.split("|")

            for j, alt in enumerate(alternatives):
                alt_stripped = alt.strip()
                alt_label = f"Line {lineno}, alternative {j + 1}"

                # ── Rule 7: Each alternative must not be blank ───────────────
                if alt_stripped == "":
                    errors.append(
                        f"{alt_label}: Empty alternative between '|'. "
                        f"Use 'ε' or 'epsilon' for an empty (epsilon) production body."
                    )
                    continue

                symbols = alt_stripped.split()

                # ── Rule 8: '->' must NOT appear in RHS ──────────────────────
                for sym in symbols:
                    if sym == "->":
                        errors.append(
                            f"{alt_label}: Found '->' inside the RHS of '{lhs_sym}'. "
                            f"'->' is the production arrow and must not appear in the body."
                        )

                # Normalise epsilon tokens
                norm = [s.lower() if s.lower() in EPSILON_TOKENS else s for s in symbols]
                has_epsilon = any(s in EPSILON_TOKENS for s in norm)

                # ── Rule 9: ε must be the ONLY symbol in an alternative ──────
                if has_epsilon and len(symbols) > 1:
                    non_eps = [s for s in symbols if s.lower() not in EPSILON_TOKENS]
                    errors.append(
                        f"{alt_label}: 'ε'/'epsilon' must appear alone in a production body. "
                        f"Found extra symbol(s): {', '.join(non_eps)}."
                    )
                    continue

                # Collect RHS symbols (skip epsilon tokens)
                if not has_epsilon:
                    for sym in symbols:
                        all_rhs_symbols.add(sym)

        # ── Rule 10: Every uppercase RHS symbol must be a defined LHS ────────
        for sym in sorted(all_rhs_symbols):
            if sym and sym[0].isupper() and sym not in defined_nt:
                errors.append(
                    f"Undefined non-terminal '{sym}': used on the RHS but never "
                    f"defined as the head of any production rule."
                )

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
                # Standardize epsilon representations
                symbols = ['ε' if s.lower() == 'epsilon' or s == 'ε' else s for s in symbols]

                # If the production is just epsilon, represent it as an empty list
                if symbols == ['ε']:
                    symbols = []
                elif 'ε' in symbols:
                    symbols = [s for s in symbols if s != 'ε']

                self.productions[left].append(symbols)

    def _extract_terminals(self):
        for left in self.productions:
            for prod in self.productions[left]:
                for sym in prod:
                    if sym not in self.non_terminals and sym != 'ε':
                        self.terminals.add(sym)

    def _build_production_list(self):
        self.production_list = []
        for left in self.productions:
            for prod in self.productions[left]:
                self.production_list.append((left, prod))

    def augment_grammar(self):
        if not self.start_symbol:
            return
        # Ensure augmented start symbol is unique
        new_start = self.start_symbol + "'"
        while new_start in self.non_terminals:
            new_start += "'"

        self.productions[new_start] = [[self.start_symbol]]
        self.non_terminals.add(new_start)
        self.start_symbol = new_start
        self._build_production_list()
from lr0 import LR0

class CLR1(LR0):
    def __init__(self, grammar, first_follow):
        super().__init__(grammar)
        self.ff = first_follow

    # ---------------- ITEM ---------------- #
    def create_item(self, left, right, dot, lookahead):
        return (left, tuple(right), dot, lookahead)

    # ---------------- FIRST ---------------- #
    def compute_first_of_sequence(self, symbols):
        result = set()

        for symbol in symbols:
            if symbol in self.grammar.terminals:
                result.add(symbol)
                return result

            if symbol not in self.ff.first:
                continue

            result |= (self.ff.first[symbol] - {'ε'})

            if 'ε' not in self.ff.first[symbol]:
                return result

        result.add('$')
        return result

    # ---------------- CLOSURE ---------------- #
    def closure(self, items):
        closure_set = set(items)

        while True:
            new_items = set()

            for (left, right, dot, lookahead) in closure_set:
                if dot >= len(right):
                    continue

                next_symbol = right[dot]

                if next_symbol in self.grammar.non_terminals:
                    remaining = list(right[dot + 1:]) + [lookahead]
                    lookaheads = self.compute_first_of_sequence(remaining)

                    for production in self.grammar.productions[next_symbol]:
                        for la in lookaheads:
                            new_item = self.create_item(next_symbol, production, 0, la)
                            if new_item not in closure_set:
                                new_items.add(new_item)

            if not new_items:
                break

            closure_set |= new_items

        return closure_set

    # ---------------- GOTO ---------------- #
    def goto(self, items, symbol):
        moved = {
            self.create_item(left, right, dot + 1, la)
            for (left, right, dot, la) in items
            if dot < len(right) and right[dot] == symbol
        }

        return self.closure(moved) if moved else set()

    # ---------------- STATES ---------------- #
    def build_canonical_collection(self):
        start_item = self.create_item(
            self.grammar.start_symbol,
            self.grammar.productions[self.grammar.start_symbol][0],
            0,
            '$'
        )

        self.states = [self.closure({start_item})]
        symbols = list(self.grammar.non_terminals | self.grammar.terminals)

        while True:
            new_states = []

            for state in self.states:
                for symbol in symbols:
                    next_state = self.goto(state, symbol)

                    if next_state and next_state not in self.states and next_state not in new_states:
                        new_states.append(next_state)

            if not new_states:
                break

            self.states.extend(new_states)

        return self.states

    # ---------------- PRODUCTION LOOKUP ---------------- #
    def find_production_index(self, left, right):
        for idx, (l, r) in enumerate(self.grammar.production_list):
            if l == left and r == list(right):
                return idx
        return None

    # ---------------- PARSING TABLE ---------------- #
    def build_parsing_table(self):
        action = {}
        goto_table = {}
        conflicts = []

        for state_index, state in enumerate(self.states):
            action[state_index] = {}
            goto_table[state_index] = {}

            for (left, right, dot, lookahead) in state:

                # SHIFT / GOTO
                if dot < len(right):
                    symbol = right[dot]
                    next_state = self.goto(state, symbol)

                    if next_state in self.states:
                        target = self.states.index(next_state)

                        if symbol in self.grammar.terminals:
                            if symbol in action[state_index] and action[state_index][symbol] != f"s{target}":
                                conflicts.append((state_index, symbol))
                            action[state_index][symbol] = f"s{target}"
                        else:
                            goto_table[state_index][symbol] = target

                # REDUCE / ACCEPT
                else:
                    if left == self.grammar.start_symbol:
                        action[state_index]['$'] = "acc"
                        continue

                    prod_index = self.find_production_index(left, right)

                    if prod_index is None:
                        continue  # safe skip

                    if lookahead in action[state_index] and action[state_index][lookahead] != f"r{prod_index}":
                        conflicts.append((state_index, lookahead))

                    action[state_index][lookahead] = f"r{prod_index}"

        return action, goto_table, conflicts

class LR0:
    def __init__(self, grammar):
        self.grammar = grammar
        self.states = []

    # ---------------- ITEM ---------------- #
    def create_item(self, left, right, dot):
        return (left, tuple(right), dot)

    # ---------------- CLOSURE ---------------- #
    def closure(self, items):
        closure_set = set(items)

        while True:
            new_items = set()

            for (left, right, dot) in closure_set:
                if dot < len(right):
                    symbol = right[dot]

                    if symbol in self.grammar.non_terminals:
                        for production in self.grammar.productions[symbol]:
                            new_item = self.create_item(symbol, production, 0)
                            if new_item not in closure_set:
                                new_items.add(new_item)

            if not new_items:
                break

            closure_set.update(new_items)

        return closure_set

    # ---------------- GOTO ---------------- #
    def goto(self, items, symbol):
        moved_items = set()

        for (left, right, dot) in items:
            if dot < len(right) and right[dot] == symbol:
                moved_items.add(self.create_item(left, right, dot + 1))

        return self.closure(moved_items)

    # ---------------- CANONICAL COLLECTION ---------------- #
    def build_canonical_collection(self):
        start_prod = self.grammar.productions[self.grammar.start_symbol][0]
        start_item = self.create_item(self.grammar.start_symbol, start_prod, 0)

        start_state = self.closure({start_item})
        self.states = [start_state]

        symbols = list(self.grammar.non_terminals) + list(self.grammar.terminals)

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

    # ---------------- LR(0) PARSING TABLE ---------------- #
    def build_parsing_table(self):
        action = {}
        goto_table = {}

        # Use set → avoids duplicate conflicts
        conflicts = set()

        for i, state in enumerate(self.states):
            action[i] = {}
            goto_table[i] = {}

            for (left, right, dot) in state:

                # -------- SHIFT / GOTO -------- #
                if dot < len(right):
                    symbol = right[dot]
                    next_state = self.goto(state, symbol)

                    if next_state in self.states:
                        j = self.states.index(next_state)

                        if symbol in self.grammar.terminals:
                            # SHIFT
                            if symbol in action[i] and action[i][symbol] != f"s{j}":
                                conflicts.add((
                                    i,
                                    symbol,
                                    action[i][symbol],
                                    f"s{j}",
                                    "shift-conflict"
                                ))
                            action[i][symbol] = f"s{j}"

                        else:
                            # GOTO
                            goto_table[i][symbol] = j

                # -------- REDUCE / ACCEPT -------- #
                else:
                    if left == self.grammar.start_symbol:
                        action[i]['$'] = "acc"
                    else:
                        prod_index = self.grammar.production_list.index(
                            (left, list(right))
                        )

                        for terminal in self.grammar.terminals.union({'$'}):
                            if terminal in action[i] and action[i][terminal] != f"r{prod_index}":
                                conflict_type = (
                                    "shift-reduce"
                                    if action[i][terminal].startswith("s")
                                    else "reduce-reduce"
                                )

                                conflicts.add((
                                    i,
                                    terminal,
                                    action[i][terminal],
                                    f"r{prod_index}",
                                    conflict_type
                                ))

                            action[i][terminal] = f"r{prod_index}"

        # Convert conflicts to readable list
        conflicts_list = [
            {
                "state": c[0],
                "symbol": c[1],
                "existing": c[2],
                "incoming": c[3],
                "type": c[4]
            }
            for c in conflicts
        ]

        return action, goto_table, conflicts_list

    # ---------------- SHIFT-REDUCE PARSER ---------------- #
    def parse_string(self, action_table, goto_table, input_string):
        stack = [0]
        input_tokens = input_string.split() + ['$']
        index = 0
        steps = []

        while True:
            state = stack[-1]
            current_token = input_tokens[index]

            action = action_table.get(state, {}).get(current_token)

            steps.append({
                "stack": stack.copy(),
                "input": input_tokens[index:],
                "action": action
            })

            if action is None:
                return {"result": "ERROR", "steps": steps}

            # -------- SHIFT -------- #
            if action.startswith("s"):
                next_state = int(action[1:])
                stack.append(current_token)
                stack.append(next_state)
                index += 1

            # -------- REDUCE -------- #
            elif action.startswith("r"):
                prod_index = int(action[1:])
                left, right = self.grammar.production_list[prod_index]

                for _ in range(2 * len(right)):
                    stack.pop()

                state = stack[-1]
                stack.append(left)
                stack.append(goto_table[state][left])

            # -------- ACCEPT -------- #
            elif action == "acc":
                return {"result": "ACCEPT", "steps": steps}
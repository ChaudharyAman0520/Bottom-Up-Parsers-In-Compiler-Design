# slr1.py

from first_follow.first_follow import FirstFollow
from lr0 import LR0

class SLR1(LR0):
    def __init__(self, grammar):
        super().__init__(grammar)

    # ---------------- SLR(1) TABLE ---------------- #
    def build_parsing_table_slr(self, first_follow: FirstFollow):
        """
        Build the SLR(1) parsing table.
        Uses FOLLOW sets to restrict reduce actions.
        """
        action = {}
        goto_table = {}
        conflicts = []

        # compute FOLLOW sets
        follow = first_follow.compute_follow()

        for i, state in enumerate(self.states):
            action[i] = {}
            goto_table[i] = {}

            for (left, right, dot) in state:

                # ---------------- SHIFT / GOTO ---------------- #
                if dot < len(right):
                    symbol = right[dot]
                    next_state = self.goto(state, symbol)

                    if next_state in self.states:
                        j = self.states.index(next_state)

                        if symbol in self.grammar.terminals:
                            if symbol in action[i] and action[i][symbol] != f"s{j}":
                                conflicts.append({
                                    "state": i,
                                    "symbol": symbol,
                                    "existing": action[i][symbol],
                                    "incoming": f"s{j}"
                                })
                            action[i][symbol] = f"s{j}"
                        else:
                            goto_table[i][symbol] = j

                # ---------------- REDUCE / ACCEPT ---------------- #
                else:
                    if left == self.grammar.start_symbol:
                        action[i]['$'] = "acc"
                    else:
                        prod_index = self.grammar.production_list.index((left, list(right)))

                        # Only reduce on FOLLOW(left)
                        for terminal in follow[left]:
                            if terminal in action[i] and action[i][terminal] != f"r{prod_index}":
                                conflicts.append({
                                    "state": i,
                                    "symbol": terminal,
                                    "existing": action[i][terminal],
                                    "incoming": f"r{prod_index}"
                                })
                            action[i][terminal] = f"r{prod_index}"

        return action, goto_table, conflicts
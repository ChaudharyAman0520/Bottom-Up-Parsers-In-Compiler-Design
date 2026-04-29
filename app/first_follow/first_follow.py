class FirstFollow:
    def __init__(self, grammar):
        self.grammar = grammar
        self.first = {nt: set() for nt in grammar.non_terminals}
        self.follow = {nt: set() for nt in grammar.non_terminals}

    

    def compute_first(self):
        changed = True

        while changed:
            changed = False

            for left in self.grammar.productions:
                for production in self.grammar.productions[left]:

                    add_epsilon = True

                    for symbol in production:

                        if symbol == 'ε':
                            continue

                        # terminal
                        if symbol in self.grammar.terminals:
                            if symbol not in self.first[left]:
                                self.first[left].add(symbol)
                                changed = True
                            add_epsilon = False
                            break

                        # non-terminal
                        elif symbol in self.grammar.non_terminals:
                            before = len(self.first[left])

                            self.first[left].update(self.first[symbol] - {'ε'})

                            if len(self.first[left]) > before:
                                changed = True

                            if 'ε' not in self.first[symbol]:
                                add_epsilon = False
                                break
                        else:
                            # Should not happen if grammar is valid, but safe fallback
                            add_epsilon = False
                            break

                    if add_epsilon:
                        if 'ε' not in self.first[left]:
                            self.first[left].add('ε')
                            changed = True

        return self.first

    def compute_follow(self):
    
        self.follow[self.grammar.start_symbol].add('$')

        changed = True

        while changed:
            changed = False

            for left in self.grammar.productions:
                for production in self.grammar.productions[left]:

                    for i in range(len(production)):
                        symbol = production[i]

                        if symbol in self.grammar.non_terminals:
                            # Compute FIRST of β (everything after symbol)
                            beta_first = set()
                            add_follow_later = True  # whether β can produce ε

                            for j in range(i + 1, len(production)):
                                next_sym = production[j]

                                if next_sym == 'ε':
                                    continue

                                if next_sym in self.grammar.terminals:
                                    beta_first.add(next_sym)
                                    add_follow_later = False
                                    break
                                elif next_sym in self.grammar.non_terminals:
                                    beta_first.update(self.first[next_sym] - {'ε'})
                                    if 'ε' not in self.first[next_sym]:
                                        add_follow_later = False
                                        break
                                else:
                                    add_follow_later = False
                                    break

                            # Add FIRST(β) - {ε} to FOLLOW(symbol)
                            before = len(self.follow[symbol])
                            self.follow[symbol].update(beta_first)

                            # If β can produce ε (or β is empty), add FOLLOW(left)
                            if add_follow_later or i == len(production) - 1:
                                self.follow[symbol].update(self.follow[left])

                            if len(self.follow[symbol]) > before:
                                changed = True

        return self.follow
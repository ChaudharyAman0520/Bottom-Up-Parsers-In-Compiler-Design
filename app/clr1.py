from .lr0 import LR0

class CLR1(LR0):
    def __init__(self, grammar, first_follow):
        super().__init__(grammar)
        self.ff = first_follow

    def create_clr_item(self, left, right, dot, lookahead):
        # Items are now (left, right, dot, lookahead)
        return (left, tuple(right), dot, lookahead)

    def get_first_of_string(self, symbols):
        """Helper to get FIRST set of a sequence of symbols."""
        res = set()
        for s in symbols:
            if s in self.grammar.terminals:
                res.add(s)
                return res
            res.update(self.ff.first[s] - {'ε'})
            if 'ε' not in self.ff.first[s]:
                return res
        res.add('$')
        return res

    def closure(self, items):
        closure_set = set(items)
        changed = True
        while changed:
            changed = False
            new_items = set()
            for (left, right, dot, lookahead) in closure_set:
                if dot < len(right):
                    symbol = right[dot]
                    if symbol in self.grammar.non_terminals:
                        # Find lookaheads for the new items: FIRST(beta + lookahead)
                        beta = list(right[dot+1:]) + [lookahead]
                        next_lookaheads = self.get_first_of_string(beta)
                        
                        for prod in self.grammar.productions[symbol]:
                            for nl in next_lookaheads:
                                item = self.create_clr_item(symbol, prod, 0, nl)
                                if item not in closure_set:
                                    new_items.add(item)
            if new_items:
                closure_set.update(new_items)
                changed = True
        return closure_set

    def goto(self, items, symbol):
        moved_items = set()
        for (left, right, dot, lookahead) in items:
            if dot < len(right) and right[dot] == symbol:
                moved_items.add(self.create_clr_item(left, right, dot + 1, lookahead))
        return self.closure(moved_items)

    def build_canonical_collection(self):
        start_prod = self.grammar.productions[self.grammar.start_symbol][0]
        start_item = self.create_clr_item(self.grammar.start_symbol, start_prod, 0, '$')
        self.states = [self.closure({start_item})]
        
        symbols = list(self.grammar.non_terminals) + list(self.grammar.terminals)
        changed = True
        while changed:
            changed = False
            for state in self.states:
                for sym in symbols:
                    nxt = self.goto(state, sym)
                    if nxt and nxt not in self.states:
                        self.states.append(nxt)
                        changed = True
        return self.states
from .clr1 import CLR1

class LALR1(CLR1):
    def __init__(self, grammar):
        super().__init__(grammar)

    def build_canonical_collection(self):
        # 1. Build CLR(1) states first
        clr_states = super().build_canonical_collection()
        
        # 2. Merge states with the same kernel (core items)
        kernels = {} # {kernel: [state_indices]}
        
        for i, state in enumerate(clr_states):
            # A kernel is (left, right, dot)
            kernel = frozenset([(left, right, dot) for (left, right, dot, la) in state])
            if kernel not in kernels:
                kernels[kernel] = []
            kernels[kernel].append(i)
        
        new_states = []
        old_to_new = {} # {old_index: new_index}
        
        for kernel, indices in kernels.items():
            merged_state = set()
            new_index = len(new_states)
            for idx in indices:
                merged_state.update(clr_states[idx])
                old_to_new[idx] = new_index
            new_states.append(merged_state)
            
        self.states = new_states
        return self.states

    # Override goto to work with merged states
    def goto(self, items, symbol):
        res = super().goto(items, symbol)
        # In LALR, we need to find which merged state this corresponds to
        # But build_parsing_table uses self.states, so we need to be careful.
        # Actually, if we just rebuild the table using the merged states, 
        # we need a way to identify the target state index.
        return res

    def build_parsing_table(self):
        # We need to re-run the table logic with merged states
        # The issue is self.goto(state, symbol) returns a set of items 
        # which might not be EXACTLY in self.states (because of lookaheads).
        # We need to match by KERNEL.
        
        action = {}
        goto_table = {}
        conflicts = []

        for i, state in enumerate(self.states):
            action[i] = {}
            goto_table[i] = {}
            
            for (left, right, dot, lookahead) in state:
                if dot < len(right):
                    symbol = right[dot]
                    next_state_items = super().goto(state, symbol)
                    if next_state_items:
                        # Find which state in self.states has the same kernel
                        next_kernel = frozenset([(l, r, d) for (l, r, d, la) in next_state_items])
                        target_idx = -1
                        for idx, s in enumerate(self.states):
                            if frozenset([(l, r, d) for (l, r, d, la) in s]) == next_kernel:
                                target_idx = idx
                                break
                        
                        if target_idx != -1:
                            if symbol in self.grammar.terminals:
                                if symbol in action[i] and action[i][symbol] != f"s{target_idx}":
                                    conflicts.append({
                                        "state": i, "symbol": symbol,
                                        "existing": action[i][symbol], "incoming": f"s{target_idx}"
                                    })
                                action[i][symbol] = f"s{target_idx}"
                            else:
                                goto_table[i][symbol] = target_idx
                else:
                    if left == self.grammar.start_symbol:
                        action[i]['$'] = "acc"
                    else:
                        prod_index = self.grammar.production_list.index((left, list(right)))
                        if lookahead in action[i] and action[i][lookahead] != f"r{prod_index}":
                            conflicts.append({
                                "state": i, "symbol": lookahead,
                                "existing": action[i][lookahead], "incoming": f"r{prod_index}"
                            })
                        action[i][lookahead] = f"r{prod_index}"
        
        return action, goto_table, conflicts

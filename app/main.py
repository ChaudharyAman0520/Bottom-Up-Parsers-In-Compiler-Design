from fastapi import FastAPI
from pydantic import BaseModel
from grammar import Grammar
from first_follow.first_follow import FirstFollow
from lr0 import LR0
from slr1 import SLR1  # ✅ new
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ allow all (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GrammarInput(BaseModel):
    grammar: str

class ParseInput(BaseModel):
    grammar: str
    input_string: str


@app.get("/")
def root():
    return {"message": "Compiler Parser Backend Running"}


# ---------------- FIRST/FOLLOW ---------------- #
@app.post("/first-follow")
def compute_sets(data: GrammarInput):
    g = Grammar(data.grammar)
    # g.augment_grammar()

    ff = FirstFollow(g)
    first = ff.compute_first()
    follow = ff.compute_follow()

    return {
        "first": {k: list(v) for k, v in first.items()},
        "follow": {k: list(v) for k, v in follow.items()}
    }


# ---------------- TEST CLOSURE ---------------- #
@app.post("/test-closure")
def test_closure(data: GrammarInput):
    g = Grammar(data.grammar)
    g.augment_grammar()

    lr = LR0(g)
    start_prod = g.productions[g.start_symbol][0]
    start_item = lr.create_item(g.start_symbol, start_prod, 0)

    closure = lr.closure({start_item})

    return {
        "closure": [
            {"left": item[0], "right": list(item[1]), "dot": item[2]}
            for item in closure
        ]
    }


# ---------------- LR(0) STATES ---------------- #
@app.post("/lr0-states")
def generate_lr0(data: GrammarInput):
    g = Grammar(data.grammar)
    g.augment_grammar()

    lr = LR0(g)
    states = lr.build_canonical_collection()

    result = []
    transitions = []
    symbols = list(g.non_terminals) + list(g.terminals)

    for i, state in enumerate(states):
        items = []
        for (left, right, dot) in state:
            items.append({"left": left, "right": list(right), "dot": dot})
        result.append({"state": i, "items": items})

        # compute transitions
        for symbol in symbols:
            next_state = lr.goto(state, symbol)
            if next_state and next_state in states:
                j = states.index(next_state)
                transitions.append({"from": i, "symbol": symbol, "to": j})

    return {"total_states": len(states), "states": result, "transitions": transitions}


# ---------------- LR(0) TABLE ---------------- #
@app.post("/lr0-table")
def generate_lr0_table(data: GrammarInput):
    g = Grammar(data.grammar)
    g.augment_grammar()

    lr = LR0(g)
    lr.build_canonical_collection()
    action, goto_table, conflicts = lr.build_parsing_table()
    return {"action": action, "goto": goto_table, "conflicts": conflicts}


# ---------------- LR(0) PARSE ---------------- #
@app.post("/lr0-parse")
def parse_lr0(data: ParseInput):
    g = Grammar(data.grammar)
    g.augment_grammar()

    lr = LR0(g)
    lr.build_canonical_collection()
    action, goto_table, conflicts = lr.build_parsing_table()

    if conflicts:
        return {"error": "Grammar is not LR(0)", "conflicts": conflicts}

    result = lr.parse_string(action, goto_table, data.input_string)
    return result


# ---------------- SLR(1) STATES ---------------- #
@app.post("/slr1-states")
def generate_slr1_states(data: GrammarInput):
    g = Grammar(data.grammar)
    g.augment_grammar()

    slr = SLR1(g)
    slr.build_canonical_collection()

    result = []
    transitions = []
    symbols = list(g.non_terminals) + list(g.terminals)

    for i, state in enumerate(slr.states):
        items = []
        for (left, right, dot) in state:
            items.append({"left": left, "right": list(right), "dot": dot})
        result.append({"state": i, "items": items})

        for symbol in symbols:
            next_state = slr.goto(state, symbol)
            if next_state and next_state in slr.states:
                j = slr.states.index(next_state)
                transitions.append({"from": i, "symbol": symbol, "to": j})

    return {"total_states": len(slr.states), "states": result, "transitions": transitions}


# ---------------- SLR(1) TABLE ---------------- #
@app.post("/slr1-table")
def generate_slr1_table(data: GrammarInput):
    g = Grammar(data.grammar)
    g.augment_grammar()

    ff = FirstFollow(g)
    ff.compute_first()

    slr = SLR1(g)
    slr.build_canonical_collection()
    action, goto_table, conflicts = slr.build_parsing_table_slr(ff)

    return {"action": action, "goto": goto_table, "conflicts": conflicts}


# ---------------- SLR(1) PARSE ---------------- #
@app.post("/slr1-parse")
def parse_slr1(data: ParseInput):
    g = Grammar(data.grammar)
    g.augment_grammar()

    ff = FirstFollow(g)
    ff.compute_first()

    slr = SLR1(g)
    slr.build_canonical_collection()
    action, goto_table, conflicts = slr.build_parsing_table_slr(ff)

    if conflicts:
        return {"error": "Grammar is not SLR(1)", "conflicts": conflicts}

    result = slr.parse_string(action, goto_table, data.input_string)
    return result
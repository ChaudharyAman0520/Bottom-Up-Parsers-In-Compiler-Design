import { useState } from "react";
import StatesView from "./components/StatesView";
import ParsingTable from "./components/ParsingTable";
import GrammarDisplay from "./components/GrammarDisplay";

const BASE_URL = "http://localhost:8000";

function App() {
  const [grammar, setGrammar] = useState("");
  const [states, setStates] = useState([]);
  const [action, setAction] = useState({});
  const [gotoTable, setGotoTable] = useState({});
  const [inputString, setInputString] = useState("");
  const [parseSteps, setParseSteps] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [parseResult, setParseResult] = useState("");
  const [parserType, setParserType] = useState("lr0"); // "lr0" or "slr1"

  const handleParseGrammar = async () => {
    try {
      const [statesRes, tableRes] = await Promise.all([
        fetch(`${BASE_URL}/${parserType}-states`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ grammar }),
        }),
        fetch(`${BASE_URL}/${parserType}-table`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ grammar }),
        }),
      ]);

      const statesData = await statesRes.json();
      const tableData = await tableRes.json();

      setStates(statesData.states || []);
      setAction(tableData.action || {});
      setGotoTable(tableData.goto || {});
      setConflicts(tableData.conflicts || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleParseInput = async () => {
    try {
      const res = await fetch(`${BASE_URL}/${parserType}-parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ grammar, input_string: inputString }),
      });

      const data = await res.json();

      if (data.error) {
        setParseResult(data.error);
        setParseSteps([]);
        return;
      }

      setParseSteps(data.steps || []);
      setParseResult(data.result);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "monospace" }}>
      <h1 style={{ textAlign: "center" }}>LR(0) / SLR(1) Visualizer</h1>

      <textarea
        rows={6}
        value={grammar}
        onChange={(e) => setGrammar(e.target.value)}
        placeholder={`Enter grammar

Example:
S -> L = R | R
L -> * R | id
R -> L`}
        style={{ width: "400px", marginBottom: "10px" }}
      />

      <br />

      <div style={{ textAlign: "center", marginBottom: "10px" }}>
        <button
          onClick={() => setParserType("lr0")}
          style={{ marginRight: "10px", fontWeight: parserType === "lr0" ? "bold" : "normal" }}
        >
          LR(0)
        </button>
        <button
          onClick={() => setParserType("slr1")}
          style={{ fontWeight: parserType === "slr1" ? "bold" : "normal" }}
        >
          SLR(1)
        </button>
      </div>

      <button onClick={handleParseGrammar}>Process Grammar</button>

      <GrammarDisplay grammar={grammar} />

      {/* STATES + TABLE */}
      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
        {/* LEFT: STATES */}
        <div style={{ flex: 1, border: "2px solid yellow", padding: "10px" }}>
          <h2 style={{ textAlign: "center" }}>States</h2>
          <StatesView states={states} />
        </div>

        {/* RIGHT: TABLE */}
        <div style={{ flex: 1, border: "2px solid yellow", padding: "10px" }}>
          <ParsingTable action={action} gotoTable={gotoTable} conflicts={conflicts} parserType={parserType} />
        </div>
      </div>

      {/* INPUT SECTION */}
      <div style={{ marginTop: "30px", textAlign: "center" }}>
        <h2>Parse Input</h2>
        <input
          type="text"
          value={inputString}
          onChange={(e) => setInputString(e.target.value)}
          placeholder="e.g. id = id"
          style={{ marginRight: "10px" }}
        />
        <button onClick={handleParseInput}>Parse</button>
      </div>

      {/* PARSE STEPS */}
      <div style={{ marginTop: "20px", textAlign: "center" }}>
        {parseSteps.length > 0 && (
          <>
            <h3>Parsing Steps</h3>
            <table border="1" cellPadding="5" style={{ margin: "0 auto" }}>
              <thead>
                <tr>
                  <th>Stack</th>
                  <th>Input</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {parseSteps.map((step, idx) => (
                  <tr key={idx}>
                    <td>{step.stack.join(" ")}</td>
                    <td>{step.input.join(" ")}</td>
                    <td>{step.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

        {parseResult && <div style={{ marginTop: "10px" }}>Result: {parseResult}</div>}
      </div>
    </div>
  );
}

export default App;
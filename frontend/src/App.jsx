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
  <div className="app-container">
    <h1 className="title">LR Parser Visualizer</h1>

    <div style={{ textAlign: "center" }}>
      <textarea
        rows={6}
        value={grammar}
        onChange={(e) => setGrammar(e.target.value)}
        placeholder={`Enter grammar

Example:
S -> L = R | R
L -> * R | id
R -> L`}
      />
    </div>

    {/* PARSER SELECT */}
    <div style={{ textAlign: "center", marginTop: "10px" }}>
      <button
        onClick={() => setParserType("lr0")}
        className={parserType === "lr0" ? "active-btn" : ""}
      >
        LR(0)
      </button>

      <button
        onClick={() => setParserType("slr1")}
        className={parserType === "slr1" ? "active-btn" : ""}
        style={{ marginLeft: "10px" }}
      >
        SLR(1)
      </button>
    </div>

    <div style={{ textAlign: "center", marginTop: "10px" }}>
      <button onClick={handleParseGrammar}>Process Grammar</button>
    </div>

    <GrammarDisplay grammar={grammar} />

    {/* STATES + TABLE */}
    <div className="flex-container">
      <div className="box">
        <StatesView states={states} />
      </div>

      <div className="box">
        <ParsingTable
          action={action}
          gotoTable={gotoTable}
          conflicts={conflicts}
          parserType={parserType}
        />
      </div>
    </div>

    {/* INPUT */}
    <div style={{ marginTop: "30px", textAlign: "center" }}>
      <h2>Parse Input</h2>
      <input
        value={inputString}
        onChange={(e) => setInputString(e.target.value)}
        placeholder="id = id"
      />
      <button onClick={handleParseInput} style={{ marginLeft: "10px" }}>
        Parse
      </button>
    </div>

    {/* STEPS */}
    {parseSteps.length > 0 && (
      <div className="card">
        <h3 className="section-title">Parsing Steps</h3>
        <div className="table-container">
          <table>
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
        </div>
      </div>
    )}

    {parseResult && (
      <div style={{ textAlign: "center", marginTop: "10px" }}>
        Result: {parseResult}
      </div>
    )}
  </div>
);
 
}

export default App;
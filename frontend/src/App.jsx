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
  const [parserType, setParserType] = useState("lr0"); 
  const [validationMsg, setValidationMsg] = useState({ text: "", type: "" });

  const handleValidate = async () => {
    try {
      const res = await fetch(`${BASE_URL}/validate-grammar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ grammar }),
      });
      const data = await res.json();
      if (data.valid) {
        setValidationMsg({ text: "✅ Grammar is valid!", type: "success" });
      } else {
        setValidationMsg({ text: `❌ Error: ${data.error}`, type: "error" });
      }
    } catch (err) {
      setValidationMsg({ text: "❌ Connection to backend failed", type: "error" });
    }
  };

  const handleParseGrammar = async () => {
    try {
      // Clear previous states
      setParseSteps([]);
      setParseResult("");
      
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
    <div className="app-shell">
      <div className="app-container">
        <header className="app-header">
          <h1 className="title">Bottom-Up Parser Visualizer</h1>
          <p className="subtitle">
            Explore LR(0), SLR(1), CLR(1), and LALR(1) states and parsing logic.
          </p>
        </header>

        <section className="card control-panel">
          <div className="panel-header">
            <h2 className="section-title">Grammar Workspace</h2>
            <div className="parser-toggle">
              {["lr0", "slr1", "clr1", "lalr1"].map((type) => (
                <button
                  key={type}
                  onClick={() => setParserType(type)}
                  className={parserType === type ? "active-btn" : ""}
                >
                  {type.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <textarea
            rows={7}
            value={grammar}
            onChange={(e) => {
              setGrammar(e.target.value);
              setValidationMsg({ text: "", type: "" });
            }}
            placeholder={`Enter grammar...`}
          />

          {validationMsg.text && (
            <div className={`validation-banner ${validationMsg.type}`}>
              {validationMsg.text}
            </div>
          )}

          <div className="action-row">
            <button className="secondary-btn" onClick={handleValidate}>
              Validate Grammar
            </button>
            <button className="primary-btn" onClick={handleParseGrammar}>
              Generate Tables
            </button>
          </div>
        </section>

        <GrammarDisplay grammar={grammar} />

        <section className="flex-container">
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
        </section>

        {/* Parsing logic for input string remains same */}
        <section className="card parse-input-card">
          <h2 className="section-title">Parse Input String</h2>
          <div className="input-row">
            <input
              value={inputString}
              onChange={(e) => setInputString(e.target.value)}
              placeholder="id = id"
            />
            <button className="primary-btn" onClick={handleParseInput}>
              Parse
            </button>
          </div>
        </section>

        {/* STEPS TABLE */}
        {parseSteps.length > 0 && (
          <div className="card">
            <h3 className="section-title">Parsing Steps ({parserType.toUpperCase()})</h3>
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
          <div className="result-banner">
            <span>Result:</span> {parseResult}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
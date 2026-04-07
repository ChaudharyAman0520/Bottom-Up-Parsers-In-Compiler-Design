function ParsingTable({ action, gotoTable, conflicts = [], parserType }) {
  if (!action || Object.keys(action).length === 0) return null;

  const states = Object.keys(action);

  const terminals = new Set();
  states.forEach((s) => {
    Object.keys(action[s]).forEach((t) => terminals.add(t));
  });

  const nonTerminals = new Set();
  Object.keys(gotoTable).forEach((s) => {
    Object.keys(gotoTable[s]).forEach((nt) => nonTerminals.add(nt));
  });

  return (
    <div className="card">
      <h2 className="section-title">
        ⚙️ {parserType.toUpperCase()} Parsing Table
      </h2>

      <div className="table-container">
        <table className="styled-table">
          <thead>
            <tr>
              <th rowSpan="2">State</th>
              <th colSpan={terminals.size}>ACTION</th>
              <th colSpan={nonTerminals.size}>GOTO</th>
            </tr>
            <tr>
              {[...terminals].map((t) => (
                <th key={t}>{t}</th>
              ))}
              {[...nonTerminals].map((nt) => (
                <th key={nt}>{nt}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {states.map((state) => (
              <tr key={state}>
                <td className="state-cell">I{state}</td>

                {[...terminals].map((t) => {
                  const value = action[state][t] || "";
                  const isConflict = conflicts.some(
                    (c) => c.state == state && c.symbol === t
                  );

                  return (
                    <td
                      key={t}
                      className={isConflict ? "conflict-cell" : ""}
                    >
                      {value}
                    </td>
                  );
                })}

                {[...nonTerminals].map((nt) => (
                  <td key={nt}>{gotoTable[state][nt] ?? ""}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="conflict-box">
        <strong>⚠ Conflicts:</strong>
        {conflicts.length > 0 ? (
          conflicts.map((c, idx) => (
            <div key={idx}>
              State {c.state}, '{c.symbol}' → {c.existing} vs {c.incoming}
            </div>
          ))
        ) : (
          <span className="no-conflict"> None</span>
        )}
      </div>
    </div>
  );
}

export default ParsingTable;
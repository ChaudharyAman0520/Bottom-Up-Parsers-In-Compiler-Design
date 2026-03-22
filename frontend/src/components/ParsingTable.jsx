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
    <div style={{ marginTop: "20px" }}>
      <h2>{parserType.toUpperCase()} Parsing Table</h2>

      <table border="1" cellPadding="5" style={{ margin: "0 auto" }}>
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
              <td>{state}</td>
              {[...terminals].map((t) => (
                <td key={t}>{action[state][t] || ""}</td>
              ))}
              {[...nonTerminals].map((nt) => (
                <td key={nt}>{gotoTable[state][nt] ?? ""}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: "10px", textAlign: "center" }}>
        <strong>Conflicts:</strong>{" "}
        {conflicts.length > 0
          ? conflicts.map((c, idx) => (
              <div key={idx}>
                State {c.state}, Symbol '{c.symbol}': {c.existing} vs {c.incoming}
              </div>
            ))
          : "None"}
      </div>
    </div>
  );
}

export default ParsingTable;
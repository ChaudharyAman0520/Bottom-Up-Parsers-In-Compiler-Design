function GrammarDisplay({ grammar }) {
  if (!grammar) return null;

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Grammar</h3>

      {grammar.split("\n").map((line, i) => (
        <div key={i}>{line}</div>
      ))}
    </div>
  );
}

export default GrammarDisplay;
function GrammarDisplay({ grammar }) {
  if (!grammar) return null;

  return (
    <div className="card">
      <h3 className="section-title">📘 Input Grammar</h3>

      <div className="grammar-box">
        {grammar.split("\n").map((line, i) => (
          <div key={i} className="grammar-line">
            {line}
          </div>
        ))}
      </div>
    </div>
  );
}

export default GrammarDisplay;
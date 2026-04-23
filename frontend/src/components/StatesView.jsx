function StatesView({ states }) {
  if (!states || states.length === 0) return null;

  return (
    <div className="card">
      <h2 className="section-title">📊 LR States</h2>

      <div className="states-grid">
        {states.map((state) => {
          if (!state || !state.items) return null;

          return (
            <div key={state.state} className="state-card">
              <h3>I{state.state}</h3>

              {state.items.map((item, idx) => {
                if (!item || !item.right) return null;

                return (
                  <div key={idx} className="state-item">
                    <span className="production">
                      {item.left} → {formatItem(item)}
                    </span>
                    
                    {/* SAFE LOOKAHEAD RENDERING */}
                    {item.lookahead && (
                      <span className="lookahead-tag">
                        {" [ "}
                        {Array.isArray(item.lookahead) 
                          ? item.lookahead.join(" / ") 
                          : item.lookahead}
                        {" ]"}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatItem(item) {
  const { right, dot } = item;
  let output = [...right];
  // Insert the dot at the correct position
  output.splice(dot, 0, "•");
  return output.join(" ");
}

export default StatesView;
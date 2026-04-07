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
                    {item.left} → {formatItem(item)}
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

  let output = [];

  for (let i = 0; i < right.length; i++) {
    if (i === dot) output.push("•");
    output.push(right[i]);
  }

  if (dot === right.length) output.push("•");

  return output.join(" ");
}

export default StatesView;
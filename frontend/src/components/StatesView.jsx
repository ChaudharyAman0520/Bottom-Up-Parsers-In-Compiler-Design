function StatesView({ states }) {
  if (!states || states.length === 0) return null;

  return (
    <div>
      <h2>LR(0) States</h2>

      {states.map((state) => {
        if (!state || !state.items) return null; // 🔥 safety

        return (
          <div
            key={state.state}
            style={{
              border: "1px solid red",
              margin: "10px",
              padding: "10px"
            }}
          >
            <h3>I{state.state}</h3>

            {state.items.map((item, idx) => {
              if (!item || !item.right) return null; // 🔥 safety

              return (
                <div key={idx}>
                  {item.left} → {formatItem(item)}
                </div>
              );
            })}
          </div>
        );
      })}
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
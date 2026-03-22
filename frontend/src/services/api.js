const BASE_URL = "http://localhost:8000";

export const fetchStates = async (grammar) => {
  const res = await fetch(`${BASE_URL}/lr0-states`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ grammar })
  });

  return res.json();
};
# Bottom-Up Parser Visualizer

A professional, fully-featured visualization tool for Bottom-Up Parsing in Compiler Design. It supports generating states, tables, and simulating parsing for **LR(0)**, **SLR(1)**, **CLR(1)**, and **LALR(1)** parsers.

## Features

- **Multi-Parser Support**: Supports generating canonical collections and parsing tables for all 4 major bottom-up parsers.
- **Robust Grammar Engine**: 
  - Supports multi-character non-terminals (e.g., `Expr`, `Term`).
  - Handles Epsilon (`ε` or `epsilon`) cleanly and accurately.
  - Automatically handles cyclic dependencies in FIRST and FOLLOW set generation.
- **Conflict Detection**: Accurately detects Shift-Reduce and Reduce-Reduce conflicts.
- **Step-by-Step Simulation**: Simulates the parsing of an input string and visualizes the stack, input tape, and action taken at each step.
- **Premium UI**: A sleek, dark-themed glassmorphism interface built with React.

## Project Structure

- `app/`: FastAPI backend containing the parsing algorithms (Python).
- `frontend/`: React & Vite frontend containing the user interface.

## Getting Started

### 1. Run the Backend (FastAPI)

1. Navigate to the project root directory.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend will be running at `http://localhost:8000`.

### 2. Run the Frontend (React / Vite)

1. Open a new terminal and navigate to the `frontend/` directory.
2. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:5173` (or the port specified by Vite).

## How to Use

1. Enter your context-free grammar in the **Grammar Workspace**.
   - Use `->` to separate LHS and RHS.
   - Use `|` for alternative productions.
   - Use space to separate symbols.
   - Use `ε` or `epsilon` for empty productions.
   - Example:
     ```
     E -> E + T | T
     T -> T * F | F
     F -> ( E ) | id
     ```
2. Click **Validate Grammar** to ensure there are no syntax errors.
3. Select your desired parser (LR0, SLR1, CLR1, LALR1) and click **Generate Tables**.
4. The LR states and parsing table will be displayed below.
5. In the **Parse Input String** section, enter a string (e.g., `id + id * id`) and click **Parse** to see the step-by-step reduction process.


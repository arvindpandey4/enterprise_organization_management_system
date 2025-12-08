# Snake & Ladder Application

This project is a simple, beginner-friendly Python Flask application that simulates the classic **Snake & Ladder** game. The application progressively implements all core use cases across seven versions (UC1–UC7). Each use case adds new game behavior while keeping the previous functionality intact.

The application does not use a database or advanced frameworks. Everything is intentionally built using basic Python, simple game logic, and minimal Flask features.

---

## 1. Project Overview

This project implements the Snake & Ladder game logic in multiple steps:

* **UC1:** Single-player game start at position 0
* **UC2:** Add die roll (1–6)
* **UC3:** Add movement options (No Play, Ladder, Snake)
* **UC4:** Add snake negative position handling
* **UC5:** Enforce exact finish rule (must land exactly on 100)
* **UC6:** Show full report of every dice roll
* **UC7:** Add two-player mode with alternated turns and shared game events

Each use case is implemented in its own Flask file (`app_uc1.py` … `app_uc7.py`).

---

## 2. How the Application Works

### **Single Player Mode**

The game starts at **position 0**. On each turn:

1. A **die** is rolled (1–6)
2. A **random option** is chosen:

   * No Play → player stays in the same position
   * Ladder → move forward by die value
   * Snake → move backward by die value
3. If snake reduces position below 0 → reset to **0**
4. Ladder overshoot beyond 100 → position does **not** change
5. Game ends only when the player reaches **exactly 100**
6. Every roll is recorded and displayed in simple print-style output

### **Two Player Mode**

Two players share the **same sequence of random events**:

* Player 1 plays odd-numbered rolls
* Player 2 plays even-numbered rolls
* Both use the same die results and options in the same order
* The first player to reach **100** wins the game

Every roll prints:

```
Total Dice Roll: <roll_number>
Player: <Player 1 / Player 2>
Position: <new_position>
```

---

## 3. Flask in This Project

Flask is a lightweight Python web framework that turns Python functions into web pages. Only the most basic parts of Flask are used here:

### **Flask()**

Creates the application instance:

```
app = Flask(__name__)
```

### **@app.route()**

Defines a URL path and connects it to a Python function.

* `/` → home page (select single or two player mode)
* `/play` → runs the game simulation and displays results

### **render_template() / render_template_string()**

Used to generate the HTML response. The result page prints lines in a terminal-like style.

There are **no databases**, **no APIs**, and **no advanced Flask extensions** used.

---

## 4. Running the Application

### Install dependencies

```
pip install flask
```

### Run any use-case file

```
python app_uc7.py
```

Then open:

```
http://127.0.0.1:5000/
```

---

## 5. File Structure

```
project/
│
├── app_uc1.py
├── app_uc2.py
├── app_uc3.py
├── app_uc4.py
├── app_uc5.py
├── app_uc6.py
├── app_uc7.py
└── README.md (this file)
```

Each file contains a complete, independent Flask application implementing one use case.

---




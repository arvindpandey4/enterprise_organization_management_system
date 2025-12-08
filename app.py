from flask import Flask, render_template_string, request
app = Flask(__name__)

INDEX = """
<!doctype html><title>UC1 - Snake & Ladder</title>
<h1>UC1 - Single Player start</h1>
<p>Player starts at position 0</p>
<form method="post" action="/play">
  <button type="submit">Show start position</button>
</form>
"""

RESULT = """
<!doctype html><title>UC1 Result</title>
<pre>
Total Dice Roll: 0
Player: Player 1
Position: 0
</pre>
<p><a href="/">Back</a></p>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX)

@app.route("/play", methods=["POST"])
def play():
    return render_template_string(RESULT)

if __name__ == "__main__":
    app.run(debug=True)

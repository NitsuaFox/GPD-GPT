import os
from datetime import timedelta

import openai
from flask import Flask, redirect, render_template, request, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.permanent_session_lifetime = timedelta(days=30)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        product_description = request.form["product_description"]
        writing_style = request.form["writing_style"]
        additional_info = request.form.getlist("additional_info")

        # Store user input history in the session
        if "history" not in session:
            session["history"] = []

        session["history"].append({"product_description": product_description, "writing_style": writing_style, "additional_info": additional_info})
        session.modified = True

        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Etsy product titles, descriptions, and tags."},
            {"role": "user", "content": f"Generate an Etsy product title, description with writing style '{writing_style}', and tags (separated by commas) for the following product: {product_description}. Please provide the result in the format: TITLE: ... | DESCRIPTION: ... | TAGS: ..."}
        ]

        for info in additional_info:
            messages.append({"role": "user", "content": f"The product also has the following feature: {info}"})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.6,
        )
        result_text = response.choices[0].message["content"]
        title, description, tags = [x.strip() for x in result_text.split("|")]

        # Remove prefixes
        title = title.replace("TITLE:", "").strip()
        description = description.replace("DESCRIPTION:", "").strip()
        tags = tags.replace("TAGS:", "").strip()

        return redirect(url_for("index", title=title, description=description, tags=tags))

    title = request.args.get("title")
    description = request.args.get("description")
    tags = request.args.get("tags")
    return render_template("index.html", title=title, description=description, tags=tags, history=session.get("history", []))

if __name__ == "__main__":
    app.run(debug=True)
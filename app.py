import os
from datetime import timedelta

import openai
from flask import Flask, redirect, render_template, request, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.permanent_session_lifetime = timedelta(days=30)
openai.api_key = "ENTER KEY HERE"
@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        product_description = request.form["product_description"]
        writing_style = request.form["writing_style"]
        additional_info = request.form.getlist("additional_info")
        marketplace_style = request.form["marketplace_style"]


        # Store user input history in the session
        if "history" not in session:
            session["history"] = []

        session["history"].append({
            "product_description": product_description, 
            "writing_style": writing_style, 
            "additional_info": additional_info, 
            "marketplace_style": marketplace_style
        })
        session.modified = True

        messages = [
            {"role": "system", "content": "You are a very factual, verbose and helpful sales assistant that generates product titles, descriptions, bullet points and tags in the following format: TITLE: ... | DESCRIPTION: ... | BULLETS: ... | TAGS: ..."},
            {"role": "user", "content": f"Please be '{writing_style}' and generate the product title, description and five bullet points (prefixed by emoji and separated by returns) and tags (separated by commas) for the following product: {product_description}."}
        ]

        for info in additional_info:
            messages.append({"role": "user", "content": f"Additional Info: The product also has the following feature(s): {info}"})

        # Add the marketplace_style to the messages
        messages.append({"role": "user", "content": f"Additional Info: The product is intended for the {marketplace_style}."})

        # Conditionally include HTML markup instruction for Amazon Marketplace
        if marketplace_style == "Amazon Marketplace":
            messages.append({"role": "user", "content": "Please include HTML markup ONLY in the description for proper formatting on Amazon Marketplace."})


        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.5,
        )
        result_text = response.choices[0].message["content"]
        title, description, bullets, tags = [x.strip() for x in result_text.split("|")]


        # Remove prefixes
        title = title.replace("TITLE:", "").strip()
        description = description.replace("DESCRIPTION:", "").strip()
        bullets = bullets.replace("BULLETS:", "").replace("\n", "<br>").strip()
        tags = tags.replace("TAGS:", "").strip()

        return redirect(url_for("index", title=title, description=description, tags=tags, bullets=bullets))


    title = request.args.get("title")
    description = request.args.get("description")
    bullets = request.args.get("bullets", "")
    tags = request.args.get("tags")
    return render_template("index.html", title=title, description=description, tags=tags, bullets=bullets, history=session.get("history", []))


if __name__ == "__main__":
    app.run(debug=True)
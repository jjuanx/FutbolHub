from flask import render_template

from app.features.resultsfile import resultsfile_bp


@resultsfile_bp.route("/resultsfile", methods=["GET"])
def index():
    return render_template("resultsfile/index.html")

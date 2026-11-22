from flask import jsonify, render_template, request

from app.features.explore import explore_bp
from app.features.explore.forms import ExploreForm
from app.features.explore.services import ExploreService

explore_service = ExploreService()

FILTER_KEYS = (
    "query",
    "publication_type",
    "sorting",
    "tags",
    "author",
    "date_from",
    "date_to",
    "competition",
    "season",
    "country",
    "team",
    "min_matches",
    "max_matches",
    "min_teams",
    "max_teams",
)


def _extract_url_filters(args) -> dict:
    """Extrae los parámetros de filtrado presentes en la query string de la URL."""
    extracted = {}
    for key in FILTER_KEYS:
        if key == "tags":
            tag_list = args.getlist("tags")
            if len(tag_list) > 1:
                extracted["tags"] = ", ".join(t.strip() for t in tag_list if t.strip())
            elif len(tag_list) == 1:
                extracted["tags"] = tag_list[0].strip()
            else:
                extracted["tags"] = ""
        elif key == "publication_type":
            extracted[key] = args.get(key, "any")
        elif key == "sorting":
            extracted[key] = args.get(key, "newest")
        else:
            extracted[key] = args.get(key, "")
    return extracted


@explore_bp.route("/explore", methods=["GET"])
def index():
    url_filters = _extract_url_filters(request.args)
    if request.args.get("format") == "json" or (
        request.accept_mimetypes.best == "application/json" and not request.accept_mimetypes.accept_html
    ):
        datasets = explore_service.filter(**url_filters)
        return jsonify([dataset.to_dict() for dataset in datasets])

    return render_template(
        "explore/index.html",
        form=ExploreForm(),
        query=url_filters["query"],
        url_filters=url_filters,
    )


@explore_bp.route("/explore", methods=["POST"])
def search():
    payload = {}
    if request.args:
        for key in FILTER_KEYS:
            if key in request.args:
                if key == "tags" and len(request.args.getlist("tags")) > 1:
                    payload["tags"] = request.args.getlist("tags")
                else:
                    payload[key] = request.args.get(key)
    payload.update(request.get_json(silent=True) or {})
    datasets = explore_service.filter(**payload)
    return jsonify([dataset.to_dict() for dataset in datasets])

from app import db


class ResultsFile(db.Model):
    """A results CSV file of a football dataset. It replaces ``FeatureModel`` in the football type.

    Unlike a feature model, it has no metadata of its own: the metadata belongs to the dataset
    (option C of #15). It only keeps what is specific to the file, and its ``Hubfile`` holds the
    name, checksum and size.
    """

    __tablename__ = "results_file"

    id = db.Column(db.Integer, primary_key=True)
    data_set_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), nullable=False)
    number_of_matches = db.Column(db.Integer)
    files = db.relationship("Hubfile", backref="results_file", lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"ResultsFile<{self.id}>"

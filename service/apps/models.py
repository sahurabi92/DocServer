from datetime import datetime
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api

db = SQLAlchemy()
ma = Marshmallow()
api = Api(title='Document Server',
          version='1.0',
          description='Document Server')


class DocLib(db.Model):
    __tablename__ = "doclib"

    doc_id = db.Column(db.Integer, primary_key=True)
    doc_name = db.Column(db.String(20), nullable=False)
    doc_file_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    uploaded_time = db.Column(db.DateTime(), nullable=True, index=True)
    updated_time = db.Column(db.DateTime(), nullable=False, index=True, default=datetime.now())
    doc_owner = db.Column(db.String(20), nullable=False)
    collaborator = db.Column(db.String(100), nullable=True)
    edit_enabled_by = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"<Song {self.doc_owner}>"


"""Marshmallow Schemas for Serializing the DB datas"""


class __DocLib(ma.Schema):
    class Meta:
        fields = ['doc_id', 'doc_owner', 'collaborator', 'uploaded_time', 'updated_time']
        model = DocLib


class __Doc__Lib(ma.Schema):
    class Meta:
        fields = ['doc_id', 'doc_file_name', 'uploaded_time', 'updated_time', 'doc_owner', 'doc_name']
        model = DocLib


Doc_Lib_Schema = __DocLib()
Docs_Lib_Schema = __DocLib(many=True)
Save_doc_Schema = __Doc__Lib()

from .utils import upload_parser, update_docs, validation, FieldConstant, ErrorCode
from flask import request, send_from_directory, make_response
from .models import DocLib, Save_doc_Schema, Docs_Lib_Schema
from werkzeug.utils import secure_filename
from flask_restplus import Resource
from datetime import datetime as dt
from . import app, db, api
import logging
import time
import os

log = logging.getLogger("default")

"""Handling all the Operation in this file"""


class HandleFiles(Resource):
    """This Class is for Uploading the file"""

    @api.response(200, 'Success')
    @api.response(400, 'Bad Request')
    @api.expect(upload_parser())
    def post(self):
        """ Post Method to Upload the file"""
        try:
            file = request.files['File']
            user_name = request.form['username']
            doc_name = request.form['doc_name']
            if not validation.allowed_file(file.filename):
                return make_response(ErrorCode.invalid_file_type)
            file_name = secure_filename(str(time.time())[:-3] + file.filename)
            data = DocLib(
                doc_file_name=file_name,
                status=0,
                doc_name=doc_name,
                doc_owner=user_name,
                uploaded_time=dt.now()
            )
            db.session.add(data)
            db.session.commit()
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file_name))
            log.info(f"{user_name}-Uploaded the document")
            return Save_doc_Schema.dump(data)
        except Exception:
            log.error(f"Upload Failed", exc_info=True)
            return make_response({"msg": "Bad Request"}, 400)

    @api.doc("Get All Data")
    def get(self):
        """It will all the data present in DB in serialize way"""
        data = DocLib.query.order_by(DocLib.doc_id).all()
        log.info("Queried All the data from the DB")
        return Docs_Lib_Schema.dump(data)


class EditDoc(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Validation Error')
    @api.expect(update_docs())
    def put(self, doc_id):
        """Updating the doc with all the checks to prevent con-current edits"""
        try:
            file = request.files['file']
            user_name = request.form['editor_name']
            obj = DocLib.query.filter_by(doc_id=doc_id)
            data = obj.one()
            if not data:
                return make_response("Data Not Found", 404)
            if not validation.allowed_file(file.filename):
                return make_response(ErrorCode.invalid_file_type)
            if data.status != 3:
                return make_response(ErrorCode.edit_mode_enable)
            if data.edit_enabled_by != user_name:
                return make_response(ErrorCode.user_rights)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], data.doc_file_name))
            file_name = secure_filename(str(time.time())[:-3] + file.filename)
            obj.update(dict(status=0,
                            doc_file_name=file_name,
                            edit_enabled_by=user_name
                            ))
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file_name))
            db.session.commit()
            log.info(f"{user_name} - Updated the Doc")
            return make_response("File Edited Successfully", 201)
        except FileNotFoundError:
            return make_response("File Not Found", 404)
        except Exception:

            log.error(f"Error Occurred while updating the Doc")
            return make_response({"msg": "Error in Edit of the Doc"}, 400)


class DownLoadFile(Resource):
    """ Download of file with checking the user details"""

    @api.response(200, 'Success')
    @api.response(403, 'Permission Error')
    @api.doc(parameter={'doc_id': 'ID of the Doc to download ', 'username': "Provide the username to download"})
    def get(self, doc_id, username):
        """Download The Document"""
        data = DocLib.query.get_or_404(doc_id)
        if not validation.user_permission(username, data):
            return make_response(ErrorCode.user_rights)
        if validation.owner_share_permission(data, username):
            return make_response(ErrorCode.permission_error)
        log.info(f"{username} - Download Done")
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=data.doc_file_name)


class EditFlag(Resource):
    @api.response(200, 'Success')
    @api.expect(FieldConstant.edit_flag_fields)
    def post(self):
        """Enable Edit mode Before updating the Document"""
        try:
            doc_id = request.json['doc_id']
            user_name = request.json['username']
            data = DocLib.query.get_or_404(doc_id)
            if not validation.user_permission(user_name, data):
                return make_response(ErrorCode.user_rights)
            if validation.owner_share_permission(data, user_name):
                return make_response(ErrorCode.permission_error)
            elif (data.status == 3 and user_name is data.doc_owner) or data.status != 3:
                DocLib.query.filter_by(doc_id=doc_id).update(dict(status=3, edit_enabled_by=user_name))
                db.session.commit()
            log.info(f"{user_name} - Enabled The Edit Mode")
            return make_response({"msg": "Edit Mode Enabled"}, 200)
        except Exception:
            log.error("Error While Enabling the Edit Mode")
            return make_response({"msg": "Error Occurred"}, 400)


class DeleteDocs(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Not Found')
    @api.doc(parameter={'doc_id': 'ID of the Doc to Delete ', "username": "User Name of download user"})
    def delete(self, doc_id, username):
        """ Delete The Doc Record from both DB and file path"""
        try:
            obj = DocLib.query.get_or_404(doc_id)
            if not validation.user_permission(username, obj):
                return make_response(ErrorCode.user_rights)
            if validation.owner_share_permission(obj, username):
                return make_response(ErrorCode.permission_error)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], obj.doc_file_name))
            db.session.delete(obj)
            db.session.commit()
            log.info(f"{username} - Deleted The Doc")
            return f"Delete Done for {obj.doc_file_name}", 200
        except FileNotFoundError:
            log.error(f"File Not Found on Server path")
            return make_response(ErrorCode.not_found)
        except Exception:
            log.error(f"Delete Operation Failed")
            return {"msg": "Data Not found"}, 400


class AddCollaborator(Resource):

    @api.response(201, 'Added')
    @api.expect(FieldConstant.Collaborate_fields)
    def patch(self, doc_id):
        """Add the Collaborator to the in the Existing Doc to read and update the document"""
        try:
            members = request.json['members']
            user = request.json['doc_owner']
            data = DocLib.query.get_or_404(doc_id)
            if data.doc_owner != user:
                return make_response({"msg": "Entered User is not a the Doc Owner"}, 401)
            DocLib.query.filter_by(doc_id=doc_id).update(dict(collaborator=str(members)))
            db.session.commit()
            log.info(f"All the Members are added as Collaborator(s) {members}")
            return f"Members are added for the doc_id: {doc_id}", 201

        except Exception:
            log.error(f"Error while adding of Collaborator(s)")
            return make_response({"msg": "Failed to add members"}, 400)

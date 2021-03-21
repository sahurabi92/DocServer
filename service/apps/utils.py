from flask_restplus import fields
from . import api, app
import werkzeug
import ast

"""Creating the Form Data Parser methods for swagger Doc to upload files"""


class FieldConstant:
    edit_flag_fields = api.model('Enable edit Mode', {
        'username': fields.String, 'doc_id': fields.Integer})
    Collaborate_fields = api.model('Add Collaborator', {
        'members': fields.List(fields.String),'doc_owner': fields.String, })


class ErrorCode:
    permission_error = {'msg': "Can't delete/Edit the Doc when Edit Mode is enabled by the Doc Owner"}, 401
    user_rights = {'msg': "The user Does not have the permission to do this operation"}, 401
    not_found = {"msg": "Not Found Error"}, 404
    invalid_file_type = {"msg": "File Type is Invalid"}, 422
    edit_mode_enable = {"msg": "Edit Mode is Not Enabled , Enable First"}, 403


def upload_parser():
    upload_file = api.parser()

    upload_file.add_argument('File', type=werkzeug.datastructures.FileStorage,
                             location='files', help='Select Doc to Upload, Support format {.txt, .xlsx }')
    upload_file.add_argument('username', location='form', type='string', help='Enter the Doc Owner Name')
    upload_file.add_argument('doc_name', location='form', type='string', help='Enter the Doc to Name')
    return upload_file


def update_docs():
    update_file = api.parser()

    update_file.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files',
                             help='Upload Doc to Edit')
    update_file.add_argument('editor_name', location='form', type='string', help='Enter the Doc editorName Name')
    return update_file


class validation:

    @classmethod
    def allowed_file(cls, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    @classmethod
    def user_permission(cls, username, obj):
        m_data = ast.literal_eval(obj.collaborator.lower() if obj.collaborator is not None else '[]')

        m_data.append(obj.doc_owner.lower())
        return username in m_data

    @classmethod
    def owner_share_permission(cls, obj, username):
        return obj.status == 3 and username.lower() != obj.doc_owner.lower()

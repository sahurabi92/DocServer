
def init_api(api):
    from .view import HandleFiles, DownLoadFile, DeleteDocs, AddCollaborator, EditFlag, EditDoc
    api.add_resource(HandleFiles,
                     '/api/docserver/doc/'
                     )
    api.add_resource(EditDoc,
                     '/api/docserver/doc/<int:doc_id>',
                     )
    api.add_resource(DownLoadFile,
                     '/api/docserver/download/<int:doc_id>/<string:username>',
                     )
    api.add_resource(DeleteDocs,
                     '/api/docserver/delete/<int:doc_id>/<string:username>',
                     )
    api.add_resource(AddCollaborator,
                     '/api/docserver/addusers/<int:doc_id>',
                     )
    api.add_resource(EditFlag,
                     '/api/docserver/editmode', )

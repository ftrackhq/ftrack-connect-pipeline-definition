# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import unreal as ue

try:
    from ftrack_connect_pipeline_unreal_engine import plugin
    
    import ftrack_api


    class FBXUnrealImportPlugin(plugin.LoaderImporterUnrealPlugin):
        plugin_name = 'fbx_unreal_import'

        def run(self, context=None, data=None, options=None):
            # ensure to load the alembic plugin

            results = {}
            paths_to_import = data
            for component_path in paths_to_import:
                self.logger.debug('Importing path {}'.format(component_path))

                task = ue.AssetImportTask()
                task.options = ue.FbxImportUI()
                task.options.import_mesh = True #iAObj.options['ImportMesh']
                task.options.import_materials = True #iAObj.options['ImportMaterial']
                task.options.import_animations = False

                fbx_path = component_path
                import_path = '/Game/' + "FtrackImportFolder"#iAObj.options['ImportFolder']

                task.filename = fbx_path
                task.destination_path = import_path
                task.replace_existing = True
                task.automated = True
                # save the file when it is imported, that's right!
                task.save = True

                imported_asset = ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
                    [task]
                )

                if imported_asset:
                    self.name_import = (
                        import_path
                        + '/'
                        + imported_asset.asset_name
                        + '.'
                        + imported_asset.asset_name
                    )
                    importedAssetNames = [str(imported_asset.asset_name)]
                else:
                    importedAssetNames = []

                #try:
                #    self.addMetaData(iAObj, imported_asset)
                #except Exception as error:
                #    self.logger.error(error)

                #return importedAssetNames

                results[component_path] = importedAssetNames

            return results


    def register(api_object, **kw):
        if not isinstance(api_object, ftrack_api.Session):
            # Exit to avoid registering this plugin again.
            return
        print('@@@ fbx_unreal_import::register')
        plugin = FBXUnrealImportPlugin(api_object)
        plugin.register()

except:
    import traceback
    print(traceback.format_exc())
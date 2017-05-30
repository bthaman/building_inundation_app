"""
Application to get the maximum water surface elevation and depth around building features.
Water surface and depth from infoworks output
"""
try:
    # python 2
    import Tkinter as tk
    import ttk
except ImportError:
    # python 3
    import tkinter as tk
    from tkinter import ttk
import basic_combo_dialog_v2
import msgbox
import file_dir_dialog as fdd
try:
    import arcpy
    from arcpy import env
except Exception as e:
    msgbox.show_error('arcpy error', 'Error importing arcpy: ' + str(e))
from os.path import join


class App(basic_combo_dialog_v2.BasicComboGUI):
    # inherits from BasicComboGUI
    def __init__(self, title="Get WSEL and depth around buildings", date_picker=False):
        basic_combo_dialog_v2.BasicComboGUI.__init__(self, frame_title=title, date_picker=date_picker)
        self.building_workspace = None
        self.building_fc = None
        self.building_buffer_fc = None
        self.triangle_workspace = None
        self.triangles_all_storms = None
        self.lst_fc_buildingws = []
        self.lst_fc_trianglews = []
        self.lst_fc_triangle_path = []
        self.dict_triangle_fc = {}
        self.dict_building_fc = {}
        if self.date_picker:
            pass

    def envclick(self):
        """ Click event for 'Get Building Workspace' button """
        # if the buildings are in a file gdb, this code needs to change to accommodate that
        self.building_workspace = fdd.get_directory(title='Select workspace')
        if not self.building_workspace:
            return
        env.workspace = self.building_workspace
        self.lst_fc_buildingws = arcpy.ListFeatureClasses()
        self.dict_building_fc = {fc: join(self.building_workspace, fc) for fc in self.lst_fc_buildingws}
        self.lst_fc_buildingws.sort()
        self.combo_box['values'] = self.lst_fc_buildingws
        self.combo_box.current(0)

    def envclick2(self):
        """ Click event for 'Get Triangle Workspace' button. 
        Gets feature classes from a folder or file gdb workspace, and adds to tkinter listbox """
        self.triangle_workspace = fdd.get_directory(title='Select workspace')
        if not self.triangle_workspace:
            return
        self.lst_fc_trianglews = []
        env.workspace = self.triangle_workspace
        # check if file geodatabase
        if '.' in self.triangle_workspace and self.triangle_workspace.rsplit('.')[-1] == 'gdb':
            datasets = arcpy.ListDatasets('*', 'Feature')
            datasets = [''] + datasets if datasets is not None else []
            for ds in datasets:
                for fc in arcpy.ListFeatureClasses('*', '', ds):
                    self.lst_fc_trianglews.append(fc)
                    path = join(self.triangle_workspace, ds, fc)
                    self.lst_fc_triangle_path.append(path)
            self.dict_triangle_fc = dict(zip(self.lst_fc_trianglews, self.lst_fc_triangle_path))
        else:
            self.lst_fc_trianglews = arcpy.ListFeatureClasses()
            self.dict_triangle_fc = {fc: join(self.triangle_workspace, fc) for fc in self.lst_fc_trianglews}
        self.lst_fc_trianglews.sort()
        self.lstbox.delete(0, tk.END)
        for item in self.lst_fc_trianglews:
            self.lstbox.insert(tk.END, item)

    def okclick(self):
        """ Click event for 'OK' button """
        # overrides click event in parent class
        self.building_fc = self.entered_value.get()
        self.building_buffer_fc = self.building_fc.split('.')[0] + '_buffer.shp' if '.shp' in self.building_fc \
            else self.building_fc + '_buff'
        lstboxselection = self.lstbox.curselection()
        self.triangles_all_storms = list(self.lst_fc_trianglews[i] for i in lstboxselection)

        # for placeholder checkbox
        if self.chk_val.get():
            pass

        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = self.building_workspace

        # buffer buildings by 2 feet
        try:
            building_buffer_distance = "2 Feet"
            building_features = self.dict_building_fc[self.building_fc]
            buff_features = 'in_memory/buff_features'
            arcpy.Buffer_analysis(building_features, buff_features,
                                  building_buffer_distance, "FULL", "ROUND", "NONE", "", "PLANAR")
        except Exception as e:
            msgbox.show_error('Buffer Error', str(e))
            return
        # do geoprocessing for all storms
        for n, triangle in enumerate(self.triangles_all_storms):
            triangle_fc = self.dict_triangle_fc[triangle]
            print('Executing: ' + triangle_fc)
            # repair geometry, because you have to
            try:
                arcpy.RepairGeometry_management(triangle_fc, 'DELETE_NULL')
            except Exception as e:
                msgbox.show_error('RepairGeometry error', str(e))
                return
            # union buildings and triangles
            try:
                in_features = list((buff_features, triangle_fc))
                # write union features to disk: in-memory fc threw exception
                union_features = join(self.building_workspace, 'bldg_triangle_union.shp')
                # union_features = 'in_memory/bldg_triangle_union'
                arcpy.Union_analysis(in_features, union_features, 'ALL', "", 'NO_GAPS')
            except Exception as e:
                msgbox.show_error('Union error', str(e))
                return
            finally:
                pass
            # dissolve (get max WSEL ans max depth for each building)
            try:
                dissolve_fields = ['poly_id']
                stat_fields = [['DEPTH2D', 'MAX'], ['elevation2', 'MAX']]
                dissolve_features = join(self.building_workspace, 'temp_dissolveelev.shp')
                # dissolve_features = 'in_memory/dissolveelev'
                arcpy.Dissolve_management(union_features, dissolve_features, dissolve_fields, stat_fields,
                                          'MULTI_PART', 'DISSOLVE_LINES')
            except Exception as e:
                msgbox.show_error('Dissolve error', str(e))
                return
            finally:
                arcpy.Delete_management(union_features)
            # join max WSEL and max depth to buildings
            try:
                building_id_field = 'poly_id'
                included_fields = ['MAX_DEPTH2', 'MAX_elevat']
                arcpy.JoinField_management(building_features, building_id_field,
                                           dissolve_features, building_id_field, included_fields)
            except Exception as e:
                msgbox.show_error('JoinField error', str(e))
                return
            finally:
                arcpy.Delete_management(dissolve_features)
            # add WSELn and Depth2Dn fields.
            try:
                arcpy.AddField_management(building_features, 'WSEL_' + str(n), 'FLOAT', "", "", "", "",
                                          "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(building_features, 'Depth2D_' + str(n), 'FLOAT', "", "", "", "",
                                          "NULLABLE", "NON_REQUIRED", "")
            except Exception as e:
                msgbox.show_error('Add field error', str(e))
                return
            finally:
                pass
            # calculate WSELn and Depth2Dn fields
            try:
                expression = '!MAX_elevat!'
                arcpy.CalculateField_management(building_features, 'WSEL_' + str(n), expression, 'PYTHON', "")
                arcpy.DeleteField_management(building_features, 'MAX_elevat')

                expression = '!MAX_DEPTH2!'
                arcpy.CalculateField_management(building_features, 'Depth2D_' + str(n), expression, 'PYTHON', "")
                arcpy.DeleteField_management(building_features, 'MAX_DEPTH2')
            except Exception as e:
                msgbox.show_error('Calculate field error', str(e))
                return
            finally:
                pass

        # delete in_memory building buffer and display message
        arcpy.Delete_management(buff_features)
        msgbox.show_message('Message', 'Completed successfully.')

    def handle_event(self, *args):
        """ event to enable/disable 'OK' button """
        x = self.entered_value.get()
        y = self.lstbox.curselection()

        if x and y:
            self.btn_ok.configure(state='normal')
        else:
            self.btn_ok.configure(state='disabled')

    def combo_box_select_event(self, *args):
        """ select event for combo box - originally did something other than call another even, 
        but deleted logic and left it in case i want to use it for something else """
        self.handle_event()

if __name__ == "__main__":
    app = App(date_picker=False)
    app.show_window()

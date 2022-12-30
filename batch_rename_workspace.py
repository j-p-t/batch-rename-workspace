import arcpy
import time
import re


class BatchRenameWorkspaceException(Exception):
    error_msg = ""

    def __init__(self, error_msg, *args):
        super().__init__(args)
        self.error_msg = error_msg

    def __str__(self):
        return 'Exception: ' + self.error_msg


def count_booleans(lst):
	return sum(bool(x) for x in lst)


if __name__ == '__main__':
    ws = arcpy.GetParameterAsText(0)
    is_ds = arcpy.GetParameter(1)
    is_fc = arcpy.GetParameter(2)
    is_fname = arcpy.GetParameter(3)
    reg = arcpy.GetParameter(4)
    is_lowercase = arcpy.GetParameter(5)
    is_title = arcpy.GetParameter(6)
    is_uppercase = arcpy.GetParameter(7)
    repl = arcpy.GetParameterAsText(8)
    repl_with = arcpy.GetParameterAsText(9)
    remove_first_n = arcpy.GetParameterAsText(10)
    remove_last_n = arcpy.GetParameterAsText(11)
    add_prefix = arcpy.GetParameterAsText(12)
    add_suffix = arcpy.GetParameterAsText(13)

    if count_booleans([is_ds, is_fc, is_fname]) == 0:
        err_msg = "Error - no dataset type selected"
        arcpy.AddError(err_msg)
        raise BatchRenameWorkspaceException(err_msg)

    if count_booleans([is_lowercase, is_title, is_uppercase]) > 1:
        err_msg = "Error - select either lowercase, title case, uppercase or none"
        arcpy.AddError(err_msg)
        raise BatchRenameWorkspaceException(err_msg)

    if repl == "" and repl_with != "":
        err_msg = "Error - 'Replace' cannot be an empty string"
        arcpy.AddError(err_msg)
        raise BatchRenameWorkspaceException(err_msg)

    special_characters = " !@#$%^&*()-=+,./<>?[]{}\|`~"

    if (any((c in special_characters) for c in repl_with)) or (any((c in special_characters) for c in add_prefix)) or (any((c in special_characters) for c in add_suffix)):
        err_msg = "Error - feature class or feature dataset or field names cannot contain any empty spaces or special characters except an underscore"
        arcpy.AddError(err_msg)
        raise BatchRenameWorkspaceException(err_msg)

    if add_prefix[0].isnumeric() or add_prefix[0] == "_":
        err_msg = "Error - first character cannot be a number or an underscore"
        arcpy.AddError(err_msg)
        raise BatchRenameWorkspaceException(err_msg)

    arcpy.env.workspace = ws

    datasets = arcpy.ListDatasets(feature_type='all')
    datasets = [''] + datasets if datasets is not None else []

    try:
        for ds in datasets:
            oldnm = ds
            tmpnm = ds
            if is_ds and ds != "":
                if reg == "" or (reg != "" and re.search(r'{0}}'.format(reg), ds)):
                    if is_uppercase:
                        tmpnm = tmpnm.upper()
                    if is_lowercase:
                        tmpnm = tmpnm.lower()
                    if is_title:
                        tmpnm = tmpnm.title()
                    if repl != "":
                        tmpnm.replace(repl, repl_with)
                    if remove_first_n != "":
                        tmpnm = tmpnm[int(remove_first_n):]
                    if remove_last_n != "":
                        tmpnm = tmpnm[:int(remove_last_n)]
                    if add_prefix != "":
                        tmpnm = add_prefix + tmpnm
                    if add_suffix != "":
                        tmpnm = tmpnm + add_suffix
                    tmpnm = "tmp_" + tmpnm.strip()
                    arcpy.AddMessage("old feature dataset name: " + ds)
                    arcpy.AddMessage(oldnm)
                    arcpy.AddMessage(tmpnm)
                    arcpy.Rename_management(oldnm, tmpnm, "FeatureDataset")
                    arcpy.AddMessage("tmp dataset feature name: " + tmpnm)
                    arcpy.Rename_management(tmpnm, tmpnm[4:].strip(), "FeatureDataset")
                    arcpy.AddMessage("new feature dataset name: " + tmpnm[4:].strip())
            features = arcpy.ListFeatureClasses(feature_dataset=ds)
            for fc in features:
                if is_fname:
                    field_list = arcpy.ListFields(fc)
                    arcpy.AddMessage(field_list)
                    for f in field_list:
                        arcpy.AddMessage(f)
                        if f.editable and f.name not in ["OBJECTID", "FID", "Shape", "Shape_Length", "Shape_Area", "GLOBALID"]:
                            if reg == "" or (reg != "" and re.search(r'{0}}'.format(reg), f.name)):
                                arcpy.AddMessage("editing")
                                oldnm = f.name
                                tmpnm = f.name
                                if is_uppercase:
                                    tmpnm = tmpnm.upper()
                                if is_lowercase:
                                    tmpnm = tmpnm.lower()
                                if is_title:
                                    tmpnm = tmpnm.title()
                                if repl != "":
                                    tmpnm.replace(repl, repl_with)
                                if remove_first_n != "":
                                    tmpnm = tmpnm[int(remove_first_n):]
                                if remove_last_n != "":
                                    tmpnm = tmpnm[:int(remove_last_n)]
                                if add_prefix != "":
                                    tmpnm = add_prefix + tmpnm
                                if add_suffix != "":
                                    tmpnm = tmpnm + add_suffix
                                tmpnm = "tmp_" + tmpnm.strip()
                                arcpy.AlterField_management(fc, oldnm, tmpnm)
                                arcpy.AddMessage("tmp field name: " + tmpnm)
                                newnm = tmpnm[4:].strip()
                                new_alias = newnm
                                time.sleep(1)
                                arcpy.AlterField_management(fc, tmpnm, newnm, new_alias)
                                arcpy.AddMessage("new field name: " + newnm)
            if is_fc:
                if reg == "" or (reg != "" and re.search(r'{0}}'.format(reg), fc)):
                    oldnm = fc
                    tmpnm = fc
                    if is_uppercase:
                        tmpnm = tmpnm.upper()
                    if is_lowercase:
                        tmpnm = tmpnm.lower()
                    if is_title:
                        tmpnm = tmpnm.title()
                    if repl != "":
                        tmpnm.replace(repl, repl_with)
                    if remove_first_n != "":
                        tmpnm = tmpnm[int(remove_first_n):]
                    if remove_last_n != "":
                        tmpnm = tmpnm[:int(remove_last_n)]
                    if add_prefix != "":
                        tmpnm = add_prefix + tmpnm
                    if add_suffix != "":
                        tmpnm = tmpnm + add_suffix
                    tmpnm = "tmp_" + tmpnm.strip()
                    arcpy.AddMessage("old feature class name: " + fc)
                    arcpy.Rename_management(oldnm, tmpnm, "FeatureClass")
                    arcpy.AddMessage("tmp feature class name: " + tmpnm)
                    arcpy.Rename_management(tmpnm, tmpnm[4:].strip(), "FeatureClass")
                    arcpy.AddMessage("new feature class name: " + tmpnm[4:].strip())
    except Exception as e:
        arcpy.AddError(e)
        raise BatchRenameWorkspaceException(e)

import os
import polymorphic

target_module_dir = os.path.dirname(polymorphic.__file__)
target_file = target_module_dir + '/admin/childadmin.py'
patch_file = os.path.dirname(os.path.realpath(__file__)) + "/fix_scriptname_bug.patch"
os.system('patch %s %s' % (target_file, patch_file))

# Copyright (C) 2016, RMIT University

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import logging
from chiminey.smartconnectorscheduler import models
from chiminey.initialisation import CoreInitial
from django.conf import settings as django_settings
from  distutils.file_util  import copy_file
import sys
import os
import zipfile
import tarfile


logger = logging.getLogger(__name__)


class CharlieInitial(CoreInitial):
    def get_updated_parent_params(self):
        return {'package': "chiminey.charlieconnector.charlieparent.CharlieParent"}

    def get_updated_configure_params(self):
        print "\n\nPlease download CHARLIE from http://www-dssz.informatik.tu-cottbus.de/DSSZ/Software/Charlie#downloadCharlie" 
        print "\nRun the GUI installer at a directory of your choice"
        print "\nCreate charlie.tar.gz file with charlie.jar, tCharlie.sh and externalpackages directory"
        print "\nPlace the charlie.tar.gz file in ./package directory\n\n"
        
        MESSAGE = "Is charlie.tar.gz (already) available is ./package directory? [Yes/No]"
        confirm = raw_input(MESSAGE)
        if confirm != "Yes":
            print "action aborted by user"
            raise sys.exit()
        package_name = "charlie.tar.gz"
        package_path = "/var/chiminey/package/" + package_name
        if  not os.path.isfile(package_path):
            print "package does not exist : ./package/%s" %package_name
            print "exiting..." 
            raise sys.exit()
        elif os.path.getsize(package_path) <= 0 or not tarfile.is_tarfile(package_path):
            print "invalid package : ./package/%s" %package_name
            print "exiting..." 
            raise sys.exit()

        destination = os.path.join(django_settings.LOCAL_FILESYS_ROOT_PATH,
                                   django_settings.PAYLOAD_DESTINATION,
                                   'payload_charlie')
        print destination
        copy_file(package_path, destination)

        with open ( destination + "/" + "package_metadata.txt", "w") as fh:
            fh.write("CHARLIE_PACKAGE_NAME=" + package_name)

        settings = \
            {
            u'http://rmit.edu.au/schemas/system':
                {
                    u'random_numbers': 'file://127.0.0.1/randomnums.txt',
                    #u'metadata_builder': 'chiminey.mytardis.metadata.MetadataBuilder',
                },
        }
        return { 'settings': settings}

    def get_ui_schema_namespace(self):
        schemas = [
                django_settings.INPUT_FIELDS['cloud'],
                django_settings.INPUT_FIELDS['input_location'],
                django_settings.INPUT_FIELDS['output_location'],
                django_settings.INPUT_FIELDS['charlie'],
                #django_settings.INPUT_FIELDS['mytardis'],
                ]
        return schemas

#TODO backward compatability issue
    def get_domain_specific_schemas(self):

        schema_data =  [u'Charlie Smart Connector',
             {
                 u'internal_sweep_map': {'type': models.ParameterName.STRING, 'subtype': 'jsondict',
                                'description': 'Payload parameter sweep', 'ranking': 60, 'initial': '{}',
                                'help_text': 'Dictionary of values to sweep over, e.g {"var1":[3,7],"var2":[1,2]} would result in 4 Jobs:[3,1][3,2][7,1][7,2](JSON Dictionary)'},

             }
            ]
        #}
        return schema_data

    def get_updated_sweep_params(self, subdirective):
        package = "chiminey.corestages.sweep.HRMCSweep"
        settings = {
            u'http://rmit.edu.au/schemas/stages/sweep':
            {
                u'template_name': 'HRMC.inp',
                u'directive': subdirective.name

            },
            # FIXME: move random_numbers into system schema
            u'http://rmit.edu.au/schemas/system':
            {
                u'random_numbers': 'file://127.0.0.1/randomnums.txt'
            },
            }
        return {'package': package, 'settings': settings}

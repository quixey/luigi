# Copyright (c) 2013 Quixey
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
import subprocess
import tempfile
import logging

from luigi.task import Task
from luigi.file import File as localTarget


logger = logging.getLogger('luigi-interface')


class PigTask(Task):
    def get_script(self):
        return ''

    def run(self):
        # Setup any parameters for the script
        pig_params = []
        for key, value in self.script_parameters().items():
            pig_params += ['-p', '%s=%s' % (key, value)]

        temp_stdout = tempfile.TemporaryFile()
        script = self.get_script()
        if not script:
            logging.warn('Terminating pig script as no source script was set')
            return

        logger.info('Running pig script %s with parameters %s' % (script, ', '.join(pig_params)))

        proc = subprocess.Popen(['pig', '-f', script] + pig_params, stdout=temp_stdout, stderr=subprocess.PIPE)

        # Track the output so we can get error messages
        error_message = None
        while True:
            if proc.poll() is not None:
                break
            err_line = proc.stderr.readline()
            if err_line.strip():
                logger.info(err_line.strip())
            if err_line.find('ERROR ') != -1:
                error_message = err_line

        if proc.returncode == 0:
            return

        # Try to fetch error logs if possible
        message = 'Pig job failed with error %s. ' % error_message

        raise Exception(message)

    def script_parameters(self):
        return {}

    def output(self):
        return localTarget('./output_files/%s' % self.task_id)

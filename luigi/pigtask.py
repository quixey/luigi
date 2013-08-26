import subprocess
import tempfile
import luigi
import logging
from luigi import File
from games_classifier import *

logger = logging.getLogger('luigi-interface')


class PigTask(luigi.Task):

    def get_script(self):
        return ''

    def run(self):
        # Setup any parameters for the script
        pig_params = []
        for param in self.script_parameters():
            pig_params += ['-param', param]

        temp_stdout = tempfile.TemporaryFile()
        proc = subprocess.Popen(['pig', '-f', self.get_script()] + pig_params, stdout=temp_stdout, stderr=subprocess.PIPE)

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

        self.output().open('w').close()

        if proc.returncode == 0:
            return

        # Try to fetch error logs if possible
        message = 'Pig job failed with error %s. ' % error_message

        raise Exception(message)

    def script_parameters(self):
        return {}

    def output(self):
        return luigi.LocalTarget('./output_files/%s' % self.task_id)

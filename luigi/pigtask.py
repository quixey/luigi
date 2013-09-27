import subprocess
import tempfile
from luigi.task import Task
from luigi.file import File as localTarget
import logging

logger = logging.getLogger('luigi-interface')


class PigTask(Task):

    def get_script(self):
        return ''

    def run(self):
        # Setup any parameters for the script
        pig_params = []
        for param in self.script_parameters():
            pig_params += ['-p', param]

        temp_stdout = tempfile.TemporaryFile()
        script = self.get_script()
        if not script:
            logging.warn('Terminating pig script as no source script was set')
            return

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

        self.output().open('w').close()

        if proc.returncode == 0:
            return

        # Try to fetch error logs if possible
        message = 'Pig job failed with error %s. ' % error_message

        raise Exception(message)

    def script_parameters(self):
        return {}

    def output(self):
        return localTarget('./output_files/%s' % self.task_id)

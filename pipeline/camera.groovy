import hudson.tasks.test.AbstractTestResultAction
import hudson.model.Actionable
import hudson.tasks.junit.CaseResult
import hudson.tasks.test.TestResult

def SERIAL = "0000"
def USB_N = "0"
def DEVICE = "SKKF"
def PRODUCT = "kingfisher"
// def NODES = "${params.nodes}"
def result_path = ""
def totalCount =0
def failedCount =0
def skippedCount =0
def passCount =0
def mailRecipient = ""
def description = "${params.DESCRIPTION}" + " " + "RELEASE"
def jobName = ""
def status = ""
def user = ""
def failedTestDescription = ""
currentBuild.setDescription(description)


def TESTING_TIME="${params.TESTING_TIME}"

timestamps {
node (nodes) {
        stage('Preparation') {
            currentBuild.description = "test description"
            deleteDir()
            }
          stage ("Getting VF_TAF build") {
                script {
                    sh "git clone ssh://denys.horovyi@vf.globallogic.com:29418/gl/vf_test_camera"
                }
            }
        stage('Install python venv') {

                   script {
                    sh '''#!/bin/bash
                    PATH=$WORKSPACE/venv/bin:/usr/local/bin:$PATH
                    if [ ! -d "$(ls "$WORKSPACE" | grep "venv")" ]; then
                    python3 -m venv venv
                    fi
                    source venv/bin/activate
                    echo 'export PYTHONPATH=$PYTHONPATH:.' >> venv/bin/activate
                    pip3 install --upgrade pip
                    pip3 install -r $WORKSPACE/vf_test_camera/requirements.txt
                    '''
                    }

        }

        stage('Camera stability testing') {
            environment {
                TESTS_ROOT_DIR = "$WORKSPACE"
                LOGS_DIR = "$WORKSPACE" + "/logs_dir"
                USB_N = "$USB_N"
                result_path = "$WORKSPACE" + "/result"
                ANDROID_SERIAL = "$SERIAL"
                PRODUCT = "$PRODUCT"
            }

                script {

                        sh '''#!/bin/bash
                          . venv/bin/activate
                          python3 -m pytest -v -s $WORKSPACE/vf_test_camera/tests/camera/test_camera.py'''

            }
        }
        stage('Logs gathering') {
//         junit 'result/**/*.xml'
        archiveArtifacts artifacts: 'logs_dir/*'
            }
    }
}



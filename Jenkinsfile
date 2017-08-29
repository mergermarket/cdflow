// configuration
def slavePrefix = "mmg"
def cdflow_commit_sha

// pipeline definition
try {
    unitTest(slavePrefix)
    acceptanceTest(slavePrefix)
}
catch (e) {
    currentBuild.result = 'FAILURE'
    notifySlack(currentBuild.result)
    throw e
}

def unitTest(slavePrefix) {
    stage ("Unit Test") {
        node ("${slavePrefix}dev") {

            cdflow_commit_sha = checkout scm
            sh "./test.sh"
        }
    }
}

def acceptanceTest(slavePrefix) {
    stage ("Acceptance Test") {
		build job: 'platform/cdflow-test-service.temp', parameters: [string(name: 'CDFLOW_COMMIT_SHA', value: "${cdflow_commit_sha.GIT_COMMIT}")]
    }
}

// slack notifications
def notifySlack(String buildStatus = 'STARTED') {
    // Build status of null means success.
    buildStatus = buildStatus ?: 'SUCCESS'

    def color

    if (buildStatus == 'STARTED') {
        color = '#D4DADF'
    } else if (buildStatus == 'SUCCESS') {
        color = '#BDFFC3'
    } else if (buildStatus == 'UNSTABLE') {
        color = '#FFFE89'
    } else {
        color = '#FF9FA1'
    }

    def msg = "${buildStatus}: `${env.JOB_NAME}` #${env.BUILD_NUMBER}:\n${env.BUILD_URL}"
    slackSend(color: color, message: msg, channel: '#platform-team-alerts', token: fetch_credential('slack-r2d2'))
}

def fetch_credential(name) {
  def v;
  withCredentials([[$class: 'StringBinding', credentialsId: name, variable: 'CREDENTIAL']]) {
      v = env.CREDENTIAL;
  }
  return v
}

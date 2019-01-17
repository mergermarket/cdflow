// vim: filetype=groovy

// configuration
def cdflow_commit_sha
def githubCredentialsId = "github-credentials"

// pipeline definition
try {
    unitTest()
    acceptanceTest()
    publish(githubCredentialsId)
}
catch (e) {
    currentBuild.result = 'FAILURE'
    notifySlack(currentBuild.result)
    throw e
}

def unitTest() {
    stage ("Unit Test") {
        node ("swarm2") {
            cdflow_commit_sha = checkout scm
            currentVersion = sh(returnStdout: true, script: 'git describe --abbrev=0 --tags').trim().toInteger()
            remote = sh(returnStdout: true, script: "git config remote.origin.url").trim()
            commit = sh(returnStdout: true, script: "git rev-parse HEAD").trim()
            nextVersion = currentVersion + 1

            sh "./test.sh"
        }
    }
}

def acceptanceTest() {
    stage ("Acceptance Test") {
        parallel(
          cdflow_test_service_classic_metadata_handling: {
            build job: 'platform/cdflow-test-service-classic-metadata-handling', parameters: [string(name: 'CDFLOW_COMMIT_SHA', value: "${cdflow_commit_sha.GIT_COMMIT}")]
          },
          cdflow_test_service: {
            build job: 'platform/cdflow-test-service', parameters: [string(name: 'CDFLOW_COMMIT_SHA', value: "${cdflow_commit_sha.GIT_COMMIT}")]
          },
          cdflow_test_infrastructure: {
            build job: 'platform/cdflow-test-infrastructure', parameters: [string(name: 'CDFLOW_COMMIT_SHA', value: "${cdflow_commit_sha.GIT_COMMIT}")]
          }
        )
    }
}

def publish(githubCredentialsId) {
    stage("Publish Release") {
        node ("swarm2") {
            withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: githubCredentialsId, usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD']]) {
                git url: remote, commitId: commit, credentialsId: githubCredentialsId
                def author = sh(returnStdout: true, script: "git --no-pager show -s --format='%an' ${commit}").trim()
                def email = sh(returnStdout: true, script: "git --no-pager show -s --format='%ae' ${commit}").trim()
                sh """
                    git config user.name '${author}'
                    git config user.email '${email}'
                    git tag -a '${nextVersion}' -m 'Version ${nextVersion}'
                    git push 'https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/mergermarket/cdflow' --tags
                """
            }

            sh "./release.sh --repo_name mergermarket/cdflow --version ${nextVersion} --asset_path ./dist/cdflow-Linux-x86_64"
        }
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

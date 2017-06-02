// configuration
def slavePrefix = "mmg"

// pipeline definition
test(slavePrefix)

def test(slavePrefix) {
    stage ("Test") {
        node ("${slavePrefix}dev") {

            checkout scm
            sh "./test.sh"
        }
    }
}

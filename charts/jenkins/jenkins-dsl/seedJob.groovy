// seedJob.groovy

def repos = evaluate(new File('/var/jenkins_home/dsl/repos.groovy'))

repos.each { repo ->
    def repoName = repo.name
    def owner = repo.owner
    def jobNamePrefix = "${owner}-${repoName}"
    def gitUrl = "git@github.com:${owner}/${repoName}.git"

    def checkoutDir = "/tmp/${repoName}"
    println "Cloning repo ${gitUrl}..."

    def result = "git clone ${gitUrl} ${checkoutDir}".execute().waitFor()
    if (result != 0) {
        println "ERROR: Failed to clone ${gitUrl}"
        return
    }

    def dslPath = new File("${checkoutDir}/buildScripts/jenkins")
    if (!dslPath.exists()) {
        println "ERROR: Missing buildScripts/jenkins folder in ${repoName}"
        return
    }

    def dslScripts = ["${dslPath}/pull-request.groovy", "${dslPath}/release.groovy"]
    dslScripts.each { path ->
        println "Running DSL: ${path}"
        jobDsl targets: path, removeAction: 'IGNORE', ignoreMissingFiles: false
    }
}
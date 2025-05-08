def repos = [
    [ name: 'netgod-terraform', sshUrl: 'git@github.com:yudapinhas/netgod-terraform.git' ]
]

repos.each { repo ->
    pipelineJob("${repo.name}-pull-request") {
        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            url(repo.sshUrl)
                            credentials('github-ssh-key')
                        }
                        branches('*/master')
                    }
                }
                scriptPath('buildScripts/jenkins/pipelines/pull_request.groovy')
            }
        }
    }

    pipelineJob("${repo.name}-release") {
        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            url(repo.sshUrl)
                            credentials('github-ssh-key')
                        }
                        branches('*/master')
                    }
                }
                scriptPath('buildScripts/jenkins/pipelines/release.groovy')
            }
        }
    }
}
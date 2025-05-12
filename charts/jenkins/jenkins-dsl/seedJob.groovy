def repos = evaluate(new File("${JENKINS_HOME}/dsl/repos.groovy"))

repos.each { repo ->

  pipelineJob("${repo.name}-pull-request") {
    description("Runs on PR open or when someone comments 'retest this please' on ${repo.name}")
    triggers {
      githubPullRequest {
        useGitHubHooks()
        triggerPhrase('retest this please')
        onlyTriggerPhrase(true)
        permitAll(true)
        admins(['yudapinhas'])
        whiteListTargetBranches(['master'])
      }
    }
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
    description("Runs on push to master for ${repo.name}")
    triggers {
      githubPush()
    }
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
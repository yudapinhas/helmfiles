def repos = evaluate(new File("${JENKINS_HOME}/dsl/repos.groovy"))

repos.each { repo ->

  pipelineJob("${repo.name}-pull-request") {
    displayName("${repo.name}-pull-request")
    description("Pull Request CI for ${repo.name}")

    properties {
      githubProjectUrl("https://github.com/${repo.org}/${repo.name}")
    }

    definition {
      cpsScm {
        scm {
          git {
            remote {
              url(repo.sshUrl)
              credentials('github-ssh-key')
            }
          }
        }
        scriptPath('buildScripts/jenkins/pipelines/pull_request.groovy')
      }
    }

    triggers {
      githubPullRequest {
        useGitHubHooks() 
        permitAll()
        triggerPhrase('retest this please')
        admin("${repo.org}")
        extensions {
          commitStatus {
            context("CI - ${repo.name} PR")
            triggeredStatus("Triggered by PR or comment")
            startedStatus("Running CI for PR…")
            completedStatus("SUCCESS", "Build succeeded")
            completedStatus("FAILURE", "Build failed")
          }
        }
      }
    }
  }

  pipelineJob("${repo.name}-release") {
    displayName("${repo.name}-release")
    description("Runs on push to master for ${repo.name}")

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
    triggers {
      githubPush()
    }
  }
}
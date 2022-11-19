import static Constants.*

class Constants {
    static final GOOGLE_PROJECT_ID = "ai-dev-dev-yo9m"
    static final GOOGLE_REPOSITORIES = ['us.gcr.io', 'eu.gcr.io', 'asia.gcr.io']
}

def pullImages() {
    final repo = GOOGLE_REPOSITORIES[0]

    withCredentials([file(credentialsId: 'gcr.json', variable: 'GCR_KEY')]) {
        sh "cat ${GCR_KEY} | docker login -u _json_key --password-stdin https://${repo}"
        sh "docker pull ${repo}/${GOOGLE_PROJECT_ID}/workfit/alpine:3.10"
        sh "docker logout https://${repo}"
    }
}

def dockerBuildRelease(String tag) {
    docker.build(tag, "-f Dockerfile .")
}

def dockerPublish(String buildTag, String basePublishTag) {
    GOOGLE_REPOSITORIES.each { repo ->
        sh "docker tag ${buildTag} ${repo}/${GOOGLE_PROJECT_ID}/${basePublishTag}"
    }
    sh "docker tag ${buildTag} ${basePublishTag}"

    withCredentials([file(credentialsId: 'gcr.json', variable: 'GCR_KEY')]) {
        GOOGLE_REPOSITORIES.each { repo ->
            sh "cat ${GCR_KEY} | docker login -u _json_key --password-stdin https://${repo}"
            sh "docker push ${repo}/${GOOGLE_PROJECT_ID}/${basePublishTag}"
            sh "docker logout https://${repo}"
        }
    }
}

// Note that this assumes it's being called for develop or a release tag.
def makeDockerTag() {
    if (env.BRANCH_NAME == 'develop') {
        "${env.BRANCH_NAME}_${env.SHORT_SHA}_${new Date().format('yyyyMMddHHmmss')}"
    } else if (env.BRANCH_NAME == 'master') {
        "${env.BRANCH_NAME}_${env.SHORT_SHA}_${new Date().format('yyyyMMddHHmmss')}"
    } else {
        env.BRANCH_NAME
    }
}

def notifyTeams() {
    def msg = "Job: <a href=\"${JOB_URL}\">${JOB_NAME}</a> build: <a href=\"${BUILD_URL}\">${BUILD_ID}</a><br>Status: ${currentBuild.currentResult}"
    if (currentBuild.resultIsBetterOrEqualTo("SUCCESS")) {
        msg += "<br>Image: <code>workfit/asr-evaluator:${env.DOCKER_TAG}</code>"
    }

    sparkSend(
        credentialsId: 'voiceanotifications-bot',
        message: msg,
        messageType: 'html',
        spaceList: [[
            spaceId: 'd960bce0-5a07-11ed-8393-1d847438f9ac',
            spaceName: 'Jenkins asr-evaluation'
        ]]
    )
}

pipeline {
    agent { label 'docker' }

    environment {
        SHORT_SHA = sh(returnStdout: true, script: 'git rev-parse --short=8 HEAD').trim()

        BUILDING_TAG = "voicea-asr-evaluation:${env.SHORT_SHA}"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        // Setup environment variables for later publishing.
        // Mostly so they're available for post stages even on failure.
        stage('publish-init') {
            when {
                anyOf {
                    tag pattern: "\\A[0-9.]+\\z", comparator: "REGEXP"
                    branch 'develop'
                    branch 'master'
                }
            }

            steps {
                script {
                    env.DOCKER_TAG = makeDockerTag()
                }
            }
        }

        stage('build') {
            steps {
                script {
                    withCredentials([gitUsernamePassword(credentialsId: scm.userRemoteConfigs[0].credentialsId)]) {
                        // sh 'git pull'
                        // sh 'git submodule update --init --remote'
                        sh 'ls -l'
                        sh 'ls -l common-flow'
                    }
                }
                pullImages()
                dockerBuildRelease(env.BUILDING_TAG)
            }
        }

        stage('publish') {
            when { expression { env.DOCKER_TAG } }

            steps {
                dockerPublish(env.BUILDING_TAG, "workfit/asr-evaluator:${env.DOCKER_TAG}")

                script {
                    currentBuild.description = "Published docker tag: ${env.DOCKER_TAG}"
                }
            }
        }
    }

    post {
        always {
            script {
                notifyTeams()
            }
        }
    }
}

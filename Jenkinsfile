def image = ''

pipeline {
    agent any

    environment {
        REGISTRY = 'registry.spearmanwm.dev'
        IMAGE_NAME = 'downloader'
    }

    stages {
        stage('checkout') {
            steps {
                checkout scm
            }
        }

        stage('build docker image') {
            steps {
                script {
                    image = docker.build("${REGISTRY}/${IMAGE_NAME}:${BUILD_ID}")
                }
            }
        }

        stage('push to private registry') {
            steps {
                script {
                  docker.withRegistry("https://${REGISTRY}") {
                        image.push()
                        image.push('prod')
                    }
                }
            }
        }
    }
}
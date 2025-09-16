def dockerImage
pipeline {
    agent any

    environment {
        REGISTRY = 'registry.spearmanwm.dev'
        IMAGE_NAME = 'downloader'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        IMAGE_FULL = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    }

    stages {
        stage('clone') {
            steps {
                git branch: 'main',
                     credentialsId: 'GitHubCredentials',
                        url: 'https://github.com/WilliamSpear1/Downloader.git'
            }
        }

        stage('build docker image') {
            steps {
                script {
                    dockerImage = docker.build("${IMAGE_FULL}")
                }
            }
        }

        stage('push to private registry') {
            steps {
                script {
                   docker.withRegistry("https://registry.spearmanwm.dev") {
                        dockerImage.push()
                    }
                }
            }
        }
    }
    post {
        always {
            script{
                cleanWs()
            }
        }
    }
}

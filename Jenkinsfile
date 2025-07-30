def dockerImage
pipeline {
    agent any

    environment {
        REGISTRY = 'registry.spearmanwm.dev'
        IMAGE_NAME = 'downloader'
        HOME = '${WORKSPACE}'
    }

    stages {
        stage('clone') {
            steps {
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GitHubCredentials', url: 'https://github.com/WilliamSpear1/UrlProcessor.git']])
            }
        }

        stage('build docker image') {
            steps {
                script {
                    dockerImage = docker.build("${REGISTRY}/${IMAGE_NAME}:latest")
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

pipeline {
    agent any

    environment {
        REGISTRY = 'registry.spearmanwm.dev'
        IMAGE_NAME = 'downloader'
    }

    stages {
        stage('checkout') {
            steps {
               checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GithubJenkins2', url: 'https://github.com/WilliamSpear1/Downloader.git']])
            }
        }

        stage('build docker image') {
            steps {
                script {
                    echo "Building Docker Image: ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}"
                    sh "docker build -t ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER} -t ${REGISTRY}/${IMAGE_NAME}:latest."
                }
            }
        }

        stage('push to private registry') {
            steps {
                script {
                   docker.withRegistry("https://${REGISTRY}") {
                        sh "docker push ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}"
                        sh "docker push ${REGISTRY}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }
    }
}
pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        SONAR_HOST_URL = 'http://10.3.25.142:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Installing Python dependencies'

                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running ACEest Pytest suite'

                sh '''
                    .venv/bin/python -m pytest -v
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube analysis and enforcing the quality gate'

                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        docker run --rm \
                          -e SONAR_HOST_URL="${SONAR_HOST_URL}" \
                          -e SONAR_TOKEN="${SONAR_TOKEN}" \
                          -v "$PWD:/usr/src" \
                          sonarsource/sonar-scanner-cli \
                          -Dsonar.projectKey=aceest-fitness-gym \
                          -Dsonar.projectName="ACEest Fitness & Gym" \
                          -Dsonar.sources=. \
                          -Dsonar.exclusions=.venv/**,**/__pycache__/**,screenshots/**,static/**,templates/** \
                          -Dsonar.qualitygate.wait=true
                    '''
                }
            }
        }

        stage('Code Inspection') {
            steps {
                echo 'Checking Python syntax'

                sh '''
                    .venv/bin/python -m compileall -q app.py tests
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building ACEest Docker image'

                sh '''
                    docker build -t aceest-fitness-gym:latest .
                '''
            }
        }

        stage('Docker Test') {
            steps {
                echo 'Running Pytest inside Docker'

                sh '''
                    docker run --rm aceest-fitness-gym:latest python -m pytest -v
                '''
            }
        }
    }

        stage('Deploy to Minikube') {
            steps {
                echo 'Deploying ACEest to Kubernetes'

                sh '''
                    kubectl apply -f k8s/deployment-v1.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/aceest-v1 --timeout=120s
                '''
            }
        }

    post {
        success {
            echo 'ACEest pipeline completed successfully!'
        }

        failure {
            echo 'ACEest pipeline failed!'
        }
    }
}

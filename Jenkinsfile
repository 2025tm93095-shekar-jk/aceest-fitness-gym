pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
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

    post {
        success {
            echo 'ACEest pipeline completed successfully!'
        }

        failure {
            echo 'ACEest pipeline failed!'
        }
    }
}

pipeline {
    agent any

    // Build trigger: poll the Git repo every minute (alternative: GitHub webhook)
    triggers {
        pollSCM('* * * * *')
    }

    environment {
        // CI enhancement: version every build with the Jenkins build number + short commit SHA
        GIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        VERSION   = "${BUILD_NUMBER}-${GIT_SHORT}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r app/requirements.txt
                '''
            }
        }

        // CI enhancement: automated unit tests run BEFORE the build/package stage
        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    cd app && python -m pytest -v --junitxml=../test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Build') {
            steps {
                sh './build.sh "${VERSION}"'
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'dist/*.tar.gz', fingerprint: true
            }
        }
    }

    post {
        success { echo "Build ${VERSION} succeeded" }
        failure { echo "Build ${VERSION} FAILED" }
    }
}

pipeline {

    agent any

    environment {
        DOCKER_IMAGE = 'docker.io/rajaaravindan2497/employeehub'
        MANIFEST     = 'K8s/Deployment.yaml'
    }

    stages {

        // ==================================================
        // 1. CHECKOUT
        // ==================================================

        stage('Checkout') {
            steps {

                checkout scm

                script {

                    env.COMMIT_SHA = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE = "${DOCKER_IMAGE}:${COMMIT_SHA}"

                    echo "======================================"
                    echo " EmployeeHub CI/CD Pipeline"
                    echo "======================================"
                    echo "Git Commit  : ${COMMIT_SHA}"
                    echo "Docker Image: ${IMAGE}"
                }
            }
        }


        // ==================================================
        // 2. DOCKER BUILD
        // ==================================================

        stage('Docker Build') {
            steps {

                echo "=== Building EmployeeHub ==="

                sh '''
                    set -e

                    docker build -t "$IMAGE" .
                '''

                echo "=== Docker build completed ==="
            }
        }


        // ==================================================
        // 3. DOCKER PUSH
        // ==================================================

        stage('Docker Push') {
            steps {

                echo "=== Logging into Docker Hub ==="

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "$DOCKERHUB_TOKEN" | docker login \
                            -u "$DOCKERHUB_USERNAME" \
                            --password-stdin

                        echo "=== Pushing EmployeeHub ==="

                        docker push "$IMAGE"

                        docker logout
                    '''
                }

                echo "=== Docker image pushed ==="
            }
        }


        // ==================================================
        // 4. UPDATE KUBERNETES MANIFEST
        // ==================================================

        stage('Update Kubernetes Manifest') {
            steps {

                echo "=== Updating Kubernetes manifest ==="

                sh '''
                    set -e

                    sed -i \
                        "s|image: docker.io/rajaaravindan2497/employeehub:.*|image: $IMAGE|" \
                        "$MANIFEST"

                    echo "=== Updated image ==="

                    grep "image:" "$MANIFEST"
                '''
            }
        }


        // ==================================================
        // 5. PUSH MANIFEST TO GITHUB
        // ==================================================

        stage('Push Manifest to GitHub') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-credentials',
                        usernameVariable: 'GITHUB_USERNAME',
                        passwordVariable: 'GITHUB_TOKEN'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "=== Configuring Git ==="

                        git config user.name "Jenkins"
                        git config user.email "jenkins@employeehub.local"

                        git add "$MANIFEST"

                        if git diff --cached --quiet; then

                            echo "=== No manifest changes detected ==="

                        else

                            git commit \
                                -m "Update Employeehub image to $COMMIT_SHA"

                            echo "=== Pushing manifest change to GitHub ==="

                            git remote set-url origin \
                                "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/rajaaravindan2497/Employeehub.git"

                            git push origin HEAD:main

                        fi
                    '''
                }
            }
        }
    }


    // ==================================================
    // PIPELINE RESULT
    // ==================================================

    post {

        success {

            echo "======================================"
            echo " EmployeeHub CI SUCCESS"
            echo "======================================"

            echo "Docker Image: ${IMAGE}"
            echo "Manifest    : ${MANIFEST}"
        }

        failure {

            echo "======================================"
            echo " EmployeeHub CI FAILED"
            echo "======================================"
        }

        always {

            echo "Pipeline finished."
        }
    }
}
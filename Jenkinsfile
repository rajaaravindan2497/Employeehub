pipeline {

    agent any

   environment {
    EMPLOYEE_IMAGE = 'docker.io/rajaaravindan2497/employeehub'
    ADMIN_IMAGE    = 'docker.io/rajaaravindan2497/employeehub-admin'

    EMPLOYEE_MANIFEST = 'K8s/Deployment.yaml'
    ADMIN_MANIFEST    = 'K8s/Admin-Deployment.yaml'
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

                    env.EMPLOYEE_IMAGE_TAG = "${EMPLOYEE_IMAGE}:${COMMIT_SHA}"
                    env.ADMIN_IMAGE_TAG    = "${ADMIN_IMAGE}:${COMMIT_SHA}"

                    echo "======================================"
                    echo " EmployeeHub CI/CD Pipeline"
                    echo "======================================"
                    echo "Git Commit  : ${COMMIT_SHA}"
                    echo "Docker Image: ${EMPLOYEE_IMAGE}"
                    echo "Docker Image: ${ADMIN_IMAGE}"
                }
            }
        }


        // ==================================================
        // 2. DOCKER BUILD
        // ==================================================

        stage('Docker Build') {
            steps {
                sh '''
                    set -e
                    echo "=== Building EmployeeHub ==="
                    docker build -t "$EMPLOYEE_IMAGE_TAG" .
                    
                    echo "Building EmployeeHub Admin..."
                    docker build -t "$ADMIN_IMAGE_TAG" ./Admin
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

                        echo "=== Pushing EmployeeHub and EmployeeHub-admin ==="

                        docker push "$EMPLOYEE_IMAGE_TAG"
                        docker push "$ADMIN_IMAGE_TAG"

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
                sh '''
                    set -e

                    echo "Updating EmployeeHub image..."
                    sed -i \
                        "s|image: docker.io/rajaaravindan2497/employeehub:.*|image: $EMPLOYEE_IMAGE_TAG|" \
                        "$EMPLOYEE_MANIFEST"

                    echo "Updating Admin image..."
                    sed -i \
                        "s|image: docker.io/rajaaravindan2497/employeehub-admin:.*|image: $ADMIN_IMAGE_TAG|" \
                        "$ADMIN_MANIFEST"

                    echo "=== EmployeeHub ==="
                    grep "image:" "$EMPLOYEE_MANIFEST"

                    echo "=== Admin ==="
                    grep "image:" "$ADMIN_MANIFEST"
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

                        git add "$EMPLOYEE_MANIFEST" "$ADMIN_MANIFEST"

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
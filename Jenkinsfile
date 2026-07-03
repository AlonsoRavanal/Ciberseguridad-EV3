pipeline {
    agent any

    environment {
        APP_URL = 'http://app-evaluacion3:5000'
    }

    options {
        ansiColor('xterm')
    }

    stages {
        stage('Construccion (Docker)') {
            steps {
                echo 'Construyendo la imagen Docker de la aplicación...'
                sh '''
                    docker network create secureweb-network || true
                    docker build -t ciberseguridad-evaluacion3:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Instalar Dependencias') {
            steps {
                echo 'Instalando las librerías del proyecto y herramientas de prueba...'
                sh 'pip3 install -r requirements.txt --break-system-packages'
                sh 'pip3 install bandit safety pytest --break-system-packages'
            }
        }

        stage('Pruebas Unitarias') {
            steps {
                echo 'Ejecutando pruebas unitarias con Pytest...'
                sh 'pytest --junitxml=results.xml || true'
                junit allowEmptyResults: true, testResults: 'results.xml'
            }
        }

        stage('Pruebas SAST (Código)') {
            steps {
                echo 'Ejecutando escaneo de seguridad en el código con Bandit...'
                sh '/var/jenkins_home/.local/bin/bandit -r . -f txt -o reporte-bandit.txt || true'
                sh 'cat reporte-bandit.txt'
            }
        }

        stage('Pruebas SCA (Dependencias)') {
            steps {
                echo 'Ejecutando análisis de composición de software (SCA) con Safety...'
                sh '/var/jenkins_home/.local/bin/safety check -r requirements.txt > reporte-sca.txt || true'
                sh 'cat reporte-sca.txt'
            }
        }

        stage('Despliegue') {
            steps {
                echo 'Desplegando la aplicación en contenedor Docker...'
                sh '''
                    docker rm -f app-evaluacion3 || true
                    docker run -d \
                        --name app-evaluacion3 \
                        --network secureweb-network \
                        -p 5000:5000 \
                        ciberseguridad-evaluacion3:${BUILD_NUMBER}

                    sleep 5

                    docker run --rm \
                        --network secureweb-network \
                        curlimages/curl:latest \
                        -sf http://app-evaluacion3:5000 || echo "La aplicación no responde"
                '''
            }
         }
    }

    post {
        always {
            archiveArtifacts(
                artifacts: 'results.xml, reporte-bandit.txt, reporte-sca.txt',
                allowEmptyArchive: true
            )
        }
    }
} 
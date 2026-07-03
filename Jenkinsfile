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

        stage('Pruebas DAST (OWASP ZAP)') {
            steps {
                echo 'Ejecutando escaneo dinámico de seguridad con OWASP ZAP...'
                sh """
                    docker volume rm zap-report-vol 2>/dev/null || true
                    docker volume create zap-report-vol

                    docker run --rm \
                        -v zap-report-vol:/zap/wrk \
                        alpine sh -c 'chmod 777 /zap/wrk'

                    echo "=== Verificando que la aplicacion responda antes del escaneo ==="
                    docker run --rm \
                        --network secureweb-network \
                        curlimages/curl:latest \
                        -sf ${APP_URL} || echo "La aplicacion no responde"

                    echo "=== Ejecutando OWASP ZAP Baseline Scan ==="
                    docker run --rm \
                        -u root \
                        --network secureweb-network \
                        -v zap-report-vol:/zap/wrk/:rw \
                        ghcr.io/zaproxy/zaproxy:stable \
                            zap-baseline.py \
                                -t ${APP_URL} \
                                -r reporte-zap.html \
                                -J reporte-zap.json \
                                --auto || true

                    rm -rf \${WORKSPACE}/zap-reports
                    mkdir -p \${WORKSPACE}/zap-reports

                    docker rm -f zap-copy 2>/dev/null || true
                    docker create --name zap-copy -v zap-report-vol:/report alpine
                    docker cp zap-copy:/report/. \${WORKSPACE}/zap-reports/ || true
                    docker rm zap-copy || true

                    chmod 644 \${WORKSPACE}/zap-reports/* 2>/dev/null || true

                    echo "=== Contenido de zap-reports ==="
                    ls -la \${WORKSPACE}/zap-reports/ || true
                """

                publishHTML(target: [
                    allowMissing : true,
                    alwaysLinkToLastBuild : true,
                    keepAll : true,
                    reportDir : "zap-reports",
                    reportFiles : 'reporte-zap.html',
                    reportName : 'OWASP ZAP Report'
                ])
            }
        }
    }
    
    post {
        always {
            sh '''
                cp ${WORKSPACE}/zap-reports/reporte-zap.html ${WORKSPACE}/ 2>/dev/null || true
                cp ${WORKSPACE}/zap-reports/reporte-zap.json ${WORKSPACE}/ 2>/dev/null || true
            '''

            archiveArtifacts(
                artifacts: 'results.xml, reporte-bandit.txt, reporte-sca.txt, reporte-zap.html, reporte-zap.json',
                allowEmptyArchive: true
            )

            sh 'docker rm -f app-evaluacion3 || true'
        }
    }
}
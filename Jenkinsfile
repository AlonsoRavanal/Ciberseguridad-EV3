pipeline {
    agent any

    options {
        ansiColor('xterm')
    }
    
    stages {
        stage('Construccion') {
            steps {
                echo 'Construyendo la aplicacion vulnerable...'
            }
        }

        stage('Instalar Dependencias') {
            steps {
                echo 'Instalando las librerías del proyecto y herramientas de prueba...'
                sh 'pip3 install -r requirements.txt --break-system-packages'
                sh 'pip3 install bandit --break-system-packages'
                sh 'pip3 install safety --break-system-packages'
                sh 'pip3 install pytest --break-system-packages'
            }
        }

        stage('Pruebas Unitarias') {
            steps {
                echo 'Ejecutando pruebas unitarias con Pytest...'
                sh '/var/jenkins_home/.local/bin/pytest --junitxml=results.xml || true'
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
                echo 'Desplegando aplicacion en entorno de prueba...'
            }
        }
    }
}
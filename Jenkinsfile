pipeline {
    agent any

    stages {
        stage('Construccion') {
            steps {
                echo 'Construyendo la aplicacion vulnerable...'
            }
        }

        stage('Pruebas SAST (Código)') {
            steps {
                echo 'Ejecutando escaneo de seguridad en el código con Bandit...'
                sh 'pip3 install bandit'
                sh 'bandit -r . -f txt -o reporte-bandit.txt || true'
                sh 'cat reporte-bandit.txt'
            }
        }

        stage('Pruebas SCA (Dependencias)') {
            steps {
                echo 'Ejecutando análisis de composición de software (SCA) con Safety...'
                sh 'pip3 install -r requirements.txt'
                sh 'pip3 install safety'
                sh 'safety check -r requirements.txt > reporte-sca.txt || true'
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
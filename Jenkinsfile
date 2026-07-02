pipeline {
    agent any

    stages {
        stage('Construccion') {
            steps {
                echo 'Construyendo la aplicacion vulnerable...'
                sh 'python3 -m venv venv'
            }
        }

        stage('Pruebas SAST (Código)') {
            steps {
                echo 'Ejecutando escaneo de seguridad en el código con Bandit...'
                sh '''
                    . venv/bin/activate
                    pip install bandit
                    bandit -r . -f txt -o reporte-bandit.txt || true
                    cat reporte-bandit.txt
                '''
            }
        }

        stage('Pruebas SCA (Dependencias)') {
            steps {
                echo 'Ejecutando análisis de composición de software (SCA) con Safety...'
                sh '''
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pip install safety
                    safety check -r requirements.txt > reporte-sca.txt || true
                    cat reporte-sca.txt
                '''
            }
        }

        stage('Despliegue') {
            steps {
                echo 'Desplegando aplicacion en entorno de prueba...'
            }
        }
    }
}
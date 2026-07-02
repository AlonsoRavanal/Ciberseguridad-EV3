pipeline {
    agent any

    stages {
        stage('Construccion') {
            steps {
                echo 'Construyendo la aplicacion vulnerable...'
            }
        }

        stage('Pruebas') {
            steps {
                echo 'Ejecutando pruebas basicas...'
            }
        }

        stage('Despliegue') {
            steps {
                echo 'Desplegando aplicacion en entorno de prueba...'
            }
        }
    }
}

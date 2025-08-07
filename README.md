# OrderFlow
OrderFlow is a lightweight and reliable system for managing product orders, ensuring data integrity and consistent stock control in concurrent environments.







#Case 2

Integração com Sistema Legado
VPN ou AWS Direct Connect continua para integração segura.

Criação de serviços de integração isolados em ECS que acessam o sistema legado e publicam dados em S3 ou em filas (por exemplo, SQS).

Orquestração e Execução de Microserviços
Amazon ECS (Fargate) com containers para microserviços modulares.

Cada serviço pode:

Consumir eventos de filas (SQS/SNS).

Consultar dados no S3 via Athena.

Expor APIs por meio do API Gateway ou Application Load Balancer.

Armazenamento e Consumo de Dados
Amazon S3 como data lake central.

Dados armazenados em formatos otimizados (Parquet/ORC).

AWS Glue para catalogação.

Amazon Athena para consulta serverless de dados.

Observabilidade e Monitoramento
Datadog para:

Logs estruturados de todos os containers ECS.

Tracing distribuído entre serviços.

Dashboards de performance e alertas automáticos.

Integração com AWS CloudWatch para métricas nativas.

# OrderFlow
OrderFlow is a lightweight and reliable system for managing product orders, ensuring data integrity and consistent stock control in concurrent environments.


#Case 2
🏦 Sistema Legado (On-Premises)
Comunicação via VPN ou Direct Connect.

☁️ Nuvem AWS - Arquitetura Baseada em Microserviços
🔹 1. Camada de Integração
Serviço em Amazon ECS (Fargate) que:

Recebe/extrai dados do sistema legado via VPN.

Publica mensagens em Amazon SQS/SNS ou envia arquivos para o Amazon S3.

🔹 2. Armazenamento de Dados
Amazon S3 como data lake central.

Dados estruturados (ex: JSON, Parquet).

Controlado via AWS Glue (catálogo de dados e schema registry).

Dados versionados e replicados (para backup e recuperação).

🔹 3. Consumo e Processamento
Microserviços em Amazon ECS (Fargate) que:

Processam eventos do SQS/SNS.

Consultam dados via Amazon Athena.

Geram relatórios, processamentos ou notificações.

🔹 4. Exposição de Serviços
APIs expostas via API Gateway ou ALB (Application Load Balancer) conectando-se aos containers ECS.

🔹 5. Observabilidade
Datadog com:

Agentes instalados nos containers ECS.


Integração com CloudWatch Logs, Metrics e Traces.

Dashboards, alertas e rastreamento distribuído.

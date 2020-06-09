FROM astronomerinc/ap-airflow:1.10.10-buster-onbuild
ENV VAULT__ROOT_TOKEN $VAULT__ROOT_TOKEN
ENV VAULT__URL $VAULT__URL
ENV AIRFLOW__SECRETS__BACKEND="airflow.contrib.secrets.hashicorp_vault.VaultBackend"
ENV AIRFLOW__SECRETS__BACKEND_KWARGS='{"url":$VAULT__URL,"token": $VAULT__ROOT_TOKEN,"connections_path": "connections","kv_engine_version":1}'